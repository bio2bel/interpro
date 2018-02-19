# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel.resources.arty import get_today_arty_namespace
from pybel.resources.definitions import write_namespace
from pybel.resources.deploy import deploy_namespace
from .constants import MODULE_NAME
from .models import Base, Entry, Protein, Type
from .parser.entries import get_interpro_entries_data
from .parser.tree import parse_tree

log = logging.getLogger(__name__)

COLUMNS = ['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']


def _write_bel_namespace_helper(values, file):
    """Writes the InterPro entries namespace

    :param file file: A write-enabled file or file-like. Defaults to standard out
    :param values: The values to write
    """
    write_namespace(
        namespace_name='InterPro Protein Families',
        namespace_keyword=MODULE_NAME.upper(),
        namespace_domain=NAMESPACE_DOMAIN_GENE,
        author_name='Charles Tapley Hoyt',
        author_contact='charles.hoyt@scai.fraunhofer.de',
        author_copyright='Creative Commons by 4.0',
        citation_name='InterPro',
        values=values,
        functions='P',
        file=file
    )


class Manager(object):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param Optional[str] connection: SQLAlchemy connection string
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = get_connection(MODULE_NAME, connection=connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.session_maker)
        self.create_all()

    def create_all(self, check_first=True):
        """creates all tables from models in your database

        :param bool check_first: True or False check if tables already exists
        """
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine)

    @staticmethod
    def ensure(connection=None):
        """Checks and allows for a Manager to be passed to the function.

        :param connection: can be either a already build manager or a connection string to build a manager with.
        """
        if connection is None or isinstance(connection, str):
            return Manager(connection=connection)

        if isinstance(connection, Manager):
            return connection

        raise TypeError

    def count_interpros(self):
        """Counts the number of InterPro entries in the database

        :rtype: int
        """
        return self.session.query(Entry).count()

    def count_proteins(self):
        """Counts the number of protein entries in the database

        :rtype: int
        """
        return self.session.query(Protein).count()

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(interpros=self.count_interpros(), proteins=self.count_proteins())

    def populate_entries(self, url=None):
        """Populates the database

        :param Optional[str] url: An optional URL for the InterPro entries' data
        """
        df = get_interpro_entries_data(url=url)

        id_type = {}

        for _, interpro_id, entry_type, name in tqdm(df[COLUMNS].itertuples(), desc='Entries', total=len(df.index)):

            family_type = id_type.get(entry_type)

            if family_type is None:
                family_type = id_type[entry_type] = Type(name=entry_type)
                self.session.add(family_type)

            entry = Entry(
                interpro_id=interpro_id,
                type=family_type,
                name=name
            )

            self.session.add(entry)

        log.info('committing entries')
        self.session.commit()

    def populate_tree(self, path=None, force_download=False):
        """Populates the hierarchical relationships of the InterPro entries

        :param Optional[str] path:
        :param bool force_download:
        """
        graph = parse_tree(path=path, force_download=force_download)

        name_model = {
            model.name: model
            for model in self.session.query(Entry).all()
        }

        for parent, child in tqdm(graph.edges_iter(), desc='Building Tree', total=graph.number_of_edges()):
            name_model[child].parent = name_model[parent]

        log.info('committing tree')
        self.session.commit()

    def populate_membership(self):
        raise NotImplementedError

    def populate(self, family_entries_url=None, tree_url=None):
        self.populate_entries(url=family_entries_url)
        self.populate_tree(path=tree_url)

    def get_family_by_name(self, name):
        """Gets an InterPro family by name, if exists.

        :param str name: The name to search
        :rtype: Optional[Family]
        """
        return self.session.query(Entry).filter(Entry.name == name).one_or_none()

    def enrich_proteins(self, graph):
        """Finds UniProt entries and annotates their InterPro entries

        :param pybel.BELGraph graph: A BEL graph
        """
        raise NotImplementedError

    def enrich_interpros(self, graph):
        """Finds InterPro entries and annotates their proteins

        :param pybel.BELGraph graph: A BEL graph
        """
        raise NotImplementedError

    def write_bel_namespace(self, file):
        values = [name for name, in self.session.query(Entry.name).all()]
        _write_bel_namespace_helper(values, file)

    def deploy_bel_namespace(self):
        """Creates and deploys the Gene Names Namespace

        :rtype: Optional[str]
        """
        file_name = get_today_arty_namespace('interpro')

        with open(file_name, 'w') as file:
            self.write_bel_namespace(file)

        return deploy_namespace(file_name, module_name='interpro')

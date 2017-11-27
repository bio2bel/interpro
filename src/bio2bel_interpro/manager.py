# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from tqdm import tqdm

from bio2bel.utils import get_connection
from .constants import MODULE_NAME
from .models import Base, Family, Type
from .tree import parse_tree
from .utils import get_family_entries_data

log = logging.getLogger(__name__)

COLUMNS = ['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']

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

    def populate_entries(self, family_entries_url=None):
        """Populates the database

        :param str family_entries_url:
        """
        df = get_family_entries_data(url=family_entries_url)

        id_type = {}

        for _, interpro_id, entry_type, name in tqdm(df[COLUMNS].itertuples(), desc='Entries', total=len(df.index)):

            family_type = id_type.get(entry_type)

            if family_type is None:
                family_type = Type(name=entry_type)
                id_type[entry_type] = family_type
                self.session.add(family_type)

            entry = Family(
                interpro_id=interpro_id,
                type=family_type,
                name=name
            )

            self.session.add(entry)

        self.session.commit()

    def populate_tree(self, path=None, force_download=False):
        graph = parse_tree(path=path, force_download=force_download)

        name_model = {
            model.name: model
            for model in self.session.query(Family).all()
        }

        for parent, child in tqdm(graph.edges_iter(), desc='Tree', total=graph.number_of_edges()):
            name_model[child].parent = name_model[parent]

        self.session.commit()

    def populate(self, path=None, family_entries_url=None):
        self.populate_entries(family_entries_url=family_entries_url)
        self.populate_tree(path=path)

    def populate_protein_membership(self):
        raise NotImplementedError

    def get_family_by_name(self, name):
        """Gets an InterPro family by name, if exists.

        :param str name: The name to search
        :rtype: Optional[Family]
        """
        return self.session.query(Family).filter(Family.name == name).one_or_none()

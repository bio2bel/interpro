# -*- coding: utf-8 -*-

import logging

from tqdm import tqdm

from bio2bel.abstractmanager import AbstractManager
from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel.resources.definitions import write_namespace
from .constants import MODULE_NAME
from .models import Base, Entry, Protein, Type, entry_protein
from .parser.entries import get_interpro_entries_df
from .parser.tree import get_interpro_tree

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


class Manager(AbstractManager):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    module_name = MODULE_NAME
    flask_admin_models = [Entry, Protein, Type]

    @property
    def _base(self):
        return Base

    def is_populated(self):
        """Check if the database is already populated"""
        return 0 < self.count_interpros()

    def count_interpros(self):
        """Counts the number of InterPro entries in the database

        :rtype: int
        """
        return self._count_model(Entry)

    def count_interpro_proteins(self):
        """Counts the number of protein-interpro associations

        :rtype: int
        """
        return self._count_model(entry_protein)

    def count_proteins(self):
        """Counts the number of protein entries in the database

        :rtype: int
        """
        return self._count_model(Protein)

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(
            interpros=self.count_interpros(),
            interpro_proteins=self.count_interpro_proteins(),
            proteins=self.count_proteins()
        )

    def populate_entries(self, url=None):
        """Populates the database

        :param Optional[str] url: An optional URL for the InterPro entries' data
        """
        df = get_interpro_entries_df(url=url)

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
        graph = get_interpro_tree(path=path, force_download=force_download)

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
        """Populate the database.

        :param family_entries_url:
        :param tree_url:
        :return:
        """
        self.populate_entries(url=family_entries_url)
        self.populate_tree(path=tree_url)

    def get_family_by_name(self, name):
        """Gets an InterPro family by name, if exists.

        :param str name: The name to search
        :rtype: Optional[Family]
        """
        return self.session.query(Entry).filter(Entry.name == name).one_or_none()

    def enrich_proteins(self, graph):
        """Find UniProt entries and annotates their InterPro entries.

        :param pybel.BELGraph graph: A BEL graph
        """
        raise NotImplementedError

    def enrich_interpros(self, graph):
        """Find InterPro entries and annotates their proteins.

        :param pybel.BELGraph graph: A BEL graph
        """
        raise NotImplementedError

    def write_bel_namespace(self, file):
        """Write an InterPro BEL namespace file."""
        values = [name for name, in self.session.query(Entry.name).all()]
        _write_bel_namespace_helper(values, file)

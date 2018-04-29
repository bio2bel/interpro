# -*- coding: utf-8 -*-

import logging
import time
from typing import Optional

from bio2bel.abstractmanager import AbstractManager
from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel.resources.definitions import write_namespace
from tqdm import tqdm

from .constants import MODULE_NAME
from .models import Base, Entry, GoTerm, Protein, Type, entry_protein
from .parser.entries import get_interpro_entries_df
from .parser.interpro_to_go import get_go_mappings
from .parser.proteins import get_proteins_df
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
    flask_admin_models = [Entry, Protein, Type, GoTerm]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.types = {}
        self.interpros = {}
        self.go_terms = {}

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

    def count_go_terms(self):
        return self._count_model(GoTerm)

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(
            interpros=self.count_interpros(),
            interpro_proteins=self.count_interpro_proteins(),
            proteins=self.count_proteins(),
            go_terms=self.count_go_terms()
        )

    def get_type_by_name(self, name) -> Optional[Type]:
        return self.session.query(Type).filter(Type.name == name).one_or_none()

    def get_interpro_by_interpro_id(self, interpro_id) -> Optional[Entry]:
        return self.session.query(Entry).filter(Entry.interpro_id == interpro_id).one_or_none()

    def _populate_entries(self, url=None):
        """Populates the database

        :param Optional[str] url: An optional URL for the InterPro entries' data
        """
        df = get_interpro_entries_df(url=url)

        for _, interpro_id, entry_type, name in tqdm(df[COLUMNS].itertuples(), desc='Entries', total=len(df.index)):

            family_type = self.types.get(entry_type)

            if family_type is None:
                family_type = self.types[entry_type] = Type(name=entry_type)
                self.session.add(family_type)

            entry = self.interpros[interpro_id] = Entry(
                interpro_id=interpro_id,
                type=family_type,
                name=name
            )

            self.session.add(entry)

        t = time.time()
        log.info('committing entries')
        self.session.commit()
        log.info('committed entries in %.2f seconds', time.time() - t)

    def _populate_tree(self, path=None, force_download=False):
        """Populates the hierarchical relationships of the InterPro entries

        :param Optional[str] path:
        :param bool force_download:
        """
        graph = get_interpro_tree(path=path, force_download=force_download)

        for parent_name, child_name in tqdm(graph.edges(), desc='Building Tree', total=graph.number_of_edges()):
            child_id = graph.node[child_name]['interpro_id']
            parent_id = graph.node[parent_name]['interpro_id']

            child = self.interpros.get(child_id)
            parent = self.interpros.get(parent_id)

            if child is None:
                log.warning('missing %s/%s', child_id, child_name)
                continue

            if parent is None:
                log.warning('missing %s/%s', parent_id, parent_name)
                continue

            child.parent = parent

        t = time.time()
        log.info('committing tree')
        self.session.commit()
        log.info('committed tree in %.2f seconds', time.time() - t)

    def get_go_by_go_identifier(self, go_id) -> Optional[GoTerm]:
        return self.session.query(GoTerm).filter(GoTerm.go_id == go_id).one_or_none()

    def get_or_create_go_term(self, go_id, name=None):

        go = self.go_terms.get(go_id)
        if go is not None:
            return go

        go = self.get_go_by_go_identifier(go_id)
        if go is not None:
            self.go_terms[go_id] = go
            return go

        go = self.go_terms[go_id] = GoTerm(go_id=go_id, name=name)
        self.session.add(go)
        return go

    def _populate_go(self, path=None):
        """Populate the InterPro-GO mappings.

        Assumes entries are populated.
        """
        go_mappings = get_go_mappings(path=path)

        for interpro_id, go_id, go_name in tqdm(go_mappings, desc='Mappings to GO'):
            interpro = self.interpros.get(interpro_id)

            if interpro is None:
                log.warning('could not find %s', interpro_id)
                continue

            interpro.go_terms.append(self.get_or_create_go_term(go_id=go_id, name=go_name))

        t = time.time()
        log.info('committing go terms')
        self.session.commit()
        log.info('committed go terms in %.2f seconds', time.time() - t)

    def _populate_proteins(self, url=None):
        """Populate the InterPro-protein mappings."""
        df = get_proteins_df(url=url)

    def populate(self, family_entries_url=None, tree_url=None, go_mapping_path=None):
        """Populate the database.

        :param Optional[str] family_entries_url:
        :param Optional[str] tree_url:
        :param Optional[str] go_mapping_path:
        """
        self._populate_entries(url=family_entries_url)
        self._populate_tree(path=tree_url)
        self._populate_go(path=go_mapping_path)

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

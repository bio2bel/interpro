# -*- coding: utf-8 -*-

import logging
from typing import List, Optional

import time
from pybel import BELGraph
from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel.manager.models import NamespaceEntry
from pybel.resources.definitions import write_namespace
from tqdm import tqdm

from bio2bel.namespace_manager import NamespaceManagerMixin
from compath_utils import CompathManager
from .constants import CHUNKSIZE, MODULE_NAME
from .models import Annotation, Base, Entry, GoTerm, Protein, Type
from .parser.entries import get_interpro_entries_df
from .parser.interpro_to_go import get_go_mappings
from .parser.proteins import get_proteins_df
from .parser.tree import get_interpro_tree

log = logging.getLogger(__name__)


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


class Manager(CompathManager, NamespaceManagerMixin):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    module_name = MODULE_NAME
    namespace_model = Entry
    flask_admin_models = [Entry, Protein, Type, Annotation, GoTerm]

    pathway_model = Entry
    pathway_model_identifier_column = Entry.interpro_id
    protein_model = Protein

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.types = {}
        self.interpros = {}
        self.go_terms = {}

    @property
    def _base(self):
        return Base

    def is_populated(self) -> bool:
        """Check if the database is already populated"""
        return 0 < self.count_interpros()

    def count_interpros(self) -> int:
        """Counts the number of InterPro entries in the database

        :rtype: int
        """
        return self._count_model(Entry)

    def list_interpros(self) -> List[Entry]:
        return self._list_model(Entry)

    def count_annotations(self) -> int:
        """Counts the number of protein-interpro associations

        :rtype: int
        """
        return self._count_model(Annotation)

    def count_proteins(self) -> int:
        """Counts the number of protein entries in the database

        :rtype: int
        """
        return self._count_model(Protein)

    def list_proteins(self) -> List[Protein]:
        return self._list_model(Protein)

    def count_go_terms(self) -> int:
        return self._count_model(GoTerm)

    def summarize(self):
        """Returns a summary dictionary over the content of the database

        :rtype: dict[str,int]
        """
        return dict(
            interpros=self.count_interpros(),
            annotations=self.count_annotations(),
            proteins=self.count_proteins(),
            go_terms=self.count_go_terms()
        )

    def get_type_by_name(self, name) -> Optional[Type]:
        return self.session.query(Type).filter(Type.name == name).one_or_none()

    def get_interpro_by_interpro_id(self, interpro_id) -> Optional[Entry]:
        return self.session.query(Entry).filter(Entry.interpro_id == interpro_id).one_or_none()

    def _populate_entries(self, entry_url=None, tree_url=None, force_download=False):
        """Populates the database

        :param Optional[str] entry_url: An optional URL for the InterPro entries' data
        :param Optional[str] tree_url:
        :param bool force_download:
        """
        interpro_count = self.count_interpros()
        if interpro_count > 0:
            log.info('proteins (%d) already populated', interpro_count)
            return

        df = get_interpro_entries_df(url=entry_url, force_download=force_download)

        for _, interpro_id, entry_type, name in tqdm(df.itertuples(), desc='Entries', total=len(df.index)):

            family_type = self.types.get(entry_type)

            if family_type is None:
                family_type = self.types[entry_type] = Type(name=entry_type)
                self.session.add(family_type)

            self.get_or_create_interpro(
                interpro_id=interpro_id,
                type=family_type,
                name=name,
            )

        t = time.time()
        log.info('committing entries')
        self.session.commit()
        log.info('committed entries in %.2f seconds', time.time() - t)

        graph = get_interpro_tree(path=tree_url, force_download=force_download)

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

    def get_or_create_interpro(self, interpro_id: str, **kwargs) -> Entry:
        interpro = self.interpros.get(interpro_id)
        if interpro is not None:
            return interpro

        interpro = self.get_interpro_by_interpro_id(interpro_id)
        if interpro is not None:
            self.interpros[interpro_id] = interpro
            return interpro

        interpro = self.interpros[interpro_id] = Entry(interpro_id=interpro_id, **kwargs)

        self.session.add(interpro)
        return interpro

    def get_or_create_go_term(self, go_id, name=None) -> GoTerm:
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
        go_count = self.count_go_terms()
        if go_count > 0:
            log.info('GO terms (%d) already populated', go_count)
            return

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

    def _populate_proteins(self, url=None, chunksize=None):
        """Populate the InterPro-protein mappings."""
        chunksize = chunksize or CHUNKSIZE

        df = get_proteins_df(url=url, chunksize=chunksize)

        log.info('precaching interpros')
        interpros = {
            interpro.interpro_id: interpro
            for interpro in self.list_interpros()
        }

        log.info('cached %d interpros', len(interpros))

        log.info('building protein models')

        interpro, protein = None, None
        current_uniprot_id = None

        # Assumes ordered by uniprot_id

        for chunk in tqdm(df, desc='Protein mapping chunks of {}'.format(CHUNKSIZE)):
            for _, (uniprot_id, interpro_id, xref, start, end) in tqdm(chunk.iterrows(), total=CHUNKSIZE):
                if current_uniprot_id != uniprot_id:
                    protein = Protein(uniprot_id=uniprot_id)
                    current_uniprot_id = uniprot_id

                interpro = self.get_or_create_interpro(interpro_id)
                annotation = Annotation(
                    entry=interpro,
                    protein=protein,
                    xref=xref,
                    start=start,
                    end=end,
                )
                self.session.add(annotation)

            t = time.time()
            log.info('committing proteins from chunk')
            self.session.commit()
            log.info('committed proteins from chunk in %.2f seconds', time.time() - t)

    def populate(self, entries_url=None, tree_url=None, go_mapping_path=None, proteins_url=None):
        """Populate the database.

        :param Optional[str] entries_url:
        :param Optional[str] tree_url:
        :param Optional[str] go_mapping_path:
        :param Optional[str] proteins_url:
        """
        self._populate_entries(entry_url=entries_url, tree_url=tree_url)
        self._populate_go(path=go_mapping_path)
        self._populate_proteins(url=proteins_url)

    def get_interpro_by_name(self, name) -> Optional[Entry]:
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

    @staticmethod
    def _get_identifier(model):
        return model.interpro_id

    def _create_namespace_entry_from_model(self, model, namespace):
        return NamespaceEntry(encoding='P', name=model.name, identifier=model.interpro_id, namespace=namespace)

    def to_bel(self):
        graph = BELGraph()

        interpro_namespace = self.upload_bel_namespace()
        graph.namespace_url[interpro_namespace.keyword] = interpro_namespace.url

        for entry in self.list_interpros():
            entry_bel = entry.as_bel()

            for child in entry.children:
                graph.add_is_a(child.as_bel(), entry_bel)

            for annotation in entry.annotations:
                graph.add_is_a(annotation.protein.as_bel(), entry_bel)

            # for go_term in entry.go_terms:
            #    graph.add_qualified_edge(entry_bel, go_term.as_bel())

        return graph

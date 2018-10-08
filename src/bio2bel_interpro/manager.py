# -*- coding: utf-8 -*-

"""Manager for Bio2BEL InterPro."""

import logging
from typing import List, Mapping, Optional

import time
from flask_admin.contrib.sqla import ModelView
from tqdm import tqdm

from bio2bel.manager.bel_manager import BELManagerMixin
from bio2bel.manager.flask_manager import FlaskMixin
from bio2bel.manager.namespace_manager import BELNamespaceManagerMixin
from compath_utils import CompathManager
from pybel import BELGraph
from pybel.manager.models import Namespace, NamespaceEntry
from .constants import CHUNKSIZE, MODULE_NAME
from .models import Annotation, Base, Entry, GoTerm, Protein, Type
from .parser.entries import get_interpro_entries_df
from .parser.interpro_to_go import get_go_mappings
from .parser.proteins import get_proteins_chunks
from .parser.tree import get_interpro_tree

log = logging.getLogger(__name__)


class EntryView(ModelView):
    column_searchable_list = ['interpro_id']


class Manager(CompathManager, BELNamespaceManagerMixin, BELManagerMixin, FlaskMixin):
    """Manager for Bio2BEL InterPro."""

    module_name = MODULE_NAME
    namespace_model = Entry
    flask_admin_models = [(Entry, EntryView), Protein, Type, Annotation, GoTerm]

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
        """Check if the database is already populated."""
        return 0 < self.count_interpros()

    def count_interpros(self) -> int:
        """Count the number of InterPro entries in the database."""
        return self._count_model(Entry)

    def list_interpros(self) -> List[Entry]:
        """List the InterPro entries in the database."""
        return self._list_model(Entry)

    def count_annotations(self) -> int:
        """Count the number of protein-interpro associations."""
        return self._count_model(Annotation)

    def count_proteins(self) -> int:
        """Count the number of protein entries in the database."""
        return self._count_model(Protein)

    def list_proteins(self) -> List[Protein]:
        """List the proteins in the database."""
        return self._list_model(Protein)

    def count_go_terms(self) -> int:
        """Count the GO terms in the database."""
        return self._count_model(GoTerm)

    def summarize(self) -> Mapping[str, int]:
        """Summarize the database."""
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

    def get_go_by_go_identifier(self, go_id: str) -> Optional[GoTerm]:
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

    def get_or_create_go_term(self, go_id: str, name=None) -> GoTerm:
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

    def _populate_entries(self, entry_url: Optional[str] = None, tree_url: Optional[str] = None,
                          force_download: bool = False) -> None:
        """Populate the database."""
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
            child_id = graph.nodes[child_name]['interpro_id']
            parent_id = graph.nodes[parent_name]['interpro_id']

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

    def _populate_go(self, path: Optional[str] = None):
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

    def _populate_proteins(self, url: Optional[str] = None, chunksize: Optional[int] = None) -> None:
        """Populate the InterPro-protein mappings."""
        chunksize = chunksize or CHUNKSIZE

        log.info('precaching interpros')
        interpros = {
            interpro.interpro_id: interpro
            for interpro in self.list_interpros()
        }

        log.info('cached %d interpros', len(interpros))

        log.info('building protein models')

        cursor_uniprot_id, protein = None, None

        # Assumes ordered by uniprot_id

        missing = set()

        chunks = get_proteins_chunks(url=url, chunksize=chunksize)
        for chunk in tqdm(chunks, desc=f'Protein mapping chunks of {chunksize}'):
            for _, (uniprot_id, interpro_id, xref, start, end) in tqdm(chunk.iterrows(), total=chunksize):
                if uniprot_id != cursor_uniprot_id:  # means new type of entry
                    protein = Protein(uniprot_id=uniprot_id)
                    cursor_uniprot_id = uniprot_id

                interpro = interpros.get(interpro_id)
                if interpro is None:
                    missing.add(interpro_id)
                    continue

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

        for m in missing:
            log.warning('missing %s', m)

    def get_interpro_by_name(self, name: str) -> Optional[Entry]:
        """Gets an InterPro family by name, if exists."""
        return self.session.query(Entry).filter(Entry.name == name).one_or_none()

    def enrich_proteins(self, graph: BELGraph):
        """Find UniProt entries and annotates their InterPro entries."""
        raise NotImplementedError

    def enrich_interpros(self, graph: BELGraph):
        """Find InterPro entries and annotates their proteins."""
        raise NotImplementedError

    @staticmethod
    def _get_identifier(entry: Entry) -> str:
        return entry.interpro_id

    def _create_namespace_entry_from_model(self, entry: Entry, namespace: Namespace) -> NamespaceEntry:
        return NamespaceEntry(
            encoding='P',
            name=entry.name,
            identifier=entry.interpro_id,
            namespace=namespace,
        )

    def to_bel(self) -> BELGraph:
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

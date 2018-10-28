# -*- coding: utf-8 -*-

"""Test cases for Bio2BEL InterPro."""

from bio2bel.testing import AbstractTemporaryCacheClassMixin
from bio2bel_interpro import Manager
from tests.constants import TEST_ENTRIES_PATH, TEST_INTERPRO_GO_MAPPINGS_PATH, TEST_INTERPRO_PROTEIN_MAPPINGS_PATH, TEST_TREE_PATH


class TemporaryCacheClassMixin(AbstractTemporaryCacheClassMixin):
    """An implementation of :class:`bio2bel.testing.AbstractTemporaryCacheClassMixin` for Bio2BEL InterPro."""

    Manager = Manager

    @classmethod
    def populate(cls):
        cls.manager.populate(
            entries_url=TEST_ENTRIES_PATH,
            tree_url=TEST_TREE_PATH,
            go_mapping_path=TEST_INTERPRO_GO_MAPPINGS_PATH,
            proteins_url=TEST_INTERPRO_PROTEIN_MAPPINGS_PATH,
            populate_proteins=True,
        )

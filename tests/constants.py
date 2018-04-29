# -*- coding: utf-8 -*-

"""Testing constants, mocks, and fixtures for Bio2BEL InterPro."""

import logging
import os

from bio2bel.testing import AbstractTemporaryCacheClassMixin

from bio2bel_interpro.manager import Manager

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
resources_path = os.path.join(dir_path, 'resources')
test_tree_path = os.path.join(resources_path, 'test.txt')
test_go_path = os.path.join(resources_path, 'go.txt')


class TemporaryManagerMixin(AbstractTemporaryCacheClassMixin):
    """An implementation of :class:`bio2bel.testing.AbstractTemporaryCacheClassMixin` for Bio2BEL InterPro."""

    Manager = Manager

    @classmethod
    def populate(cls):
        cls.manager.populate(
            family_entries_url=None,
            tree_url=test_tree_path,
            go_mapping_path=test_go_path,
        )

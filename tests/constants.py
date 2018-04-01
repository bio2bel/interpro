# -*- coding: utf-8 -*-

import logging
import os

from bio2bel.testing import make_temporary_cache_class_mixin
from bio2bel_interpro.manager import Manager

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
test_tree_path = os.path.join(dir_path, 'test.txt')


class TemporaryManagerMixin(make_temporary_cache_class_mixin(Manager)):
    @classmethod
    def populate(cls):
        cls.manager.populate(
            family_entries_url=None,
            tree_url=test_tree_path
        )

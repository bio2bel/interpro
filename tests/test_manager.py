# -*- coding: utf-8 -*-

import logging
import unittest

from tests.constants import TemporaryManagerMixin

log = logging.getLogger(__name__)


class TestManager(TemporaryManagerMixin):
    def test_populated(self):
        """Tests the database was populated and can be queried"""
        result = self.manager.get_family_by_name('Ubiquitin/SUMO-activating enzyme E1')
        self.assertIsNotNone(result)

        child = self.manager.get_family_by_name('Ubiquitin-activating enzyme E1')
        self.assertIsNotNone(child)

        self.assertEqual(result.interpro_id, 'IPR000011')
        self.assertEqual(len(result.children), 1)
        self.assertIn(child, result.children)


if __name__ == '__main__':
    unittest.main()

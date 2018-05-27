# -*- coding: utf-8 -*-

from tests.constants import TemporaryManagerMixin


class TestPopulation(TemporaryManagerMixin):

    def test_interpros(self):
        self.assertEqual(44, self.manager.count_interpros())

    def test_proteins(self):
        self.assertEqual(2, self.manager.count_proteins())

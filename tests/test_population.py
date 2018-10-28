# -*- coding: utf-8 -*-

"""Tests for population of the database."""

from tests.cases import TemporaryCacheClassMixin


class TestPopulation(TemporaryCacheClassMixin):
    """Test the database was populated."""

    def test_interpros(self):
        """Count the number of InterPro entries."""
        self.assertEqual(44, self.manager.count_interpros())

    def test_proteins(self):
        """Count the number of proteins."""
        self.assertEqual(2, self.manager.count_proteins())

# -*- coding: utf-8 -*-

"""Tests for parsing the InterPro tree."""

import unittest

from bio2bel_interpro.parser.tree import parse_tree_helper
from tests.constants import TEST_TREE_PATH


class TestTreeParser(unittest.TestCase):
    """Methods to test that the parser for the InterPro tree works properly."""

    @classmethod
    def setUpClass(cls):
        """Save a copy of the parsed tree for reuse by each of the test methods."""
        with open(TEST_TREE_PATH) as file:
            cls.graph = parse_tree_helper(file)

    def test_names_in_graph(self):
        """Test that all names are nodes in graph."""

        self.assertEqual(
            {
                'C2 domain',
                'Phosphatidylinositol 3-kinase, C2 domain',
                'Tensin phosphatase, C2 domain',
                'Calpain C2 domain',
                'Cystatin domain',
                'Fetuin-A-type cystatin domain',
                'Fetuin-B-type cystatin domain',
                'Kininogen-type cystatin domain',
                'Ubiquitin/SUMO-activating enzyme E1',
                'Ubiquitin-activating enzyme E1',
                'PAS domain',
                'PAS fold-3',
                'PAS fold-4',
                'PAS fold',
                'Anaphylatoxin/fibulin',
                'Anaphylatoxin, complement system',
                'Anaphylatoxin, complement system domain',
                'Guanine-specific ribonuclease N1/T1/U2',
                'Barnase',
                'Fungal ribotoxin',
                'PurE domain',
                'Class II PurE',
                'Class I PurE',
                'Acute myeloid leukemia 1 protein (AML1)/Runt',
                'Runt-related transcription factor RUNX',
                'Adenosylhomocysteinase-like',
                'Adenosylhomocysteinase',
                'Thymidine/pyrimidine-nucleoside phosphorylase',
                'Thymidine phosphorylase/AMP phosphorylase',
                'AMP phosphorylase',
                'Putative thymidine phosphorylase',
                'Pyrimidine-nucleoside phosphorylase, bacterial/eukaryotic',
                'Thymidine phosphorylase',

            },
            {data['name'] for node, data in self.graph.nodes(data=True) if 'name' in data}
        )

        self.assertEqual(set(), {node for node, data in self.graph.nodes(data=True) if 'name' not in data})

        self.assertEqual(33, self.graph.number_of_nodes())

    def test_c2_number_children(self):
        """Test the C2 domain has the right number of children."""
        self.assertEqual(3, len(self.graph['C2 domain']), msg='Edges: {}'.format(list(self.graph['C2 domain'])))

    def test_1(self):
        """Check members of C2 Domain."""
        self.assertIn('Phosphatidylinositol 3-kinase, C2 domain', self.graph['C2 domain'])
        self.assertEqual(0, len(self.graph['Phosphatidylinositol 3-kinase, C2 domain']))

    def test_4(self):
        """Test Tensin phosphatase, C2 domain is not a parent."""
        self.assertIn('Tensin phosphatase, C2 domain', self.graph['C2 domain'])
        self.assertEqual(0, len(self.graph['Tensin phosphatase, C2 domain']))

    def test_5(self):
        """Test that Calpain C2 domain is a child of the C2 domain."""
        self.assertIn('Calpain C2 domain', self.graph['C2 domain'])
        self.assertEqual(0, len(self.graph['Calpain C2 domain']))

    def test_3(self):
        """Test that Phosphatidylinositol 3-kinase, C2 domain has no children."""
        self.assertEqual(0, len(self.graph['Phosphatidylinositol 3-kinase, C2 domain']))

    def test_2(self):
        self.assertEqual(1, len(self.graph['Ubiquitin/SUMO-activating enzyme E1']))
        self.assertIn('Ubiquitin-activating enzyme E1', self.graph['Ubiquitin/SUMO-activating enzyme E1'])

    def test_6(self):
        self.assertEqual(1, len(self.graph['Anaphylatoxin/fibulin']))
        self.assertIn('Anaphylatoxin, complement system', self.graph['Anaphylatoxin/fibulin'])

    def test_7(self):
        self.assertEqual(1, len(self.graph['Anaphylatoxin, complement system']))
        self.assertIn('Anaphylatoxin, complement system domain', self.graph['Anaphylatoxin, complement system'])

    def test_8(self):
        self.assertEqual(2, len(self.graph['Thymidine phosphorylase/AMP phosphorylase']))
        self.assertIn('AMP phosphorylase', self.graph['Thymidine phosphorylase/AMP phosphorylase'])
        self.assertIn('Putative thymidine phosphorylase', self.graph['Thymidine phosphorylase/AMP phosphorylase'])

        self.assertEqual(1, len(self.graph['Pyrimidine-nucleoside phosphorylase, bacterial/eukaryotic']))
        self.assertIn('Thymidine phosphorylase',
                      self.graph['Pyrimidine-nucleoside phosphorylase, bacterial/eukaryotic'])


if __name__ == '__main__':
    unittest.main()

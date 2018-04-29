# -*- coding: utf-8 -*-

import unittest

from bio2bel_interpro.parser.tree import parse_tree_helper
from tests.constants import test_tree_path


class TestTreeParser(unittest.TestCase):
    """Methods to test that the parser for the InterPro tree works properly"""

    @classmethod
    def setUpClass(cls):
        """Saves a copy of the parsed tree for reuse by each of the test methods"""
        with open(test_tree_path) as f:
            cls.graph = parse_tree_helper(f)

    def test_names_in_graph(self):
        """All names are nodes in graph"""

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
        self.assertEqual(3, len(self.graph.edge['C2 domain']),
                         msg='Edges: {}'.format(list(self.graph.edge['C2 domain'])))

    def test_1(self):
        """Checks members of C2 Domain"""
        self.assertIn('Phosphatidylinositol 3-kinase, C2 domain', self.graph.edge['C2 domain'])
        self.assertEqual(0, len(self.graph.edge['Phosphatidylinositol 3-kinase, C2 domain']))

    def test_4(self):
        """Tests Tensin phosphatase, C2 domain is not a parent"""
        self.assertIn('Tensin phosphatase, C2 domain', self.graph.edge['C2 domain'])
        self.assertEqual(0, len(self.graph.edge['Tensin phosphatase, C2 domain']))

    def test_5(self):
        self.assertIn('Calpain C2 domain', self.graph.edge['C2 domain'])
        self.assertEqual(0, len(self.graph.edge['Calpain C2 domain']))

    def test_3(self):
        self.assertEqual(0, len(self.graph.edge['Phosphatidylinositol 3-kinase, C2 domain']))

    def test_2(self):
        self.assertEqual(1, len(self.graph.edge['Ubiquitin/SUMO-activating enzyme E1']))
        self.assertIn('Ubiquitin-activating enzyme E1', self.graph.edge['Ubiquitin/SUMO-activating enzyme E1'])

    def test_6(self):
        self.assertEqual(1, len(self.graph.edge['Anaphylatoxin/fibulin']))
        self.assertIn('Anaphylatoxin, complement system', self.graph.edge['Anaphylatoxin/fibulin'])

    def test_7(self):
        self.assertEqual(1, len(self.graph.edge['Anaphylatoxin, complement system']))
        self.assertIn('Anaphylatoxin, complement system domain', self.graph.edge['Anaphylatoxin, complement system'])

    def test_8(self):
        self.assertEqual(2, len(self.graph.edge['Thymidine phosphorylase/AMP phosphorylase']))
        self.assertIn('AMP phosphorylase', self.graph.edge['Thymidine phosphorylase/AMP phosphorylase'])
        self.assertIn('Putative thymidine phosphorylase', self.graph.edge['Thymidine phosphorylase/AMP phosphorylase'])

        self.assertEqual(1, len(self.graph.edge['Pyrimidine-nucleoside phosphorylase, bacterial/eukaryotic']))
        self.assertIn('Thymidine phosphorylase',
                      self.graph.edge['Pyrimidine-nucleoside phosphorylase, bacterial/eukaryotic'])


if __name__ == '__main__':
    unittest.main()

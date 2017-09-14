# -*- coding: utf-8 -*-

import unittest

from pybel import BELGraph
from pybel.constants import PROTEIN

from bio2bel_interpro.enrich import enrich_proteins

mapk1_hgnc = PROTEIN, 'HGNC', 'MAPK1'
mapk1_uniprot = PROTEIN, 'UNIPROT', 'P28482'

interpro_entries = [
    'IPR011009',  # . Kinase-like_dom.
    'IPR003527',  # . MAP_kinase_CS.
    'IPR008349',  # . MAPK_ERK1/2.
    'IPR000719',  # . Prot_kinase_dom.
    'IPR017441',  # . Protein_kinase_ATP_BS.
    'IPR008271',  # . Ser/Thr_kinase_AS.
]

intepro_node_tuples = [
    (PROTEIN, 'INTERPRO', accession)
    for accession in interpro_entries
]


class TestEnrich(unittest.TestCase):
    def test_annotate(self):
        """Tests that the enrich_proteins function gets the interpro entries in the graph"""
        graph = BELGraph()
        graph.add_simple_node(*mapk1_hgnc)

        self.assertEqual(1, graph.number_of_nodes())

        enrich_proteins(graph)

        for node in interpro_entries:
            self.assertIn(node, graph)
            self.assertIn(node, graph.edge[mapk1_hgnc])


if __name__ == '__main__':
    unittest.main()
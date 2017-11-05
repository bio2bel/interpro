# -*- coding: utf-8 -*-

"""This module tests that proteins in a given BELGraph can be annotated to their families. This file does NOT
test the existence of the InterPro hierarchy"""

import unittest

from bio2bel_interpro.enrich import enrich_node
from pybel import BELGraph
from pybel.constants import IS_A, RELATION
from pybel.dsl import protein

mapk1_hgnc = protein(namespace='HGNC', name='MAPK1', identifier='6871')
mapk1_uniprot = protein(namespace='UNIPROT', identifier='P28482')

interpro_identifiers = [
    'IPR011009',  # . Kinase-like_dom.
    'IPR003527',  # . MAP_kinase_CS.
    'IPR008349',  # . MAPK_ERK1/2.
    'IPR000719',  # . Prot_kinase_dom.
    'IPR017441',  # . Protein_kinase_ATP_BS.
    'IPR008271',  # . Ser/Thr_kinase_AS.
]

interpro_family_nodes = [
    protein(namespace='INTERPRO', identifier=identifier)
    for identifier in interpro_identifiers
]


class TestEnrich(unittest.TestCase):
    def test_enrich_uniprot(self):
        graph = BELGraph()
        mapk1_uniprot_tuple = graph.add_node_from_data(mapk1_uniprot)

        enrich_node(graph, mapk1_uniprot_tuple)

        for interpro_family_node in interpro_family_nodes:
            self.assertTrue(graph.has_node_with_data(interpro_family_node))
            self.assertIn(interpro_family_node, graph.edge[mapk1_uniprot_tuple])
            v = list(graph.edge[mapk1_uniprot_tuple][interpro_family_node].values())[0]
            self.assertIn(RELATION, v)
            self.assertEqual(IS_A, v[RELATION])

    def test_enrich_hgnc(self):
        """Tests that the enrich_proteins function gets the interpro entries in the graph"""
        graph = BELGraph()
        mapk1_hgnc_tuple = graph.add_node_from_data(mapk1_hgnc)

        enrich_node(graph, mapk1_hgnc_tuple)

        for interpro_family_node in interpro_family_nodes:
            self.assertTrue(graph.has_node_with_data(interpro_family_node))
            self.assertIn(interpro_family_node, graph.edge[mapk1_hgnc_tuple])
            v = list(graph.edge[mapk1_hgnc_tuple][interpro_family_node].values())[0]
            self.assertIn(RELATION, v)
            self.assertEqual(IS_A, v[RELATION])


if __name__ == '__main__':
    unittest.main()

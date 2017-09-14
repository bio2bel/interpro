# -*- coding: utf-8 -*-

from pybel_tools import pipeline


@pipeline.in_place_mutator
def enrich_proteins(graph):
    """Adds the InterPro annotations for proteins in the graph

    :param pybel.BELGraph graph: A BEL Graph
    """
    raise NotImplemented


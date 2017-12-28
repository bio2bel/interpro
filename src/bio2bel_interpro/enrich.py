# -*- coding: utf-8 -*-

import logging

from .manager import Manager

log = logging.getLogger(__name__)

__all__ = [
    'enrich_proteins',
    'enrich_interpros',
]


def enrich_proteins(graph, connection=None):
    """Finds UniProt entries and annotates their InterPro entries

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_interpro.manager.Manager
    """
    m = Manager.ensure(connection)
    m.enrich_proteins(graph)


def enrich_interpros(graph, connection=None):
    """Finds InterPro entries and annotates their proteins

    :param pybel.BELGraph graph: A BEL graph
    :type connection: str or bio2bel_interpro.manager.Manager
    """
    m = Manager.ensure(connection=connection)
    m.enrich_interpros(graph)

# -*- coding: utf-8 -*-


import logging
import os
from urllib.request import urlretrieve

import networkx as nx
from tqdm import tqdm

from ..constants import INTERPRO_TREE_PATH, INTERPRO_TREE_URL

__all__ = [
    'download_interpro_tree',
    'parse_tree_helper',
    'get_interpro_tree',
]

log = logging.getLogger(__name__)


def download_interpro_tree(force_download=False):
    """Download the InterPro tree file to the data directory if it doesn't already exist.

    :param bool force_download: Should the data be re-downloaded?
    :rtype: str
    """
    if force_download or not os.path.exists(INTERPRO_TREE_PATH):
        log.info('downloading %s to %s', INTERPRO_TREE_URL, INTERPRO_TREE_PATH)
        urlretrieve(INTERPRO_TREE_URL, INTERPRO_TREE_PATH)
    else:
        log.info('using cached data at %s', INTERPRO_TREE_PATH)

    return INTERPRO_TREE_PATH


def count_front(s):
    """Count the number of leading dashes on a string.

    :param str s: A string
    :rtype: int
    """
    for position, element in enumerate(s):
        if element != '-':
            return position


def get_interpro_tree(path=None, force_download=False):
    """Download and parse the InterPro tree.

    :param Optional[str] path: The path to the InterPro Tree file
    :param bool force_download: Should the data be re-downloaded?
    :rtype: networkx.DiGraph
    """
    if not path:
        path = download_interpro_tree(force_download=force_download)

    with open(path) as f:
        return parse_tree_helper(f)


def parse_tree_helper(lines):
    """Parse the InterPro Tree from the given file.

    :param iter[str] lines: A readable file or file-like
    :rtype: networkx.DiGraph
    """
    graph = nx.DiGraph()
    previous_depth, previous_id, previous_name = 0, None, None
    stack = [previous_name]

    for line in tqdm(lines, desc='Parsing Tree'):
        depth = count_front(line)
        interpro_id, name, _ = line[depth:].split('::')

        if depth == 0:
            stack.clear()
            stack.append(name)

            graph.add_node(name, interpro_id=interpro_id, name=name)

        else:
            if depth > previous_depth:
                stack.append(previous_name)

            elif depth < previous_depth:
                del stack[-1]

            parent = stack[-1]

            graph.add_node(name, interpro_id=interpro_id, parent=parent, name=name)
            graph.add_edge(parent, name)

        previous_depth, previous_id, previous_name = depth, interpro_id, name

    return graph

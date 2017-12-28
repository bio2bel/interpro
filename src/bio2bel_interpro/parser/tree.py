# -*- coding: utf-8 -*-

from __future__ import print_function

import os
from urllib.request import urlretrieve

import networkx as nx
from tqdm import tqdm

from ..constants import DATA_DIR, INTERPRO_TREE_URL

TREE_FILE_PATH = os.path.join(DATA_DIR, 'ParentChildTreeFile.txt')


def ensure_interpro_family_tree_file(force_download=False):
    """Downloads the InterPro tree file to the data directory if it doesn't already exist

    :param bool force_download: Should the data be re-downloaded?
    """
    if force_download or not os.path.exists(TREE_FILE_PATH):
        urlretrieve(INTERPRO_TREE_URL, TREE_FILE_PATH)


def count_front(s):
    """Counts the number of leading dashes on a string

    :param str s: A string
    :rtype: int
    """
    for position, element in enumerate(s):
        if element != '-':
            return position


def parse_tree(path=None, force_download=False):
    """Downlaods and parses the InterPro Tree

    :param Optional[str] path: The path to the InterPro Tree file
    :param bool force_download: Should the data be re-downloaded?
    :rtype: networkx.DiGraph
    """
    if not path:
        ensure_interpro_family_tree_file(force_download=force_download)

    with open(path or TREE_FILE_PATH) as f:
        return parse_tree_helper(f)


def parse_tree_helper(file):
    """Parse the InterPro Tree from the given file

    :param iter[str] file: A readable file or file-like
    :rtype: networkx.DiGraph
    """
    graph = nx.DiGraph()
    previous_depth, previous_id, previous_name = 0, None, None
    stack = [previous_name]

    for line in tqdm(file, desc='Parsing Tree'):
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

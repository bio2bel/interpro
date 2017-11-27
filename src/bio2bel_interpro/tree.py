# -*- coding: utf-8 -*-

from __future__ import print_function

import os
from urllib.request import urlretrieve

import networkx as nx
from tqdm import tqdm

from pybel.resources.arty import get_latest_arty_namespace
from pybel.resources.defaults import CONFIDENCE
from pybel.resources.document import make_knowledge_header
from pybel.utils import ensure_quotes
from .constants import DATA_DIR, INTERPRO_TREE_URL

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
    """Parse the InterPro Tree

    :param iter[str] file: A readable file or file-like
    :rtype: networkx.DiGraph
    """
    graph = nx.DiGraph()
    previous_depth, previous_id, previous_name = 0, None, None
    stack = [previous_name]

    for line in tqdm(file):
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



def write_interpro_family_tree_header(file=None):
    """Writes the BEL document header to the file

    :param file file: A writeable file or file like. Defaults to stdout
    """
    lines = make_knowledge_header(
        name='InterPro Tree',
        authors='Aram Grigoryan and Charles Tapley Hoyt',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents relations from InterPro entity relationship tree""",
        namespace_url={
            'INTERPRO': get_latest_arty_namespace('interpro'),
        },
        namespace_patterns={},
        annotation_url={'Confidence': CONFIDENCE},
        annotation_patterns={},
    )

    for line in lines:
        print(line, file=file)


def write_interpro_family_tree_body(graph, file=None):
    """Creates the lines of BEL document that represents the InterPro tree

    :param networkx.DiGraph graph: A graph representing the InterPro tree from :func:`main`
    :param file file: A writeable file or file-like. Defaults to stdout.
    """
    print('SET Citation = {"PubMed","InterPro","27899635"}', file=file)
    print('SET Evidence = "InterPro Definitions"', file=file)
    print('SET Confidence = "Axiomatic"', file=file)

    for parent, child in graph.edges_iter():
        print(
            'p(INTERPRO:{}) isA p(INTERPRO:{})'.format(
                ensure_quotes(child),
                ensure_quotes(parent),
            ),
            file=file
        )

    print('UNSET ALL', file=file)


def write_interpro_tree(file=None, force_download=False):
    """Creates the entire BEL document representing the InterPro tree

    :param file file: A writeable file or file-like. Defaults to stdout.
    :param bool force_download: Should the data be re-downloaded?
    """
    graph = parse_tree(force_download=force_download)
    write_interpro_family_tree_header(file)
    write_interpro_family_tree_body(graph, file)

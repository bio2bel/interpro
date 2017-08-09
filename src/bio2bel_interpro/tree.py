# -*- coding: utf-8 -*-

import os
from urllib.request import urlretrieve

import fuckit
import networkx as nx

from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import get_latest_arty_namespace
from .constants import INTERPRO_DATA_DIR, INTERPRO_TREE_URL

TREE_FILE_PATH = os.path.join(INTERPRO_DATA_DIR, 'ParentChildTreeFile.txt')


def ensure_tree_file(force_download=False):
    """Downloads the InterPro tree file to the data directory if it doesn't already exist"""
    if not os.path.exists(TREE_FILE_PATH) or force_download:
        urlretrieve(INTERPRO_TREE_URL, TREE_FILE_PATH)


def populate_tree(graph, file, option, parent=None, depth=0):
    """Populates the graph with

    :param graph:
    :param file:
    :param option:
    :param parent:
    :param depth:
    """
    line = file.readline()
    word = '::'.join(line.split('::')[:2])
    dashes = word.split('::')[0].count('-') // 2
    if depth == 0:
        parent = word[2::]
        populate_tree(graph, file, option, parent, depth + 1)

    while word:
        if dashes == depth:

            word = word[2 * dashes::]

            graph.add_edge(parent.split('::')[option], word.split('::')[option])
            # print(parent)
            populate_tree(graph, file, option, parent, depth)
        elif dashes < depth:

            # word = word[2*dashes::]
            populate_tree(graph, file, option, word, depth)
        elif dashes > depth:
            word = word[2 * dashes::]

            graph.add_edge(list(graph.edge[parent.split('::')[option]].keys())[-1], word.split('::')[option])

            populate_tree(graph, file, option, parent, depth)


def parse_interpro_tree(file, opt=1):
    """Parse the InterPro entity relationship tree into a directional graph, where edges from source to
    target signify "hasChild"

    :param file file: A readable file or file-like over the lines of the InterPro entity relationship tree.
    :param int opt: 1 for InterPro names and 0 for InterPro identifiers
    :rtype: networkx.DiGraph

    .. seealso::

        The entity relation tree can be downloaded here: ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt
    """
    assert opt in {0, 1}

    graph = nx.DiGraph()

    with fuckit:
        populate_tree(graph, file, opt, parent=None, depth=0)

    return graph


def get_graph(force_download=False):
    """Downloads the data and puts it into the right place and then calls :func:`parse_interpro_tree`
    returns the result of that function

    :rtype: networkx.DiGraph
    """
    ensure_tree_file(force_download=force_download)

    with open(TREE_FILE_PATH, 'r') as f:
        graph = parse_interpro_tree(f)

    return graph


def write_interpro_tree_boilerplate(file=None):
    """Writes the BEL document header to the file

    :param file file: A writeable file or file like. Defaults to stdout
    """
    write_boilerplate(
        document_name='Interpro relations file',
        authors='Aram Grigoryan and Charles Tapley Hoyt',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents relations from InterPro entity relationship tree""",
        namespace_dict={
            'INTERPRO': get_latest_arty_namespace('interpro'),
        },
        namespace_patterns={},
        annotations_dict={},
        annotations_patterns={},
        file=file
    )


def write_interpro_tree_body(graph, file):
    """Creates the lines of BEL document that represents the InterPro tree

    :param networkx.DiGraph graph: A graph representing the InterPro tree from :func:`main`
    :param file file: A writeable file or file-like. Defaults to stdout.
    """
    for parent, child in graph.edges_iter():
        print(
            'p(INTERPRO:{}) isA p(INTERPRO:{})'.format(
                ensure_quotes(child),
                ensure_quotes(parent),
            ),
            file=file
        )


def write_interpro_tree(graph, file=None):
    """Creates the entire BEL document representing the InterPro tree

    :param networkx.DiGraph graph: A graph representing the InterPro tree from :func:`main`
    :param file file: A writeable file or file-like. Defaults to stdout.
    """
    write_interpro_tree_boilerplate(file)
    write_interpro_tree_body(graph, file)

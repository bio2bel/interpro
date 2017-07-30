# -*- coding: utf-8 -*-

import os

import networkx as nx

from pybel.constants import PYBEL_DATA_DIR
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import get_latest_arty_namespace

INTERPRO_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'interpro')
if not os.path.exists(INTERPRO_DATA_DIR):
    os.makedirs(INTERPRO_DATA_DIR)

TREE_FILE_PATH = os.path.join(INTERPRO_DATA_DIR, 'ParentChildTreeFile.txt')


def read_tree(graph, file, option, parent=None, depth=0):
    """

    :param graph:
    :param file:
    :param option:
    :param parent:
    :param depth:
    :return:
    """
    line = next(file)
    word = '::'.join(line.split('::')[:2])

    while word:
        dashes = word.count('-') // 2
        word = word.lstrip('-')
        if dashes < depth:
            return word

        if dashes >= depth:
            if parent is not None:
                graph.add_edge(parent.split('::')[option], word.split('::')[option])
            word = read_tree(graph, file, option, word, depth + 1)
        else:
            word = read_tree(graph, file, option, parent, depth)


def main(file, opt=1):
    """

    :param file:
    :param opt:
    :return:
    :rtype: networkx.DiGraph
    """
    assert opt in {0, 1}

    graph = nx.DiGraph()
    try:
        read_tree(graph, file, opt, parent=None, depth=0)
    except:
        pass

    if opt == 0:
        assert 'IPR002420' in graph.edge['IPR000008']
        assert 'IPR001840' in graph.edge['IPR018081']
        assert 'IPR033965' in graph.edge['IPR000092']
    else:
        assert 'Phosphatidylinositol 3-kinase, C2 domain' in graph.edge['C2 domain']

        assert 'Histamine H1 receptor' in graph.edge['G protein-coupled receptor, rhodopsin-like']
        assert not graph.edge['Histamine H1 receptor']

        assert 'Dopamine receptor family' in graph.edge['G protein-coupled receptor, rhodopsin-like']
        assert 'Dopamine D1 receptor, C2 domain' in graph.edge['Dopamine receptor family']
        assert not graph.edge['Dopamine D1 receptor, C2 domain']
        assert 'Dopamine D2 receptor, C2 domain' in graph.edge['Dopamine receptor family']
        assert 'Dopamine D3 receptor, C2 domain' in graph.edge['Dopamine receptor family']
        assert 'Dopamine D4 receptor, C2 domain' in graph.edge['Dopamine receptor family']
        assert 'Dopamine D5 receptor, C2 domain' in graph.edge['Dopamine receptor family']
        assert not graph.edge['Dopamine D5 receptor, C2 domain']

    return graph


def make_bel(graph, file):
    """Creates the lines of BEL document that represents the InterPro hierarchy

    :param networkx.DiGraph graph: A graph representing the InterPro hierarchy from :func:`main`
    :return: An iterator over the lines of a BEL document
    :rtype: iter[str]
    """

    # make header stuff
    write_boilerplate(
        document_name='Interpro relations file',
        authors='Aram Grigoryan',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents relations from interpro parent child tree file""",
        namespace_dict={
            'INTERPRO': get_latest_arty_namespace('interpro'),
        },
        namespace_patterns={},
        annotations_dict={},
        annotations_patterns={},
        file=file
    )

    for parent, child in graph.edges_iter():
        print('p(INTERPRO:{}) isA p(INTERPRO:{})'.format(
            ensure_quotes(child),
            ensure_quotes(parent),
        ), file=file)


def write_interpro_bel(in_file, file=None):
    """

    :param file in_file:
    :param file file:
    :return:
    """
    G = main(in_file)
    make_bel(G, file)


if __name__ == '__main__':
    with open(TREE_FILE_PATH, 'r') as f, open(os.path.join(INTERPRO_DATA_DIR, 'interpro_hierarchy.bel'), 'w') as f2:
        write_interpro_bel(f, f2)

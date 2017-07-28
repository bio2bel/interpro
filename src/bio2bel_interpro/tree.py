import os

import networkx as nx
from pybel.constants import PYBEL_DATA_DIR
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate
from pybel_tools.resources import get_latest_arty_namespace

CHEMBL_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'chembl')
if not os.path.exists(CHEMBL_DATA_DIR):
    os.makedirs(CHEMBL_DATA_DIR)

TREE_FILE_PATH = os.path.join(CHEMBL_DATA_DIR, 'ParentChildTreeFile.txt')


def read_tree(G, file, option, parent=None, depth=0):
    line = next(file)
    word = '::'.join(line.split('::')[:2])
    while word:
        dashes = word.count('-') // 2
        word = word.lstrip('-')
        if dashes < depth:
            return word

        if dashes >= depth:
            if parent is not None:
                G.add_edge(parent.split('::')[option], word.split('::')[option])
            word = read_tree(G, file, option, word, depth + 1)
        else:
            word = read_tree(G, file, option, parent, depth)


def main(file):
    G = nx.DiGraph()
    opt = 1 #1 for name 0 for ID
    try:
        read_tree(G, file, opt, parent=None, depth=0)
    except:
        pass
    if opt == 0:
        assert 'IPR002420' in G.edge['IPR000008']
        assert 'IPR001840' in G.edge['IPR018081']
        assert 'IPR033965' in G.edge['IPR000092']
    else:
        if opt == 1:
            assert 'Phosphatidylinositol 3-kinase, C2 domain' in G.edge['C2 domain']
        else:
            assert opt == 0 or opt == 1

    return G


def make_bel(G, file):
    """Creates the lines of BEL document that represents the InterPro hierarchy

    :param networkx.DiGraph G:
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

    for parent, child in G.edges_iter():
        print('p(INTERPRO:{}) isA p(INTERPRO:{})'.format(
            ensure_quotes(child),
            ensure_quotes(parent),
        ), file=file)


def write_interpro_bel(in_file, file=None):
    G = main(in_file)
    make_bel(G, file)


if __name__ == '__main__':
    with open(TREE_FILE_PATH, 'r') as f, open(os.path.join(CHEMBL_DATA_DIR, 'blahblah.bel'), 'w') as f2:
        write_interpro_bel(f, f2)

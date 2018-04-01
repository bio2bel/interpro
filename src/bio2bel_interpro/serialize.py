# -*- coding: utf-8 -*-

from pybel.resources import CONFIDENCE, get_latest_arty_namespace, make_knowledge_header
from pybel.utils import ensure_quotes
from .parser.tree import get_interpro_tree


def write_interpro_tree_header(file=None):
    """Writes the BEL document header to the file

    :param file file: A writeable file or file like. Defaults to stdout
    """
    lines = make_knowledge_header(
        name='InterPro Tree',
        authors='Charles Tapley Hoyt',
        contact='charles.hoyt@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
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


def write_interpro_tree_body(graph, file=None):
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
    graph = get_interpro_tree(force_download=force_download)
    write_interpro_tree_header(file)
    write_interpro_tree_body(graph, file)

# -*- coding: utf-8 -*-

"""Testing constants for Bio2BEL InterPro."""

import os

__all__ = [
    'TEST_ENTRIES_PATH',
    'TEST_TREE_PATH',
    'TEST_INTERPRO_GO_MAPPINGS_PATH',
    'TEST_INTERPRO_PROTEIN_MAPPINGS_PATH',
]

HERE = os.path.dirname(os.path.realpath(__file__))
RESOURCES_DIR = os.path.join(HERE, 'resources')

TEST_ENTRIES_PATH = os.path.join(RESOURCES_DIR, 'test.entry.list')
TEST_TREE_PATH = os.path.join(RESOURCES_DIR, 'test.ParentChildTreeFile.txt')
TEST_INTERPRO_GO_MAPPINGS_PATH = os.path.join(RESOURCES_DIR, 'test.interpro2go.txt')
TEST_INTERPRO_PROTEIN_MAPPINGS_PATH = os.path.join(RESOURCES_DIR, 'test.protein2ipr.dat.gz')

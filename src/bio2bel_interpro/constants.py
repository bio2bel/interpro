# -*- coding: utf-8 -*-

import os

MODULE_NAME = 'interpro'
BIO2BEL_DIR = os.environ.get('BIO2BEL_DIRECTORY', os.path.join(os.path.expanduser('~'), '.pybel', 'bio2bel'))
DATA_DIR = os.path.join(BIO2BEL_DIR, MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_CACHE_NAME = '{}.db'.format(MODULE_NAME)
DEFAULT_CACHE_PATH = os.path.join(DATA_DIR, DEFAULT_CACHE_NAME)
DEFAULT_CACHE_CONNECTION = os.environ.get('BIO2BEL_CONNECTION', 'sqlite:///' + DEFAULT_CACHE_PATH)

#: Data source for InterPro entries
INTERPRO_ENTRIES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
#: Data source for InterPro tree
INTERPRO_TREE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt'

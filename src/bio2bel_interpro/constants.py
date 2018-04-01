# -*- coding: utf-8 -*-

import os

from bio2bel.utils import get_connection, get_data_dir

MODULE_NAME = 'interpro'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

#: Data source for InterPro entries
INTERPRO_ENTRIES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
INTERPRO_ENTRIES_PATH = os.path.join(DATA_DIR, 'entry.list')

#: Data source for InterPro tree
INTERPRO_TREE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt'
INTERPRO_TREE_PATH = os.path.join(DATA_DIR, 'ParentChildTreeFile.txt')

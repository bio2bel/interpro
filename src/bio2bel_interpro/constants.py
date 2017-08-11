# -*- coding: utf-8 -*-

import os

#: Data source for InterPro entries
INTERPRO_ENTRIES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
entries = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
INTERPRO_TREE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt'

INTERPRO_DATA_DIR = os.path.join(os.path.expanduser('~'), '.pyinterpro')

if not os.path.exists(INTERPRO_DATA_DIR):
    os.makedirs(INTERPRO_DATA_DIR)

INTERPRO_DATABASE_NAME = 'interpro_database.db'
INTERPRO_SQLITE_PATH = 'sqlite:///' + os.path.join(INTERPRO_DATA_DIR, INTERPRO_DATABASE_NAME)

INTERPRO_CONFIG_FILE_PATH = os.path.join(INTERPRO_DATA_DIR, 'config.ini')

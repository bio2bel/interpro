# -*- coding: utf-8 -*-

import os

from bio2bel import get_connection, get_data_dir

MODULE_NAME = 'interpro'
DATA_DIR = get_data_dir(MODULE_NAME)
DEFAULT_CACHE_CONNECTION = get_connection(MODULE_NAME)

#: Data source for InterPro entries
INTERPRO_ENTRIES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
INTERPRO_ENTRIES_PATH = os.path.join(DATA_DIR, 'entry.list')

#: Data source for InterPro tree
INTERPRO_TREE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt'
INTERPRO_TREE_PATH = os.path.join(DATA_DIR, 'ParentChildTreeFile.txt')

#: Data source for protein-interpro mappings
INTERPRO_PROTEIN_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/protein2ipr.dat.gz'
INTERPRO_PROTEIN_PATH = os.path.join(DATA_DIR, 'protein2ipr.dat.gz')

#: Data source for interpro-GO mappings
INTERPRO_GO_MAPPING_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go'
INTERPRO_GO_MAPPING_PATH = os.path.join(DATA_DIR, 'interpro2go.txt')

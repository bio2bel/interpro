# -*- coding: utf-8 -*-

"""Constants for Bio2BEL InterPro."""

import os

from bio2bel import get_data_dir

MODULE_NAME = 'interpro'
DATA_DIR = get_data_dir(MODULE_NAME)

#: Data source for InterPro entries
INTERPRO_ENTRIES_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
INTERPRO_ENTRIES_PATH = os.path.join(DATA_DIR, 'entry.list')

INTERPRO_ENTRIES_COLUMNS = ['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']

#: Data source for InterPro tree
INTERPRO_TREE_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/ParentChildTreeFile.txt'
INTERPRO_TREE_PATH = os.path.join(DATA_DIR, 'ParentChildTreeFile.txt')

#: Data source for protein-interpro mappings
INTERPRO_PROTEIN_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/protein2ipr.dat.gz'
INTERPRO_PROTEIN_PATH = os.path.join(DATA_DIR, 'protein2ipr.dat.gz')

INTERPRO_PROTEIN_COLUMNS = [
    'uniiprot_id',
    'interpro_id',
    'interpro_name',
    'xref',  # either superfamily, gene family gene scan, PFAM, TIGERFAM
    'start',  # int
    'end',  # int
]

CHUNKSIZE = 500000

#: Data source for protein-interpro mappings
INTERPRO_PROTEIN_HASH_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/current/protein2ipr.dat.gz.md5'
INTERPRO_PROTEIN_HASH_PATH = os.path.join(DATA_DIR, 'protein2ipr.dat.gz.md5')

#: Data source for interpro-GO mappings
INTERPRO_GO_MAPPING_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go'
INTERPRO_GO_MAPPING_PATH = os.path.join(DATA_DIR, 'interpro2go.txt')

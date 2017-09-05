# -*- coding: utf-8 -*-

import os
import pandas as pd
import re
from urllib.request import urlretrieve

from pybel.constants import PYBEL_DATA_DIR
from pybel_tools.definition_utils import write_namespace
from pybel_tools.document_utils import write_boilerplate
from pybel.utils import ensure_quotes

INTERPRO_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'interpro')
if not os.path.exists(INTERPRO_DATA_DIR):
    os.makedirs(INTERPRO_DATA_DIR)

URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go'
MAPPING_FILE = os.path.join(INTERPRO_DATA_DIR, 'interpro2go')

INTERPRO_REGEX = '(InterPro)(.)(IPR)(\d+)'
GO_REGEX = '(GO)(.)(\d+)($)'

def download_mapping_file(force=False):
    """Downloads Mapping file if not found on file system

    :param bool force: Forces the download
    """
    if force:
        urlretrieve(URL, MAPPING_FILE)
    elif not os.path.isfile(MAPPING_FILE):
        urlretrieve(URL, MAPPING_FILE)


def get_data():
    """
    Extracts mapping data from file and returns the Data as Data Frame
    :return: pandas.DataFrame : Data as Data Frame
    """
    download_mapping_file()
    data = []

    with open(MAPPING_FILE, 'r') as file:
        for line in file:
            if line[0] == '!':
                continue
            go_id = re.search(GO_REGEX, line).group().split(':')[1]
            interpro_id = re.search(INTERPRO_REGEX, line).group().split(':')[1]
            data.append([interpro_id, go_id])
    df = pd.DataFrame(data, columns=['interpro_id', 'go_id'], dtype=str)
    return df




if __name__ == '__main__':
    df = get_data()
    print(df.head())
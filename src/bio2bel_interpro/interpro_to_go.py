# -*- coding: utf-8 -*-

import logging
import os
import re
from urllib.request import urlretrieve

import pandas as pd
from pybel.constants import PYBEL_DATA_DIR
from pybel.utils import ensure_quotes
from pybel_tools.document_utils import write_boilerplate

log = logging.getLogger(__name__)

INTERPRO_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'interpro')
if not os.path.exists(INTERPRO_DATA_DIR):
    os.makedirs(INTERPRO_DATA_DIR)

URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go'
MAPPING_FILE = os.path.join(INTERPRO_DATA_DIR, 'interpro2go')
DESTINATION_FILE = os.path.join(INTERPRO_DATA_DIR, 'interpro_to_go.bel')

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
    log.info("\n{}".format(df.head()))
    log.info("\n{} entries in total".format(len(df)))
    return df


def write_interpro_to_go_belns(file, df=None):
    """
    WRITES BEL MAPPING NAMESPACE FILE
    :return: None
    """
    df = get_data() if df is None else df

    write_boilerplate(
        document_name='InterPro to GO equivalence',
        authors='Aram Grigoryan',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents InterPro to GO strings equivalence""",
        namespace_dict={
            'InterPro': INTERPRO_REGEX,
            'GO': GO_REGEX,
        },
        namespace_patterns={},
        annotations_dict={},
        annotations_patterns={},
        file=file
    )

    print('SET Citation = {{"URL","{}"}}'.format(
        "https://academic.oup.com/nar/article/45/D1/D190/2605789/InterPro-in-2017-beyond-protein-family-and-domain"),
          file=file)
    print('SET Evidence = "InterPro to GO mapping"', file=file)

    for _, interpro_id, go_id in df[['interpro_id', 'go_id']].itertuples():
        interpro_clean = ensure_quotes(str(interpro_id).strip())
        go_clean = ensure_quotes(str(go_id).strip())
        print('p(InterPro:{}) eq p(GO:{})'.format(interpro_clean, go_clean), file=file)


if __name__ == '__main__':
    log.setLevel(20)
    logging.basicConfig(level=20)
    with open(DESTINATION_FILE, 'w+') as f:
        write_interpro_to_go_belns(f)

# -*- coding: utf-8 -*-

import logging
import os
import re
from urllib.request import urlretrieve

import pandas as pd

from bio2bel_interpro.constants import INTERPRO_DATA_DIR
from pybel.resources.document import make_knowledge_header
from pybel.utils import ensure_quotes

log = logging.getLogger(__name__)

INTERPRO_GO_MAPPING_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/interpro2go'
#: Local download location for interpro2go mapping
INTERPRO_GO_MAPPING_PATH = os.path.join(INTERPRO_DATA_DIR, 'interpro2go.txt')

INTERPRO_REGEX = '(InterPro)(.)(IPR)(\d+)'
INTERPRO_REGEX_COMPILED = re.compile(INTERPRO_REGEX)
GO_REGEX = '(GO)(.)(\d+)($)'
GO_REGEX_COMPILED = re.compile(GO_REGEX)


def ensure_interpro_go_mapping_file(force_download=False):
    """Downloads Mapping file if not found on file system

    :param bool force_download: Forces the download
    """
    if force_download or not os.path.exists(INTERPRO_GO_MAPPING_PATH):
        log.info('downloading interpro2go mapping from %s', INTERPRO_GO_MAPPING_URL)
        urlretrieve(INTERPRO_GO_MAPPING_URL, INTERPRO_GO_MAPPING_PATH)


def get_interpro_go_mapping(force_download=False):
    """ Extracts mapping data from file and returns the Data as Data Frame

    :return: pandas.DataFrame : Data as Data Frame
    """
    ensure_interpro_go_mapping_file(force_download=force_download)
    data = []

    with open(INTERPRO_GO_MAPPING_PATH, 'r') as file:
        for line in file:
            if line[0] == '!':
                continue

            go_id = GO_REGEX_COMPILED.search(line).group().split(':')[1]
            interpro_id = INTERPRO_REGEX_COMPILED.search(line).group().split(':')[1]
            data.append([interpro_id, go_id])

    df = pd.DataFrame(data, columns=['interpro_id', 'go_id'], dtype=str)

    log.info("Head:\n %s", df.head())
    log.info('entries in total: %d', len(df))

    return df


def write_interpro_to_go_bel(file=None, df=None, force_download=False):
    """Converts the InterPro to GO mapping to BEL

    :param file:
    :param df:
    :param bool force_download:
    """
    df = get_interpro_go_mapping(force_download=force_download) if df is None else df

    lines = make_knowledge_header(
        name='InterPro to GO equivalence',
        authors='Aram Grigoryan',
        contact='aram.grigoryan@scai.fraunhofer.de',
        licenses='Creative Commons by 4.0',
        copyright='Copyright (c) 2017 Aram Grigoryan. All Rights Reserved.',
        description="""This BEL document represents InterPro to GO strings equivalence""",
        namespace_url={
            'InterPro': INTERPRO_REGEX,
            'GO': GO_REGEX,
        },
        namespace_patterns={},
        annotation_url={},
        annotation_patterns={},
    )

    for line in lines:
        print(line, file=file)

    print('SET Citation = {"PubMed","27899635"}', file=file)
    print('SET Evidence = "InterPro to GO mapping"', file=file)

    for _, interpro_id, go_id in df[['interpro_id', 'go_id']].itertuples():
        interpro_clean = ensure_quotes(str(interpro_id).strip())
        go_clean = ensure_quotes(str(go_id).strip())
        print('p(InterPro:{}) -- bp(GO:{})'.format(interpro_clean, go_clean), file=file)


if __name__ == '__main__':
    logging.basicConfig(level=10)
    log.setLevel(10)

    with open(os.path.expanduser('~/Desktop/interpro2go.bel'), 'w') as f:
        write_interpro_to_go_bel(f)

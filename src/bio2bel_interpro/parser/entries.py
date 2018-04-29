# -*- coding: utf-8 -*-

import logging
import os
from urllib.request import urlretrieve

import pandas as pd

from ..constants import INTERPRO_ENTRIES_PATH, INTERPRO_ENTRIES_URL

__all__ = [
    'download_interpro_entries',
    'get_interpro_entries_df',
]

log = logging.getLogger(__name__)


def download_interpro_entries(force_download=False):
    """Downloads the InterPro entries file

    :param bool force_download: If true, overwrites a previously cached file
    :rtype: str
    """
    if os.path.exists(INTERPRO_ENTRIES_PATH) and not force_download:
        log.info('using cached data at %s', INTERPRO_ENTRIES_PATH)
    else:
        log.info('downloading %s to %s', INTERPRO_ENTRIES_URL, INTERPRO_ENTRIES_PATH)
        urlretrieve(INTERPRO_ENTRIES_URL, INTERPRO_ENTRIES_PATH)

    return INTERPRO_ENTRIES_PATH


def get_interpro_entries_df(url=None, cache=True, force_download=False):
    """Gets the entries data

    :return: A data frame containing the original source data
    :rtype: pandas.DataFrame
    """
    if url is None and cache:
        url = download_interpro_entries(force_download=force_download)

    return pd.read_csv(
        url,
        sep='\t',
        skiprows=1,
        names=('ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME')
    )

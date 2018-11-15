# -*- coding: utf-8 -*-

"""Downloaders and parsers for InterPro entries."""

import logging
from typing import Optional

import pandas as pd

from bio2bel.downloading import make_downloader
from ..constants import INTERPRO_ENTRIES_PATH, INTERPRO_ENTRIES_URL

__all__ = [
    'download_entries',
    'get_entries_df',
]

log = logging.getLogger(__name__)

download_entries = make_downloader(INTERPRO_ENTRIES_URL, INTERPRO_ENTRIES_PATH)


def get_entries_df(url: Optional[str] = None, cache: bool = True, force_download: bool = False) -> pd.DataFrame:
    """Get the entries' data.

    :return: A data frame containing the original source data
    """
    if url is None and cache:
        url = download_entries(force_download=force_download)

    return pd.read_csv(
        url,
        sep='\t',
        skiprows=1,
        names=('ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME')
    )

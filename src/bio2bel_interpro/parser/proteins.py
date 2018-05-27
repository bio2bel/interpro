# -*- coding: utf-8 -*-

import logging

import pandas
from bio2bel import make_downloader

from ..constants import (
    CHUNKSIZE, INTERPRO_PROTEIN_HASH_PATH, INTERPRO_PROTEIN_HASH_URL, INTERPRO_PROTEIN_PATH,
    INTERPRO_PROTEIN_URL,
)

__all__ = [
    'download_interpro_proteins_mapping',
    'download_interpro_proteins_mapping_hash',
    'get_proteins_df',
]

log = logging.getLogger(__name__)

download_interpro_proteins_mapping = make_downloader(INTERPRO_PROTEIN_URL, INTERPRO_PROTEIN_PATH)
download_interpro_proteins_mapping_hash = make_downloader(INTERPRO_PROTEIN_HASH_URL, INTERPRO_PROTEIN_HASH_PATH)


def get_proteins_df(url=None, cache=True, force_download=False, chunksize=None):
    if url is None and cache:
        url = download_interpro_proteins_mapping(force_download=force_download)

    return pandas.read_csv(
        url or INTERPRO_PROTEIN_URL,
        sep='\t',
        compression='gzip',
        usecols=[0, 1, 3, 4, 5],
        chunksize=(chunksize or CHUNKSIZE)
    )

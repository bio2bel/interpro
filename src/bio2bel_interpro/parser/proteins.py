# -*- coding: utf-8 -*-

"""Utilities for handling InterPro protein mappings."""

import logging
from typing import Optional

import pandas

from bio2bel import make_downloader
from ..constants import (
    CHUNKSIZE, INTERPRO_PROTEIN_COLUMNS, INTERPRO_PROTEIN_HASH_PATH, INTERPRO_PROTEIN_HASH_URL, INTERPRO_PROTEIN_PATH,
    INTERPRO_PROTEIN_URL,
)

__all__ = [
    'download_interpro_proteins_mapping',
    'download_interpro_proteins_mapping_hash',
    'get_proteins_chunks',
]

log = logging.getLogger(__name__)

download_interpro_proteins_mapping = make_downloader(INTERPRO_PROTEIN_URL, INTERPRO_PROTEIN_PATH)
download_interpro_proteins_mapping_hash = make_downloader(INTERPRO_PROTEIN_HASH_URL, INTERPRO_PROTEIN_HASH_PATH)


def get_proteins_chunks(url: Optional[str] = None, cache: bool = True, force_download: bool = False,
                        chunksize: Optional[int] = None, compression: str = 'gzip'):
    """Get protein mappings."""
    if url is None and cache:
        url = download_interpro_proteins_mapping(force_download=force_download)

    return pandas.read_csv(
        url or INTERPRO_PROTEIN_URL,
        sep='\t',
        compression=compression,
        usecols=[0, 1, 3, 4, 5],
        names=INTERPRO_PROTEIN_COLUMNS,
        chunksize=(chunksize or CHUNKSIZE)
    )

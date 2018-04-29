# -*- coding: utf-8 -*-

import logging

from bio2bel import make_downloader

from ..constants import INTERPRO_PROTEIN_PATH, INTERPRO_PROTEIN_URL

__all__ = [
    'download_interpro_proteins_mapping',
    'get_proteins_df',
]

log = logging.getLogger(__name__)

download_interpro_proteins_mapping = make_downloader(INTERPRO_PROTEIN_URL, INTERPRO_PROTEIN_PATH)


def get_proteins_df(url=None, cache=True, force_download=False):
    if url is None and cache:
        url = download_interpro_proteins_mapping(force_download=force_download)

    return

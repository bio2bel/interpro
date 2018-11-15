# -*- coding: utf-8 -*-

"""Utilities for InterPro - GO mappings."""

import logging
from typing import List, Tuple

from bio2bel import make_downloader
from bio2bel_interpro.constants import INTERPRO_GO_MAPPING_PATH, INTERPRO_GO_MAPPING_URL

__all__ = [
    'download_interpro_go_mapping',
    'get_interpro_go_mappings',
]

log = logging.getLogger(__name__)

download_interpro_go_mapping = make_downloader(INTERPRO_GO_MAPPING_URL, INTERPRO_GO_MAPPING_PATH)


def get_interpro_go_mappings(path=None, cache=True, force_download=False) -> List[Tuple[str, str, str]]:
    """Get mappings from InterPro to GO."""
    if path is None and cache:
        path = download_interpro_go_mapping(force_download=force_download)

    with open(path) as file:
        return _operate_file(file)


def _operate_file(file) -> List[Tuple[str, str, str]]:
    return [
        _process_line(line.strip())
        for line in file
        if line[0] != '!'
    ]


def _process_line(line: str) -> Tuple[str, str, str]:
    pos = line.find('> GO')
    interpro_terms, go_term = line[:pos], line[pos:]
    interpro_id, interpro_name = interpro_terms.strip().split(' ', 1)
    go_name, go_id = go_term.split(';')

    return (
        interpro_id.strip().split(':')[1],
        go_id.strip()[len('GO:'):],
        go_name.strip()[len('GO:'):],
    )

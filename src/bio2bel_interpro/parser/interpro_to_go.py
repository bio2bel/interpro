# -*- coding: utf-8 -*-

import logging

from bio2bel import make_downloader

from bio2bel_interpro.constants import INTERPRO_GO_MAPPING_PATH, INTERPRO_GO_MAPPING_URL

__all__ = [
    'ensure_interpro_go_mapping_file',
    'get_go_mappings',
]

log = logging.getLogger(__name__)

ensure_interpro_go_mapping_file = make_downloader(INTERPRO_GO_MAPPING_URL, INTERPRO_GO_MAPPING_PATH)


def _process_line(line):
    if line.count('>') > 1:
        log.warning('line has multiple chevrons: %s', line)
        return None, None, None

    interpro_terms, go_term = line.split('>')
    interpro_id, interpro_name = interpro_terms.strip().split(' ', 1)
    go_name, go_id = go_term.split(';')

    return interpro_id.strip().split(':')[1], go_id.strip()[len('GO:'):], go_name.strip()[len('GO:'):]


def _operate_file(file):
    return [
        _process_line(line.strip())
        for line in file
        if line[0] != '!'
    ]


def get_go_mappings(path=None, cache=True, force_download=False):
    """
    :rtype: pandas.DataFrame
    """
    if path is None and cache:
        path = ensure_interpro_go_mapping_file(force_download=force_download)

    with open(path) as file:
        return _operate_file(file)

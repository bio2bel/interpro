# -*- coding: utf-8 -*-

from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel.resources.definitions import write_namespace
from .constants import MODULE_NAME
from .parser.entries import get_interpro_entries_data


def get_names():
    """Downloads and extracts the InterPro name list

    :rtype: pandas.DataFrame
    """
    entries_df = get_interpro_entries_data()
    return entries_df['ENTRY_NAME']


def write_belns(file=None, values=None):
    """Writes the InterPro entries namespace

    :param file file: A write-enabled file or file-like. Defaults to standard out
    :param values: The values to write
    """
    values = get_names() if values is None else values

    write_namespace(
        namespace_name='InterPro Protein Families',
        namespace_keyword=MODULE_NAME.upper(),
        namespace_domain=NAMESPACE_DOMAIN_GENE,
        author_name='Charles Tapley Hoyt',
        author_contact='charles.hoyt@scai.fraunhofer.de',
        author_copyright='Creative Commons by 4.0',
        citation_name='InterPro',
        values=values,
        functions='P',
        file=file
    )

# -*- coding: utf-8 -*-

import pandas as pd

from pybel.constants import NAMESPACE_DOMAIN_GENE
from pybel_tools.definition_utils import write_namespace
from pybel_tools.resources import deploy_namespace, get_today_arty_namespace
from .constants import INTERPRO_ENTRIES_URL

MODULE_NAME = 'interpro'


def get_data():
    """Downloads the entry list into a pandas DataFrame

    :rtype: pandas.DataFrame
    """
    return pd.read_csv(INTERPRO_ENTRIES_URL, sep='\t')


def get_names():
    """Downloads and extracts the InterPro name list

    :rtype: pandas.DataFrame
    """
    entries_df = get_data()
    return entries_df['ENTRY_NAME']


def write_belns(file, values=None):
    values = get_names() if values is None else values

    write_namespace(
        namespace_name='InterPro Protein Families',
        namespace_keyword='INTERPRO',
        namespace_domain=NAMESPACE_DOMAIN_GENE,
        author_name='Charles Tapley Hoyt',
        author_contact='charles.hoyt@scai.fraunhofer.de',
        author_copyright='Creative Commons by 4.0',
        citation_name='InterPro',
        values=values,
        functions='P',
        file=file
    )


def deploy_to_arty():
    """Gets the data and writes BEL namespace file to artifactory"""

    file_name = get_today_arty_namespace(MODULE_NAME)

    with open(file_name, 'w') as file:
        write_belns(file)

    deploy_namespace(file_name, MODULE_NAME)


if __name__ == '__main__':
    deploy_to_arty()

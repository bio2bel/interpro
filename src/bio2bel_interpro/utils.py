# -*- coding: utf-8 -*-

import pandas as pd

from .constants import INTERPRO_ENTRIES_URL


def get_family_entries_data():
    """Gets the entries data

    :return: A data frame containing the original source data
    :rtype: pandas.DataFrame
    """
    return pd.read_csv(
        INTERPRO_ENTRIES_URL,
        sep='\t',
        skiprows=1,
        names=('ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME')
    )

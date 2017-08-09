# -*- coding: utf-8 -*-

import configparser
import logging
import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .constants import (
    INTERPRO_ENTRIES_URL,
    INTERPRO_SQLITE_PATH,
    INTERPRO_CONFIG_FILE_PATH,
)
from .models import Base, Entry
from .tree import get_graph

log = logging.getLogger(__name__)


def get_data():
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


class Manager(object):
    """Creates a connection to database and a persistient session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param str connection: SQLAlchemy
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = self.get_connection_string(connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.sessionmaker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.sessionmaker)
        self.create_tables()

    def create_tables(self, check_first=True):
        """creates all tables from models in your database

        :param bool check_first: True or False check if tables already exists
        """
        log.info('create tables in {}'.format(self.engine.url))
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_tables(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine)

    @staticmethod
    def get_connection_string(connection=None):
        """Return the SQLAlchemy connection string if it is set

        :param connection: get the SQLAlchemy connection string
        :rtype: str
        """
        if connection:
            return connection

        config = configparser.ConfigParser()

        cfp = INTERPRO_CONFIG_FILE_PATH

        if os.path.exists(cfp):
            log.info('fetch database configuration from {}'.format(cfp))
            config.read(cfp)
            connection = config['database']['sqlalchemy_connection_string']
            log.info('load connection string from {}: {}'.format(cfp, connection))
            return connection

        with open(cfp, 'w') as config_file:
            config['database'] = {'sqlalchemy_connection_string': INTERPRO_SQLITE_PATH}
            config.write(config_file)
            log.info('create configuration file {}'.format(cfp))

        return INTERPRO_SQLITE_PATH

    def populate(self, force_download=False):
        """Populates the database

        :param bool force_download: Should the data be downloaded again, or cache used if exists?
        """
        df = get_data()

        id_model = {}

        for _, accession, entry_type, name in df[['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']].itertuples():
            entry = Entry(
                accession=accession,
                type=entry_type,
                name=name
            )
            self.session.add(entry)
            id_model[name] = entry

        graph = get_graph(force_download=force_download)

        for parent, child in graph.edges_iter():
            id_model[parent].children.append(id_model[child])

        self.session.commit()

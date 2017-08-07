import configparser
import logging
import os

import pandas as pd

from . import models

log = logging.getLogger(__name__)

from sqlalchemy import create_engine
from pybel.constants import PYBEL_DATA_DIR
from sqlalchemy.orm import sessionmaker, scoped_session

from .. import tree

INTERPRO_DATA_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/interpro/entry.list'
INTERPRO_DATABASE_NAME = 'interpro_database.db'
INTERPRO_DATA_DIR = os.path.join(PYBEL_DATA_DIR, 'bio2bel', 'interpro')
INTERPRO_SQLITE_PATH = 'sqlite:///' + os.path.join(INTERPRO_DATA_DIR, INTERPRO_DATABASE_NAME)
INTERPRO_CONFIG_FILE_PATH = os.path.join(INTERPRO_DATA_DIR, 'config.ini')

if not os.path.exists(INTERPRO_DATA_DIR):
    os.makedirs(INTERPRO_DATA_DIR)


def get_data():
    """Gets the source data.

    :return: A data frame containing the original source data
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(
        INTERPRO_DATA_URL,
        sep='\t',
        skiprows=1,
        names=['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']
    )
    return df


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

    def create_tables(self, checkfirst=True):
        """creates all tables from models in your database

        :param checkfirst: True or False check if tables already exists
        :type checkfirst: bool
        :return:
        """
        log.info('create tables in {}'.format(self.engine.url))
        models.Base.metadata.create_all(self.engine, checkfirst=checkfirst)

    def drop_tables(self):
        """drops all tables in the database

        :return:
        """
        log.info('drop tables in {}'.format(self.engine.url))
        models.Base.metadata.drop_all(self.engine)

    @staticmethod
    def get_connection_string(connection=None):
        """return sqlalchemy connection string if it is set

        :param connection: get the SQLAlchemy connection string #TODO
        :return:
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

    def write_db(self):
        df = get_data()

        id_model = {}

        for _, id, type, name in df[['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']].itertuples():
            m = models.Interpro(accession=id, type=type, name=name)
            self.session.add(m)
            id_model[id] = m

        graph = tree.get_graph()
        for parent, child in graph.edges_iter():
            id_model[parent].children.append(id_model[child])
        self.session.commit()

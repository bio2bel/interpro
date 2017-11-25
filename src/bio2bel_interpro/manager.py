# -*- coding: utf-8 -*-

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from bio2bel.utils import get_connection
from .constants import MODULE_NAME
from .models import Base, Family
from .tree import get_interpro_family_tree
from .utils import get_family_entries_data

log = logging.getLogger(__name__)


class Manager(object):
    """Creates a connection to database and a persistent session using SQLAlchemy"""

    def __init__(self, connection=None, echo=False):
        """
        :param Optional[str] connection: SQLAlchemy connection string
        :param bool echo: True or False for SQL output of SQLAlchemy engine
        """
        self.connection = get_connection(MODULE_NAME, connection=connection)
        self.engine = create_engine(self.connection, echo=echo)
        self.session_maker = sessionmaker(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.session = scoped_session(self.session_maker)
        self.create_all()

    def create_all(self, check_first=True):
        """creates all tables from models in your database

        :param bool check_first: True or False check if tables already exists
        """
        Base.metadata.create_all(self.engine, checkfirst=check_first)

    def drop_all(self):
        """drops all tables in the database"""
        log.info('drop tables in {}'.format(self.engine.url))
        Base.metadata.drop_all(self.engine)

    def populate_entries(self, force_download=False):
        """Populates the database

        :param bool force_download: Should the data be downloaded again, or cache used if exists?
        """
        df = get_family_entries_data()

        id_model = {}

        for _, accession, entry_type, name in df[['ENTRY_AC', 'ENTRY_TYPE', 'ENTRY_NAME']].itertuples():
            entry = Family(
                accession=accession,
                type=entry_type,
                name=name
            )
            self.session.add(entry)
            id_model[name] = entry

        graph = get_interpro_family_tree(force_download=force_download)

        for parent, child in graph.edges_iter():
            id_model[parent].children.append(id_model[child])

        self.session.commit()

    def populate_tree(self):
        raise NotImplementedError

    def populate_protein_membership(self):
        raise NotImplementedError

    def get_family_by_name(self, name):
        """Gets an InterPro family by name, if exists.

        :param str name: The name to search
        :rtype: Optional[Family]
        """
        return self.session.query(Family).filter(Family.name == name).one_or_none()

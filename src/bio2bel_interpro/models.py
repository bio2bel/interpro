# -*- coding: utf-8 -*-

"""InterPro database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import protein

TABLE_PREFIX = 'interpro'
ENTRY_TABLE_NAME = '{}_entry'.format(TABLE_PREFIX)
TYPE_TABLE_NAME = '{}_type'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
ENTRY_PROTEIN_TABLE_NAME = '{}_entry_protein'.format(TABLE_PREFIX)

Base = declarative_base()

entry_protein = Table(
    ENTRY_PROTEIN_TABLE_NAME,
    Base.metadata,
    Column('entry_id', Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True),
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
)


class Type(Base):
    """InterPro Entry Type"""
    __tablename__ = TYPE_TABLE_NAME

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry type')

    def __str__(self):
        return self.name


class Entry(Base):
    """Represents families in InterPro"""
    __tablename__ = ENTRY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    interpro_id = Column(String(255), unique=True, index=True, nullable=False, doc='The InterPro identifier')
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry name')

    type_id = Column(Integer, ForeignKey('{}.id'.format(TYPE_TABLE_NAME)))
    type = relationship('Type', backref=backref('entries'))

    parent_id = Column(Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)))
    children = relationship('Entry', backref=backref('parent', remote_side=[id]))

    proteins = relationship('Protein', secondary=entry_protein, backref=backref('entries'))

    def __str__(self):
        return self.name

    def serialize_to_bel(self):
        """Returns this entry as a PyBEL node data dictionary

        :rtype: dict
        """
        return protein(
            namespace='INTERPRO',
            name=str(self.name),
            identifier=str(self.interpro_id)
        )


class Protein(Base):
    """Represents proteins that are annotated to InterPro families"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    uniprot_id = Column(String(32), nullable=False, index=True, doc='UniProt identifier')

# -*- coding: utf-8 -*-

"""InterPro database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from pybel.dsl import protein

TABLE_PREFIX = 'interpro'
FAMILY_TABLE_NAME = '{}_family'.format(TABLE_PREFIX)
TYPE_TABLE_NAME = '{}_type'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
PROTEIN_FAMILY_TABLE_NAME = '{}_protein_family'.format(TABLE_PREFIX)

Base = declarative_base()

protein_family = Table(
    PROTEIN_FAMILY_TABLE_NAME,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
    Column('family_id', Integer, ForeignKey('{}.id'.format(FAMILY_TABLE_NAME)), primary_key=True)
)


class Type(Base):
    """InterPro Entry Type"""
    __tablename__ = TYPE_TABLE_NAME

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry type')

    def __str__(self):
        return self.name


class Family(Base):
    """Represents families in InterPro"""
    __tablename__ = FAMILY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    interpro_id = Column(String(255), unique=True, index=True, nullable=False, doc='The InterPro identifier')
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry name')

    type_id = Column(Integer, ForeignKey('{}.id'.format(TYPE_TABLE_NAME)))
    type = relationship('Type', backref=backref('families'))

    parent_id = Column(Integer, ForeignKey('{}.id'.format(FAMILY_TABLE_NAME)))

    # parent = relationship('Family', remote_side=[id])

    def __str__(self):
        return self.name

    def serialize_to_bel(self):
        """Returns this entry as a PyBEL node data dictionary

        :rtype: dict
        """
        return protein(namespace='INTERPRO', name=self.name, identifier=self.interpro_id)


class Protein(Base):
    """Represents proteins that are annotated to InterPro families"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    # TODO add fields?

    families = relationship('Family', secondary=protein_family)

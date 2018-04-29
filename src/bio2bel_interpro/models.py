# -*- coding: utf-8 -*-

"""SQLAlchemy database models for Bio2BEL InterPro."""

from pybel.dsl import protein
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

from .constants import MODULE_NAME

ENTRY_TABLE_NAME = '{}_entry'.format(MODULE_NAME)
TYPE_TABLE_NAME = '{}_type'.format(MODULE_NAME)
PROTEIN_TABLE_NAME = '{}_protein'.format(MODULE_NAME)
ENTRY_PROTEIN_TABLE_NAME = '{}_entry_protein'.format(MODULE_NAME)
GO_TABLE_NAME = '{}_go'.format(MODULE_NAME)
ENTRY_GO_TABLE_NAME = '{}_entry_go'.format(MODULE_NAME)

Base = declarative_base()

entry_protein = Table(
    ENTRY_PROTEIN_TABLE_NAME,
    Base.metadata,
    Column('entry_id', Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True),
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
)

entry_go = Table(
    ENTRY_GO_TABLE_NAME,
    Base.metadata,
    Column('entry_id', Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True),
    Column('go_id', Integer, ForeignKey('{}.id'.format(GO_TABLE_NAME)), primary_key=True),
)


class Type(Base):
    """InterPro Entry Type"""
    __tablename__ = TYPE_TABLE_NAME

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry type')

    def __str__(self):
        return self.name


class Protein(Base):
    """Represents proteins that are annotated to InterPro families"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    uniprot_id = Column(String(32), nullable=False, index=True, doc='UniProt identifier')

    def __repr__(self):
        return self.uniprot_id

    def as_bel(self):
        """
        :rtype: pybel.dsl.protein
        """
        return protein(
            namespace='UNIPROT',
            identifier=str(self.uniprot_id)
        )


class GoTerm(Base):
    """Represents a GO term."""

    __tablename__ = GO_TABLE_NAME

    id = Column(Integer, primary_key=True)

    go_id = Column(String(255), unique=True, index=True, nullable=False, doc='Gene Ontology identifier')
    name = Column(String(255), unique=True, index=True, nullable=False, doc='Label')

    def __repr__(self):
        return self.go_id


class Entry(Base):
    """Represents families, domains, etc. in InterPro"""
    __tablename__ = ENTRY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    interpro_id = Column(String(255), unique=True, index=True, nullable=False, doc='The InterPro identifier')
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry name')

    type_id = Column(Integer, ForeignKey('{}.id'.format(TYPE_TABLE_NAME)))
    type = relationship(Type, backref=backref('entries'))

    parent_id = Column(Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)))
    children = relationship('Entry', backref=backref('parent', remote_side=[id]))

    proteins = relationship(Protein, secondary=entry_protein, backref=backref('proteins'))
    go_terms = relationship(GoTerm, secondary=entry_go, backref=backref('go_terms'))

    def __str__(self):
        return self.name

    def as_bel(self):
        """Returns this entry as a PyBEL node data dictionary

        :rtype: pybel.dsl.protein
        """
        return protein(
            namespace='INTERPRO',
            name=str(self.name),
            identifier=str(self.interpro_id)
        )

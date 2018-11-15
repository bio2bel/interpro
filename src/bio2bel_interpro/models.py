# -*- coding: utf-8 -*-

"""SQLAlchemy database models for Bio2BEL InterPro."""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

import pybel.dsl
from .constants import MODULE_NAME

ENTRY_TABLE_NAME = f'{MODULE_NAME}_entry'
TYPE_TABLE_NAME = f'{MODULE_NAME}_type'
PROTEIN_TABLE_NAME = f'{MODULE_NAME}_protein'
ANNOTATION_TABLE_NAME = f'{MODULE_NAME}_annotation'
GO_TABLE_NAME = f'{MODULE_NAME}_go'
ENTRY_GO_TABLE_NAME = f'{MODULE_NAME}_entry_go'

Base = declarative_base()

entry_go = Table(
    ENTRY_GO_TABLE_NAME,
    Base.metadata,
    Column('entry_id', Integer, ForeignKey(f'{ENTRY_TABLE_NAME}.id'), primary_key=True),
    Column('go_id', Integer, ForeignKey(f'{GO_TABLE_NAME}.id'), primary_key=True),
)


class Type(Base):
    """InterPro Entry Type."""

    __tablename__ = TYPE_TABLE_NAME
    id = Column(Integer, primary_key=True)

    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry type')

    def __str__(self):  # noqa: D105
        return self.name


class Protein(Base):
    """Represents proteins that are annotated to InterPro families."""

    __tablename__ = PROTEIN_TABLE_NAME
    id = Column(Integer, primary_key=True)

    uniprot_id = Column(String(32), nullable=False, index=True, doc='UniProt identifier')

    bel_encoding = 'GRP'

    def __repr__(self):  # noqa: D105
        return self.uniprot_id

    def as_bel(self) -> pybel.dsl.protein:
        """Return this protein as a PyBEL node."""
        return pybel.dsl.protein(
            namespace='uniprot',
            identifier=str(self.uniprot_id),
        )


class GoTerm(Base):
    """Represents a GO term."""

    __tablename__ = GO_TABLE_NAME
    id = Column(Integer, primary_key=True)

    go_id = Column(String(255), unique=True, index=True, nullable=False, doc='Gene Ontology identifier')
    name = Column(String(255), unique=True, index=True, nullable=False, doc='Label')

    def __repr__(self):  # noqa: D105
        return self.go_id


class Entry(Base):
    """Represents families, domains, etc. in InterPro."""

    __tablename__ = ENTRY_TABLE_NAME
    id = Column(Integer, primary_key=True)

    interpro_id = Column(String(255), unique=True, index=True, nullable=False, doc='The InterPro identifier')
    name = Column(String(255), nullable=False, unique=True, index=True, doc='The InterPro entry name')

    type_id = Column(Integer, ForeignKey(f'{TYPE_TABLE_NAME}.id'))
    type = relationship(Type, backref=backref('entries'))

    parent_id = Column(Integer, ForeignKey(f'{ENTRY_TABLE_NAME}.id'))
    children = relationship('Entry', backref=backref('parent', remote_side=[id]))

    go_terms = relationship(GoTerm, secondary=entry_go, backref=backref('entries'))

    bel_encoding = 'P'

    def __str__(self):  # noqa: D105
        return self.name

    def as_bel(self) -> pybel.dsl.Protein:
        """Return this InterPro entry as a PyBEL node."""
        return pybel.dsl.protein(
            namespace='interpro',
            name=str(self.name),
            identifier=str(self.interpro_id)
        )


class Annotation(Base):
    """Mapping of InterPro to protein."""

    __tablename__ = ANNOTATION_TABLE_NAME
    id = Column(Integer, primary_key=True)

    entry_id = Column(Integer, ForeignKey(f'{Entry.__tablename__}.id'))
    entry = relationship(Entry, backref=backref('annotations'))

    protein_id = Column(Integer, ForeignKey(f'{Protein.__tablename__}.id'))
    protein = relationship(Protein, backref=backref('annotations'))

    xref = Column(String(255))
    start = Column(Integer, doc='Starting position on reference sequence of annotation')
    end = Column(Integer, doc='Ending position on reference sequence of annotation')

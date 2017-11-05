# -*- coding: utf-8 -*-

"""InterPro database model"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

TABLE_PREFIX = 'interpro'
FAMILY_TABLE_NAME = '{}_family'.format(TABLE_PREFIX)
TREE_TABLE_NAME = '{}_tree'.format(TABLE_PREFIX)
PROTEIN_TABLE_NAME = '{}_protein'.format(TABLE_PREFIX)
PROTEIN_FAMILY_TABLE_NAME = '{}_protein_family'.format(TABLE_PREFIX)

Base = declarative_base()

entry_hierarchy = Table(
    TREE_TABLE_NAME,
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('{}.id'.format(FAMILY_TABLE_NAME)), primary_key=True),
    Column('child_id', Integer, ForeignKey('{}.id'.format(FAMILY_TABLE_NAME)), primary_key=True)
)

protein_family = Table(
    PROTEIN_FAMILY_TABLE_NAME,
    Base.metadata,
    Column('protein_id', Integer, ForeignKey('{}.id'.format(PROTEIN_TABLE_NAME)), primary_key=True),
    Column('family_id', Integer, ForeignKey('{}.id'.format(FAMILY_TABLE_NAME)), primary_key=True)
)


class Family(Base):
    """Represents families in InterPro"""
    __tablename__ = FAMILY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    accession = Column(String(255), doc='The InterPro accession number')
    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    children = relationship(
        'Family',
        secondary=entry_hierarchy,
        primaryjoin=(id == entry_hierarchy.c.parent_id),
        secondaryjoin=(id == entry_hierarchy.c.child_id)
    )


class Protein(Base):
    """Represents proteins that are annotated to InterPro families"""
    __tablename__ = PROTEIN_TABLE_NAME

    id = Column(Integer, primary_key=True)

    # TODO add fields?

    families = relationship('Family', secondary=protein_family)

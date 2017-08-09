# -*- coding: utf-8 -*-

"""Interpro database model"""

from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

TABLE_PREFIX = 'pyinterpro'
ENTRY_TABLE_NAME = '{}_entry'.format(TABLE_PREFIX)
TREE_TABLE_NAME = '{}_tree'.format(TABLE_PREFIX)

Base = declarative_base()

entry_hierarchy = Table(
    TREE_TABLE_NAME,
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True),
    Column('child_id', Integer, ForeignKey('{}.id'.format(ENTRY_TABLE_NAME)), primary_key=True)
)


class Entry(Base):
    """Represents entries in Interpro"""
    __tablename__ = ENTRY_TABLE_NAME

    id = Column(Integer, primary_key=True)

    accession = Column(String(255))
    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    children = relationship(
        'Entry',
        secondary=entry_hierarchy,
        primaryjoin=(id == entry_hierarchy.c.parent_id),
        secondaryjoin=(id == entry_hierarchy.c.child_id)
    )

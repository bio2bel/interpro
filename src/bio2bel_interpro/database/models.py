# -*- coding: utf-8 -*-
"""INTERPRO database model."""

from sqlalchemy import Column, String, Integer, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

entry_hierarchy = Table(
    'tree',
    Base.metadata,
    Column('parent_id', Integer, ForeignKey('interpro.id'), primary_key=True),
    Column('child_id', Integer, ForeignKey('interpro.id'), primary_key=True)
)


class Interpro(Base):
    __tablename__ = 'interpro'
    id = Column(Integer, primary_key=True)
    accession = Column(String(255))
    type = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)

    children = relationship(
        'Interpro',
        secondary=entry_hierarchy,
        primaryjoin=(id == entry_hierarchy.c.parent_id),
        secondaryjoin=(id == entry_hierarchy.c.child_id)
    )

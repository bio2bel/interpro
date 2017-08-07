from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Interpro(Base):
    __tablename__ = 'interpro'
    ENTRY_AC = Column(String(255), primary_key=True)
    ENTRY_TYPE = Column(String(255), nullable=False)
    ENTRY_NAME = Column(String(255), nullable=False)

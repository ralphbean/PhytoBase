from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.types import Integer, Unicode, Boolean

from phytobase.model import DeclarativeBase, metadata, DBSession

__all__ = [ 'Molecules_type' ]

class Molecules_type(DeclarativeBase):

    __tablename__ = 'molecules_type'

    id = Column(Integer, autoincrement=True,primary_key=True)
    description = Column(Unicode, nullable=True)
    def __repr__(self):
        return (u"<Molecule_type('%s')>" % (
            self.description
        )).encode('utf-8')

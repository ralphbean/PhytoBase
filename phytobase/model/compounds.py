from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.types import Integer, Unicode, Boolean

from phytobase.model import DeclarativeBase, metadata, DBSession

__all__ = [ 'Compound' ]

class Compound(DeclarativeBase):

    __tablename__ = 'compound'

    id = Column(Integer, autoincrement=True,primary_key=True)
    code = Column(Unicode,nullable=False)
    title = Column(Unicode, nullable=True)
    description = Column(Unicode, nullable=True)
    add_date = Column(DateTime,nullable=True)
    comment = Column(Unicode, nullable=True)
    mass = Column(Numeric, nullable=True)
    mass_left = Column(Numeric, nullable=True)
    def __repr__(self):
        return (u"<Compound('%s','%f')>" % (
            self.code, self.mass_left
        )).encode('utf-8')

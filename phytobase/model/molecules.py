from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy.types import Integer, Unicode, Boolean

from phytobase.model import DeclarativeBase, metadata, DBSession

__all__ = [ 'Molecule' ]

class Molecule(DeclarativeBase):

    __tablename__ = 'molecule'

    id = Column(Integer, autoincrement=True,primary_key=True)
    code = Column(Unicode,nullable=False)
    type_id = Column(Integer,ForeignKey('molecules_type.id'),nullable=True)
    type = relation('Molecules_type',foreign_keys=type_id)
    title = Column(Unicode, nullable=True)
    description = Column(Unicode, nullable=True)
    smiles = Column(Unicode, nullable=True)
    inchi = Column(Unicode, nullable=True)
    add_date = Column(DateTime,nullable=True)
    comment = Column(Unicode, nullable=True)
    def __repr__(self):
        return (u"<Molecule('%s','%s')>" % (
            self.code, self.title
        )).encode('utf-8')

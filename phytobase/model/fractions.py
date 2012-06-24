from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, relationship,dynamic
from sqlalchemy.types import Integer, Unicode, Boolean


from phytobase.model import DeclarativeBase, metadata, DBSession

__all__ = [ 'Fraction' ]


owner_fraction = Table('owner_fraction', metadata,
                      Column('owner_id', Integer, ForeignKey('tg_user.user_id')),
                      Column('fraction_id', Integer, ForeignKey('fraction.id'))
)


class Fraction(DeclarativeBase):

    __tablename__ = 'fraction'

    id = Column(Integer,autoincrement=True, primary_key=True)
    code = Column(Unicode,nullable=False)

    title = Column(Unicode, nullable=True)
    description = Column(Unicode, nullable=True)
    add_date = Column(DateTime,nullable=True)
    comment = Column(Unicode, nullable=True)
    mass = Column(Numeric, nullable=True)
    mass_left = Column(Numeric, nullable=True)
    owner = relation('User', secondary=owner_fraction, backref=backref('fractions'))

    def __repr__(self):
        return (u"<Fraction('%s')>" % (
            self.code
        )).encode('utf-8')
    def __unicode__(self):
        return(self.code)

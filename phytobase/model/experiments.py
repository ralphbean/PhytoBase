from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, relationship,dynamic
from sqlalchemy.types import Integer, Unicode, Boolean

from phytobase.model import DeclarativeBase, metadata, DBSession


__all__ = ['Experiment' ]
experiment_fraction = Table('experiment_fraction', metadata,
                      Column('experiment_id', Integer, ForeignKey('experiment.id')),
                      Column('fraction_id', Integer, ForeignKey('fraction.id'))
)
owner_experiment = Table('owner_experiment', metadata,
                      Column('owner_id', Integer, ForeignKey('tg_user.user_id')),
                      Column('experiment_id', Integer, ForeignKey('experiment.id'))
)

class Experiment(DeclarativeBase):

    __tablename__ = 'experiment'

    id = Column(Integer, autoincrement=True,primary_key=True)
    code = Column(Unicode,nullable=False,unique=True)

    title = Column(Unicode, nullable=True)
    description = Column(Unicode, nullable=True)
    add_date = Column(DateTime,nullable=True)
    comment = Column(Unicode, nullable=True)

    fractions = relation('Fraction', secondary=experiment_fraction, backref=backref('experiments'))
    owner = relation('User', secondary=owner_experiment, backref=backref('experiments'))

    def __repr__(self):
        return (u"<Experiment('%s')>" % (
            self.code
        )).encode('utf-8')
    def __unicode__(self):
        return(self.code)

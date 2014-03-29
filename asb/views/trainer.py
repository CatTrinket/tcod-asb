from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import TrainerIndex

@view_config(context=TrainerIndex, renderer='/indices/trainers.mako')
def trainer_index(context, request):
    """The index of all the trainers in the league."""

    trainers = (
        db.DBSession.query(db.Trainer)
        .filter_by(unclaimed_from_hack=False)
        .order_by(db.Trainer.name)
        .all()
    )

    return {'trainers': trainers}

@view_config(context=db.Trainer, renderer='/trainer.mako')
def trainer(context, request):
    """A trainer's info page."""

    return {'trainer': context}

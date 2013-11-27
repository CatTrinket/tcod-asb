from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models
from asb.resources import TrainerIndex
from asb.views.redirect import attempt_redirect

@view_config(context=TrainerIndex, renderer='/indices/trainers.mako')
def TrainerIndex(context, request):
    """The index of all the trainers in the league."""

    trainers = (
        models.DBSession.query(models.Trainer)
        .filter_by(unclaimed_from_hack=False)
        .order_by(models.Trainer.name)
        .all()
    )

    return {'trainers': trainers}

@view_config(context=models.Trainer, renderer='/trainer.mako')
def Trainer(context, request):
    """A trainer's info page."""

    return {'trainer': context}

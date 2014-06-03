from pyramid.view import view_config
import sqlalchemy as sqla
import sqlalchemy.orm

from asb import db
from asb.resources import TrainerIndex

@view_config(context=TrainerIndex, renderer='/indices/trainers.mako')
def trainer_index(context, request):
    """The index of all the trainers in the league."""

    pokemon_count = (
        db.DBSession.query(db.Pokemon.trainer_id, sqla.func.count('*')
            .label('count'))
        .select_from(db.Pokemon)
        .group_by(db.Pokemon.trainer_id)
        .subquery()
    )

    trainers = (
        db.DBSession.query(db.Trainer, pokemon_count.c.count)
        .select_from(db.Trainer)
        .join(pokemon_count, pokemon_count.c.trainer_id == db.Trainer.id)
        .options(sqla.orm.subqueryload('squad'))
        .filter(db.Trainer.unclaimed_from_hack == False)
        .order_by(db.Trainer.name)
        .all()
    )

    return {'trainers': trainers}

@view_config(context=db.Trainer, renderer='/trainer.mako')
def trainer(context, request):
    """A trainer's info page."""

    return {'trainer': context}

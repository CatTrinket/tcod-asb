import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models
from asb.resources import MoveIndex

@view_config(context=MoveIndex, renderer='/indices/moves.mako')
def move_index(context, request):
    """The index of all the moves."""

    moves = (
        models.DBSession.query(models.Move)
        .order_by(models.Move.name)
        .all()
    )

    return {'moves': moves}

@view_config(context=models.Move, renderer='/move.mako')
def move(move, request):
    """A move's dex page."""

    pokemon = (
        models.DBSession.query(models.PokemonForm)
        .join(models.PokemonSpecies)
        .filter(models.PokemonForm.moves.any(models.Move.id == move.id))
        .filter(or_(models.PokemonSpecies.forms_are_squashable == False,
                    models.PokemonForm.is_default == True))
        .order_by(models.PokemonForm.order)
    )

    return {'move': move, 'pokemon': pokemon}

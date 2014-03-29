import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import MoveIndex

@view_config(context=MoveIndex, renderer='/indices/moves.mako')
def move_index(context, request):
    """The index of all the moves."""

    moves = (
        db.DBSession.query(db.Move)
        .order_by(db.Move.name)
        .all()
    )

    return {'moves': moves}

@view_config(context=db.Move, renderer='/move.mako')
def move(move, request):
    """A move's dex page."""

    pokemon = (
        db.DBSession.query(db.PokemonForm)
        .join(db.PokemonSpecies)
        .filter(db.PokemonForm.moves.any(db.Move.id == move.id))
        .filter(or_(db.PokemonSpecies.forms_are_squashable == False,
                    db.PokemonForm.is_default == True))
        .order_by(db.PokemonForm.order)
    )

    return {'move': move, 'pokemon': pokemon}

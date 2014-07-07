import itertools

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload, subqueryload_all
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import MoveIndex

@view_config(context=MoveIndex, name='contests',
  renderer='/indices/contest_moves.mako')
def contest_move_index(context, request):
    """An alternate move index, displaying contest data instead of battle
    data.
    """

    supercategories = (
        db.DBSession.query(db.ContestSupercategory)
        .order_by(db.ContestSupercategory.id)
        .options(subqueryload_all('categories.moves'))
        .all()
    )

    pure_points_moves = (
        db.DBSession.query(db.Move)
        .join(db.ContestCategory)
        .filter(db.ContestCategory.identifier == 'pure-points')
        .order_by(db.Move.appeal.desc(), db.Move.jam, db.Move.name)
        .all()
    )

    pure_points_moves = itertools.groupby(pure_points_moves,
        lambda move: (move.appeal, move.jam))

    return {'supercategories': supercategories,
        'pure_points_moves': pure_points_moves}

@view_config(context=MoveIndex, renderer='/indices/moves.mako')
def move_index(context, request):
    """The index of all the moves."""

    moves = (
        db.DBSession.query(db.Move)
        .order_by(db.Move.name)
        .options(joinedload('type'), joinedload('damage_class'))
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
        .options(
            joinedload('species'),
            subqueryload('types'),
            subqueryload('abilities'),
            joinedload('abilities.ability')
        )
        .order_by(db.PokemonForm.order)
    )

    return {'move': move, 'pokemon': pokemon}

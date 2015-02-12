import itertools

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload, subqueryload_all
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import MoveIndex
from asb.views.type import attacking_labels, empty_matchup_dict

def type_matchups(move):
    """Figure out a move's type matchups."""

    # Figure out special cases
    if move.damage_class.identifier == 'non-damaging':
        return None
    elif move.identifier == 'flying-press':
        return flying_press_matchups(move)
    elif any(cat.identifier == 'exact-damage' for cat in move.categories):
        return specific_damage_matchups(move)

    # Go through and group the matchups
    matchups = empty_matchup_dict()

    for matchup in move.type.attacking_matchups:
        result = matchup.result.identifier
        type_ = matchup.defending_type

        if move.identifier == 'freeze-dry' and type_.identifier == 'water':
            # Deal with Freeze-Dry
            matchups['super-effective'].append(type_)
        elif result != 'neutral':
            # Ignore neutral matchups
            matchups[result].append(type_)

    return matchups

def flying_press_matchups(move):
    """Figure out Flying Press's type matchups."""

    matchups = empty_matchup_dict()

    fighting = move.type
    flying = db.DBSession.query(db.Type).filter_by(identifier='flying').one()

    zipped_matchups = zip(fighting.attacking_matchups,
                          flying.attacking_matchups)

    for matchup_pair in zipped_matchups:
        # Go through both matchups for each defending type
        result_n = 0

        for matchup in matchup_pair:
            result = matchup.result.identifier
            if result == 'super-effective':
                result_n += 1
            elif result == 'not-very-effective':
                result_n -= 1
            elif result == 'ineffective':
                matchups['ineffective'].append(matchup.defending_type)
                break

        # No type is weak or resistant to both Flying and Fighting, so we don't
        # have to worry about that, thankfully.
        if result_n == 1:
            matchups['super-effective'].append(matchup.defending_type)
        elif result_n == -1:
            matchups['not-very-effective'].append(matchup.defending_type)

    return matchups

def specific_damage_matchups(move):
    """Figure out the matchups that matter (immunities) for moves that deal
    specific damage.
    """

    return {
        'ineffective': [
            matchup.defending_type
            for matchup in move.type.attacking_matchups
            if matchup.result.identifier == 'ineffective'
        ]
    }

relevant_move_categories = {
    'gravity': 'airborne'
}

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

    matchups = type_matchups(move)

    move_category = relevant_move_categories.get(move.identifier)

    if move_category is not None:
        move_category = (
            db.DBSession.query(db.MoveCategory)
            .filter_by(identifier=move_category)
            .options(joinedload('moves'))
            .one()
        )

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

    return {
        'move': move,
        'matchups': matchups,
        'matchup_labels': attacking_labels,
        'move_category': move_category,
        'pokemon': pokemon
    }

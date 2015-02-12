import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import AbilityIndex

relevant_move_categories = {
    'iron-fist': 'punching',
    'strong-jaw': 'biting',
    'mega-launcher': 'pulse',
    'soundproof': 'sound',
    'bulletproof': 'ballistics',
    'aroma-veil': 'mental',
    'overcoat': 'powder',
}

@view_config(context=AbilityIndex, renderer='/indices/abilities.mako')
def ability_index(context, request):
    """The index of all the different abilities."""

    abilities = (
        db.DBSession.query(db.Ability)
        .order_by(db.Ability.name)
        .all()
    )

    return {'abilities': abilities}

@view_config(context=db.Ability, renderer='/ability.mako')
def ability(ability, request):
    """An ability's dex page."""

    stuff = {'ability': ability}

    # Fetch relevant move category, if any
    move_category = relevant_move_categories.get(ability.identifier)
    print(move_category, end=' hi' * 200)
    if move_category is not None:
        move_category = (
            db.DBSession.query(db.MoveCategory)
            .filter_by(identifier=move_category)
            .options(subqueryload('moves'))
            .one()
        )

    stuff['move_category'] = move_category

    # Pokémon who get this ability
    pokemon_base_query = (
        db.DBSession.query(db.PokemonForm)
        .join(db.PokemonSpecies)
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

    # Pokémon who get this as one of their normal abilities
    stuff['normal_pokemon'] = (
        pokemon_base_query.filter(
            db.PokemonForm.abilities.any(and_(
                db.PokemonFormAbility.ability_id == ability.id,
                db.PokemonFormAbility.is_hidden == False
            ))
        )
        .all()
    )

    # Pokémon who ONLY get this ability as a hidden ability
    stuff['hidden_pokemon'] = (
        pokemon_base_query.filter(
            db.PokemonForm.abilities.any(and_(
                db.PokemonFormAbility.ability_id == ability.id,
                db.PokemonFormAbility.is_hidden == True
            )),
            ~db.PokemonForm.abilities.any(and_(
                db.PokemonFormAbility.ability_id == ability.id,
                db.PokemonFormAbility.is_hidden == False
            ))
        )
        .all()
    )

    return stuff

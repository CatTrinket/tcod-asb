import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import AbilityIndex

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

    pokemon_base_query = (
        db.DBSession.query(db.PokemonForm)
        .join(db.PokemonSpecies)
        .filter(or_(db.PokemonSpecies.forms_are_squashable == False,
                    db.PokemonForm.is_default == True))
        .order_by(db.PokemonForm.order)
    )

    normal_pokemon = pokemon_base_query.filter(
        db.PokemonForm.abilities.any(and_(
            db.PokemonFormAbility.ability_id == ability.id,
            db.PokemonFormAbility.is_hidden == False
        ))
    ).all()

    # Pokémon who ONLY get this ability as a hidden ability
    hidden_pokemon = pokemon_base_query.filter(
        db.PokemonForm.abilities.any(and_(
            db.PokemonFormAbility.ability_id == ability.id,
            db.PokemonFormAbility.is_hidden == True
        )),
        ~db.PokemonForm.abilities.any(and_(
            db.PokemonFormAbility.ability_id == ability.id,
            db.PokemonFormAbility.is_hidden == False
        ))
    ).all()

    return {'ability': ability, 'normal_pokemon': normal_pokemon,
        'hidden_pokemon': hidden_pokemon}

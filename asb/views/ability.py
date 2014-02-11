import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import and_, or_
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models
from asb.resources import AbilityIndex

@view_config(context=AbilityIndex, renderer='/indices/abilities.mako')
def ability_index(context, request):
    """The index of all the different abilities."""

    abilities = (
        models.DBSession.query(models.Ability)
        .order_by(models.Ability.name)
        .all()
    )

    return {'abilities': abilities}

@view_config(context=models.Ability, renderer='/ability.mako')
def ability(ability, request):
    """An ability's dex page."""

    pokemon_base_query = (
        models.DBSession.query(models.PokemonForm)
        .join(models.PokemonSpecies)
        .filter(or_(models.PokemonSpecies.forms_are_squashable == False,
                    models.PokemonForm.is_default == True))
        .order_by(models.PokemonForm.order)
    )

    normal_pokemon = pokemon_base_query.filter(
        models.PokemonForm.abilities.any(and_(
            models.PokemonFormAbility.ability_id == ability.id,
            models.PokemonFormAbility.is_hidden == False
        ))
    ).all()

    # Pokémon who ONLY get this ability as a hidden ability
    hidden_pokemon = pokemon_base_query.filter(
        models.PokemonForm.abilities.any(and_(
            models.PokemonFormAbility.ability_id == ability.id,
            models.PokemonFormAbility.is_hidden == True
        )),
        ~models.PokemonForm.abilities.any(and_(
            models.PokemonFormAbility.ability_id == ability.id,
            models.PokemonFormAbility.is_hidden == False
        ))
    ).all()

    return {'ability': ability, 'normal_pokemon': normal_pokemon,
        'hidden_pokemon': hidden_pokemon}

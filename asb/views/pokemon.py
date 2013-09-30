import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models
from asb.views.redirect import attempt_redirect

@view_config(route_name='pokemon_index', renderer='/indices/pokemon.mako')
def PokemonIndex(context, request):
    pokemon = (
        models.DBSession.query(models.Pokemon)
        .order_by(models.Pokemon.id)
        .all()
    )

    return {'pokemon': pokemon}

@view_config(route_name='pokemon', renderer='/pokemon.mako')
def Pokemon(context, request):
    try:
        pokemon = (
            models.DBSession.query(models.Pokemon)
            .filter_by(identifier=request.matchdict['identifier'])
            .one()
        )
    except NoResultFound:
        attempt_redirect(request.matchdict['identifier'],
            models.Pokemon, request)

    return {'pokemon': pokemon}

@view_config(route_name='pokemon_species_index',
             renderer='/indices/pokemon_species.mako')
def PokemonSpeciesIndex(context, request):
    pokemon = (
        models.DBSession.query(models.PokemonSpecies)
        .order_by(models.PokemonSpecies.id)
        .all()
    )

    return {'pokemon': pokemon}

@view_config(route_name='pokemon_species', renderer='/pokemon_species.mako')
def PokemonSpecies(context, request):
    pokemon = (
        models.DBSession.query(models.PokemonSpecies)
        .filter_by(identifier=request.matchdict['identifier'])
        .one()
    )

    return {'pokemon': pokemon}

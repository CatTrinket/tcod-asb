from pyramid.view import view_config

import asb.models as models

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
    pokemon = (
        models.DBSession.query(models.Pokemon)
        .filter_by(id=request.matchdict['id'])
        .one()
    )

    return {'pokemon': pokemon}

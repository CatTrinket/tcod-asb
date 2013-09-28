from pyramid.view import view_config

import asb.models as models

@view_config(route_name='pokemon', renderer='/pokemon.mako')
def Pokemon(context, request):
    pokemon = (
        models.DBSession.query(models.Pokemon)
        .filter_by(id=request.matchdict['id'])
        .one()
    )

    return {'pokemon': pokemon}

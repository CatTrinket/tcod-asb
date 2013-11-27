import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

import asb.models as models

@view_config(route_name='ability_index', renderer='/indices/abilities.mako')
def AbilityIndex(context, request):
    """The index of all the different abilities."""

    abilities = (
        models.DBSession.query(models.Ability)
        .order_by(models.Ability.name)
        .all()
    )

    return {'abilities': abilities}

@view_config(route_name='ability', renderer='/ability.mako')
def Ability(context, request):
    """An ability's dex page."""

    try:
        ability = (
            models.DBSession.query(models.Ability)
            .filter_by(identifier=request.matchdict['identifier'])
            .one()
        )
    except NoResultFound:
        raise httpexc.HTTPNotFound

    return {'ability': ability}

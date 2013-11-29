import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
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
def ability(context, request):
    """An ability's dex page."""

    return {'ability': context}

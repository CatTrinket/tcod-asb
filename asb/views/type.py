import collections

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload, subqueryload_all
from sqlalchemy.orm.exc import NoResultFound

from asb import db
from asb.resources import TypeIndex

def empty_matchup_dict():
    return collections.OrderedDict([
        ('super-effective', []),
        ('not-very-effective', []),
        ('ineffective', [])
    ])

attacking_labels = {
    'super-effective': 'Super effective vs',
    'not-very-effective': 'Not very effective vs',
    'ineffective': 'Ineffective vs'
}

defending_labels = {
    'super-effective': 'Weak to',
    'not-very-effective': 'Resistant to',
    'ineffective': 'Immune to'
}

@view_config(context=TypeIndex, renderer='/indices/types.mako')
def type_index(context, request):
    """The index of all the types, featuring a type chart."""

    return {'types': db.DBSession.query(db.Type).order_by(db.Type.id).all()}

@view_config(context=db.Type, renderer='/type.mako')
def type_(context, request):
    """A type's dex page."""

    stuff = {
        'type': context,
        'attacking_matchups': empty_matchup_dict(),
        'defending_matchups': empty_matchup_dict(),
        'attacking_labels': attacking_labels,
        'defending_labels': defending_labels
    }

    for matchup in context.attacking_matchups:
        result = matchup.result.identifier
        if result != 'neutral':
            stuff['attacking_matchups'][result].append(matchup.defending_type)

    for matchup in context.defending_matchups:
        result = matchup.result.identifier
        if result != 'neutral':
            stuff['defending_matchups'][result].append(matchup.attacking_type)

    stuff['pokemon'] = (
        db.DBSession.query(db.PokemonForm)
        .join(db.PokemonSpecies)
        .filter(db.PokemonForm.types.any(db.Type.id == context.id))
        .filter(or_(db.PokemonSpecies.forms_are_squashable == False,
                    db.PokemonForm.is_default == True,
                    db.PokemonSpecies.identifier == 'arceus'))
        .options(
            joinedload('species'),
            subqueryload('types'),
            subqueryload('abilities'),
            joinedload('abilities.ability')
        )
        .order_by(db.PokemonForm.order)
    )

    return stuff

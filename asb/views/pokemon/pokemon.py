from pyramid.view import view_config
import sqlalchemy as sqla

from . import can_evolve, can_potentially_evolve_into
from asb import db
from asb.resources import PokemonIndex


@view_config(context=PokemonIndex, renderer='/indices/pokemon.mako')
def pokemon_index(context, request):
    """The index page for everyone's Pokémon."""

    pokemon = (
        db.DBSession.query(db.Pokemon)
        .filter(db.Pokemon.is_active())
        .join(db.PokemonForm, db.PokemonSpecies)
        .options(
            sqla.orm.joinedload('gender'),
            sqla.orm.joinedload('trainer'),
            sqla.orm.joinedload('form'),
            sqla.orm.joinedload('form.species'),
            sqla.orm.joinedload('ability'),
            sqla.orm.joinedload('item')
        )
    )

    show_all = request.GET.get('show-all')

    if show_all:
        pokemon = pokemon.order_by(
            db.PokemonSpecies.order, db.PokemonSpecies.name
        ).all()
        count = len(pokemon)
    else:
        pokemon = pokemon.order_by(db.Pokemon.id.desc()).limit(100).all()
        count = db.DBSession.query(db.Pokemon).count()

    return {'pokemon': pokemon, 'count': count, 'show_all': show_all}

@view_config(context=db.Pokemon, renderer='/pokemon.mako')
def pokemon(pokemon, request):
    """An individual Pokémon's info page."""

    evo_info = {}

    for evo_species in pokemon.species.evolutions:
        for evo_form in evo_species.forms:
            if can_potentially_evolve_into(pokemon, evo_form):
                method = evo_form.evolution_method

                if method is None:
                    continue

                if method.happiness:
                    evo_info['happiness'] = method.happiness

                if method.experience:
                    evo_info['experience'] = method.experience

    return {'pokemon': pokemon, 'can_evolve': can_evolve(pokemon),
            'evo_info': evo_info}

@view_config(name='sigstuff', context=db.Pokemon, renderer='/sig_stuff.mako')
def sig_stuff(pokemon, request):
    """A page for viewing a Pokémon's body modification and move modification,
    if any.
    """

    return {'pokemon': pokemon, 'movemod': pokemon.move_modification,
        'bodmod': pokemon.body_modification}

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

from . import can_evolve_into
from asb import db
import asb.forms

class PokemonEvolutionForm(asb.forms.CSRFTokenForm):
    """A form for evolving a Pokémon.

    The choices for the evolution field must be added dynamically.
    """

    evolution = wtforms.RadioField(coerce=int)
    submit = wtforms.SubmitField('Confirm')

def get_evolutions(pokemon):
    """Return all the Pokémon forms that this Pokémon can evolve into."""

    evo_forms = []  # Each element will be (form, needs_buying, needs_item)

    for species in pokemon.species.evolutions:
        for form in species.forms:
            (can_evolve, buy, item) = can_evolve_into(pokemon, form)

            if can_evolve:
                evo_forms.append((form, buy, item))

    return evo_forms

@view_config(name='evolve', context=db.Pokemon, permission='edit.evolve',
  request_method='GET', renderer='evolve_pokemon.mako')
def evolve_pokemon(pokemon, request):
    """A page for evolving a Pokémon."""

    evolutions = get_evolutions(pokemon)

    if not evolutions:
        raise httpexc.HTTPForbidden(
            "This Pokémon can't evolve (or at least not yet)!")

    form = PokemonEvolutionForm(csrf_context=request.session)
    form.evolution.choices = [(evo.id, evo.name) for evo, buy, item in
        evolutions]

    return {'pokemon': pokemon, 'evolutions': evolutions, 'form': form}

@view_config(name='evolve', context=db.Pokemon, permission='edit.evolve',
  request_method='POST', renderer='evolve_pokemon.mako')
def evolve_pokemon_commit(pokemon, request):
    """Evolve a Pokémon."""

    # Make sure this evolution is actually valid, and if not, either return
    # 403 or send them back to the evolution form as appropriate
    evolutions = get_evolutions(pokemon)

    if not evolutions:
        raise httpexc.HTTPForbidden(
            "This Pokémon can't evolve (or at least not yet)!")

    form = PokemonEvolutionForm(request.POST, csrf_context=request.session)
    form.evolution.choices = [(evo.id, evo.name) for evo, buy, item in
        evolutions]

    if not form.validate():
        return {'pokemon': pokemon, 'evolutions': evolutions, 'form': form}

    # Get the right evolution
    for evo, buy, item in evolutions:
        if evo.id == form.evolution.data:
            # evo, buy, and item are already set thanks to the loop
            break

    # Make sure it's holding the right item, and take it away if so
    if item:
        if (pokemon.trainer_item is None or pokemon.trainer_item.item_id !=
          evo.species.evolution_method.item_id):
            # Not holding the right item; back to the form after all
            form.evolution.errors.append(
                '{} must be holding the right item.'.format(pokemon.name))
            return {'pokemon': pokemon, 'evolutions': evolutions, 'form': form}
        else:
            db.DBSession.delete(pokemon.trainer_item)

    # Take money if appropriate
    if buy:
        pokemon.trainer.money -= evo.species.evolution_method.buyable_price

    # If it's not nicknamed, we'll need to update its name
    not_nicknamed = pokemon.name == pokemon.species.name

    # POOF
    pokemon.pokemon_form_id = form.evolution.data

    # Do the name thing
    if not_nicknamed:
        pokemon.name = pokemon.species.name

    # We're done here
    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

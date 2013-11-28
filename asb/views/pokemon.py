import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
import transaction
import wtforms
import wtforms.ext.csrf

import asb.models as models
from asb.resources import PokemonIndex, SpeciesIndex
from asb.views.redirect import attempt_redirect

class EditPokemonForm(wtforms.ext.csrf.SecureForm):
    name = wtforms.TextField('Name')
    save = wtforms.SubmitField('Save')

    def generate_csrf_token(self, session):
        return session.get_csrf_token()

    def validate_csrf_token(form, field):
        if field.data != field.current_token:
            raise wtforms.validators.ValidationError('Invalid CSRF token')

@view_config(context=PokemonIndex, renderer='/indices/pokemon.mako')
def PokemonIndex(context, request):
    """The index page for everyone's Pokémon."""

    pokemon = (
        models.DBSession.query(models.Pokemon)
        .join(models.Pokemon.trainer)
        .filter_by(unclaimed_from_hack=False)
        .order_by(models.Pokemon.pokemon_form_id, models.Pokemon.name)
        .options(
            joinedload('gender'),
            joinedload('trainer'),
            joinedload('form'),
            joinedload('form.species'),
            joinedload('ability'),
            joinedload('item')
        )
        .all()
    )

    return {'pokemon': pokemon}

@view_config(context=models.Pokemon, renderer='/pokemon.mako')
def Pokemon(context, request):
    """An individual Pokémon's info page."""

    return {'pokemon': context}

@view_config(name='edit', context=models.Pokemon, permission='edit:basics',
  request_method='GET', renderer='edit_pokemon.mako')
def EditPokemon(pokemon, request):
    form = EditPokemonForm(csrf_context=request.session)
    form.name.data = pokemon.name

    return {'pokemon': pokemon, 'form': form}

@view_config(name='edit', context=models.Pokemon, permission='edit:basics',
  request_method='POST', renderer='edit_pokemon.mako')
def EditPokemonCommit(pokemon, request):
    form = EditPokemonForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    pokemon.name = form.name.data
    pokemon.update_identifier()
    models.DBSession.flush()

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

@view_config(context=SpeciesIndex, renderer='/indices/pokemon_species.mako')
def PokemonSpeciesIndex(context, request):
    """The index page for all the species of Pokémon."""

    pokemon = (
        models.DBSession.query(models.PokemonSpecies)
        .order_by(models.PokemonSpecies.id)
        .all()
    )

    return {'pokemon': pokemon}

@view_config(context=models.PokemonForm, renderer='/pokemon_species.mako')
def PokemonSpecies(context, request):
    """The dex page of a Pokémon species.

    Under the hood, this is actually the dex page for a form.  But it's clearer
    to present it as the page for a species and pretend the particular form is
    just a detail.
    """

    return {'pokemon': context}

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

from . import check_form_condition
from asb import db
import asb.forms


class EditPokemonForm(asb.forms.CSRFTokenForm):
    """A form for editing a Pokémon."""

    name = wtforms.TextField('Name', [asb.forms.name_validator])
    form = wtforms.SelectField(coerce=int)
    save = wtforms.SubmitField('Save')


def add_form_choices(form, pokemon):
    """Figure out what forms this Pokémon can switch between, and add choices
    to the "form" dropdown accordingly, or delete it if it's unnecessary.
    """

    if pokemon.species.can_switch_forms or pokemon.form_uncertain:
        form.form.choices = [
            (form.id, form.form_name)
            for form in pokemon.species.forms
            if check_form_condition(pokemon, form)
        ]

        form.form.data = pokemon.pokemon_form_id
        
    if form.form.choices is None or len(form.form.choices) <= 1:
        del form.form


@view_config(name='edit', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='edit_pokemon.mako')
def edit_pokemon(pokemon, request):
    """A page for editing a Pokémon."""

    form = EditPokemonForm(csrf_context=request.session)
    form.name.data = pokemon.name

    # Figure out what forms this Pokémon can switch between
    if pokemon.species.can_switch_forms or pokemon.form_uncertain:
        form.form.choices = [
            (form.id, form.form_name)
            for form in pokemon.species.forms
            if check_form_condition(pokemon, form)
        ]

        form.form.data = pokemon.pokemon_form_id

    if form.form.choices is None or len(form.form.choices) <= 1:
        del form.form

    return {'pokemon': pokemon, 'form': form}

@view_config(name='edit', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='edit_pokemon.mako')
def edit_pokemon_commit(pokemon, request):
    """Process a request to edit a Pokémon."""

    form = EditPokemonForm(request.POST, csrf_context=request.session)

    # Figure out what forms this Pokémon can switch between
    if pokemon.species.can_switch_forms or pokemon.form_uncertain:
        form.form.choices = [
            (form.id, form.form_name)
            for form in pokemon.species.forms
            if check_form_condition(pokemon, form)
        ]

    if form.form.choices is None or len(form.form.choices) <= 1:
        del form.form

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    pokemon.name = form.name.data or pokemon.species.name
    pokemon.update_identifier()

    if form.form is not None:
        pokemon.pokemon_form_id = form.form.data
        pokemon.form_uncertain = False

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

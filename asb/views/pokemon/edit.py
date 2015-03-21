import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

from . import check_form_condition
from asb import db
import asb.forms


class EditPokemonForm(asb.forms.CSRFTokenForm):
    """A form for editing a Pokémon."""

    name = wtforms.TextField('Name', [asb.forms.name_validator])
    form = wtforms.SelectField(coerce=int)
    save = wtforms.SubmitField('Save')

    def add_form_choices(self, pokemon):
        """Figure out what forms this Pokémon can switch between, and add choices
        to the "form" dropdown accordingly, or delete it if it's unnecessary.
        """

        if pokemon.species.can_switch_forms or pokemon.form_uncertain:
            self.form.choices = [
                (form.id, form.form_name)
                for form in pokemon.species.forms
                if check_form_condition(pokemon, form)
            ]

            if self.form.data is None:
                self.form.data = pokemon.pokemon_form_id

        if self.form.choices is None or len(self.form.choices) <= 1:
            del self.form

class SuperEditPokemonForm(asb.forms.CSRFTokenForm):
    """A form for editing things about a Pokémon that only admins can edit."""

    experience = wtforms.IntegerField('Experience')
    happiness = wtforms.IntegerField('Happiness')
    unlocked_evolutions = asb.forms.MultiCheckboxField('Unlockable evos',
        coerce=int)
    give_to = wtforms.StringField('Give to')
    save = wtforms.SubmitField('Save')

    trainer = None

    def add_evolution_choices(self, pokemon):
        """Set the choices for unlocked_evolutions.  Only item and trade evos
        are unlockable.
        """

        choices = [
            (evo.id, evo.name)
            for evo in pokemon.species.evolutions
            if evo.evolution_method.item_id is not None or
                evo.evolution_method.can_trade_instead
        ]

        if choices:
            self.unlocked_evolutions.choices = choices

            if self.unlocked_evolutions.data is None:
                self.unlocked_evolutions.data = (
                    [evo.id for evo in pokemon.unlocked_evolutions])
        else:
            del self.unlocked_evolutions

    def validate_give_to(form, field):
        """Fetch the named trainer from the database; raise a validation error
        if they're not found.
        """

        try:
            form.trainer = (
                db.DBSession.query(db.Trainer)
                .filter(sqla.func.lower(db.Trainer.name) == field.data.lower())
                .one()
            )
        except sqla.orm.exc.NoResultFound:
            raise wtforms.validators.ValidationError('Unknown trainer')

@view_config(name='edit', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='edit_pokemon.mako')
def edit_pokemon(pokemon, request):
    """A page for editing a Pokémon."""

    form = EditPokemonForm(csrf_context=request.session)
    form.name.data = pokemon.name
    form.add_form_choices(pokemon)

    return {'pokemon': pokemon, 'form': form}

@view_config(name='edit', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='edit_pokemon.mako')
def edit_pokemon_commit(pokemon, request):
    """Process a request to edit a Pokémon."""

    form = EditPokemonForm(request.POST, csrf_context=request.session)
    form.add_form_choices(pokemon)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    pokemon.name = form.name.data.strip() or pokemon.species.name
    pokemon.update_identifier()

    if form.form is not None:
        pokemon.pokemon_form_id = form.form.data
        pokemon.form_uncertain = False

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

@view_config(name='super-edit', context=db.Pokemon, request_method='GET',
  permission='edit.everything', renderer='super_edit_pokemon.mako')
def super_edit(pokemon, request):
    """A page for editing stuff that only admins can edit."""

    form = SuperEditPokemonForm(csrf_context=request.session)
    form.add_evolution_choices(pokemon)
    form.experience.data = pokemon.experience
    form.happiness.data = pokemon.happiness

    return {'form': form, 'pokemon': pokemon}

@view_config(name='super-edit', context=db.Pokemon, request_method='POST',
  permission='edit.everything', renderer='super_edit_pokemon.mako')
def super_edit_commit(pokemon, request):
    """Process a request to super-edit a Pokémon."""

    form = SuperEditPokemonForm(request.POST, csrf_context=request.session)
    form.add_evolution_choices(pokemon)

    if not form.validate():
        return {'form': form, 'pokemon': pokemon}

    pokemon.experience = form.experience.data
    pokemon.happiness = form.happiness.data

    if form.unlocked_evolutions is not None:
        (db.DBSession.query(db.PokemonUnlockedEvolution)
            .filter_by(pokemon_id=pokemon.id)
            .delete())

        for evo_id in form.unlocked_evolutions.data:
            db.DBSession.add(db.PokemonUnlockedEvolution(
                pokemon_id=pokemon.id,
                evolved_species_id=evo_id
            ))

    if form.trainer is not None:
        pokemon.trainer_id = form.trainer.id
        pokemon.is_in_squad = False

        if pokemon.trainer_item is not None:
            pokemon.trainer_item.trainer_id = form.trainer.id

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

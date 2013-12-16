import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
import transaction
import wtforms

import asb.models as models
from asb.resources import PokemonIndex, SpeciesIndex
from asb.forms import CSRFTokenForm, MultiCheckboxField

class EditPokemonForm(CSRFTokenForm):
    """A form for editing a Pokémon.

    This will mean more than just its nickname, eventually.
    """

    name = wtforms.TextField('Name')
    save = wtforms.SubmitField('Save')

class PokemonMovingForm(CSRFTokenForm):
    """A form for selecting Pokémon to deposit or withdraw.

    Several parts of this form must be created dynamically, using
    pokemon_deposit_form or pokemon_withdraw_form (below).
    """

    pokemon = MultiCheckboxField(coerce=int)
    submit = wtforms.SubmitField()

def pokemon_deposit_form(trainer, request, use_post=True):
    """Return a PokemonMovingForm for depositing Pokémon."""

    post = request.POST if use_post else None
    form = PokemonMovingForm(post, csrf_context=request.session)

    form.pokemon.choices = [(p.id, '') for p in trainer.squad]

    # The Length validator is intended for strings, but this works so whatever
    form.pokemon.validators.append(
        wtforms.validators.Length(max=len(trainer.squad) - 1,
            message='You must keep at least one Pokémon in your active squad')
    )

    form.submit.label = wtforms.fields.Label('submit', 'Deposit')

    return form

def pokemon_withdraw_form(trainer, request, use_post=True):
    """Return a PokemonMovingForm for withdrawing Pokémon."""

    post = request.POST if use_post else None
    form = PokemonMovingForm(post, csrf_context=request.session)

    form.pokemon.choices = [(p.id, '') for p in trainer.pc]

    if form.pokemon.data:
        # We want to tell them how many Pokémon they're over by if they try to
        # withdraw too many, which means we have to add this validator when the
        # form is being submitted.  Thankfully, that's exactly when we need it.
        max_withdraws = 10 - len(trainer.squad)
        overflow = len(form.pokemon.data) - max_withdraws

        if max_withdraws == 0:
            message = 'Your squad is full!'
        else:
            message = ('You only have room in your squad to withdraw {0} more '
                'Pokémon; please uncheck at least {1}'.format(max_withdraws,
                overflow))

        form.pokemon.validators.append(wtforms.validators.Length(
            max=max_withdraws, message=message))

    form.submit.label = wtforms.fields.Label('submit', 'Withdraw')

    return form


@view_config(context=PokemonIndex, renderer='/indices/pokemon.mako')
def pokemon_index(context, request):
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
def pokemon(context, request):
    """An individual Pokémon's info page."""

    return {'pokemon': context}

@view_config(name='edit', context=models.Pokemon, permission='edit:basics',
  request_method='GET', renderer='edit_pokemon.mako')
def edit_pokemon(pokemon, request):
    form = EditPokemonForm(csrf_context=request.session)
    form.name.data = pokemon.name

    return {'pokemon': pokemon, 'form': form}

@view_config(name='edit', context=models.Pokemon, permission='edit:basics',
  request_method='POST', renderer='edit_pokemon.mako')
def edit_pokemon_commit(pokemon, request):
    form = EditPokemonForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    pokemon.name = form.name.data
    pokemon.update_identifier()
    models.DBSession.flush()

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

@view_config(name='manage', context=PokemonIndex, permission='manage-account',
  request_method='GET', renderer='/manage/pokemon.mako')
def manage_pokemon(context, request):
    """A page for depositing and withdrawing one's Pokémon."""

    trainer = request.user
    deposit = pokemon_deposit_form(trainer, request)
    withdraw = pokemon_withdraw_form(trainer, request)

    return {'trainer': trainer, 'deposit': deposit, 'withdraw': withdraw}

@view_config(name='manage', context=PokemonIndex, permission='manage-account',
  request_method='POST', renderer='/manage/pokemon.mako')
def manage_pokemon_commit(context, request):
    """Process a request to deposit or withdraw Pokémon."""

    trainer = request.user

    if request.POST['submit'] == 'Deposit':
        deposit = pokemon_deposit_form(trainer, request)
        withdraw = pokemon_withdraw_form(trainer, request, use_post=False)
        form = deposit
        is_in_squad = False
    elif request.POST['submit'] == 'Withdraw':
        deposit = pokemon_deposit_form(trainer, request, use_post=False)
        withdraw = pokemon_withdraw_form(trainer, request)
        form = withdraw
        is_in_squad = True

    if not form.validate():
        return {'trainer': trainer, 'deposit': deposit, 'withdraw': withdraw}

    to_toggle = (models.DBSession.query(models.Pokemon)
        .filter(models.Pokemon.id.in_(form.pokemon.data))
        .all())

    for pokemon in to_toggle:
        pokemon.is_in_squad = is_in_squad

    return httpexc.HTTPSeeOther('/pokemon/manage')

@view_config(context=SpeciesIndex, renderer='/indices/pokemon_species.mako')
def species_index(context, request):
    """The index page for all the species of Pokémon."""

    pokemon = (
        models.DBSession.query(models.PokemonSpecies)
        .order_by(models.PokemonSpecies.id)
        .all()
    )

    return {'pokemon': pokemon}

@view_config(context=models.PokemonForm, renderer='/pokemon_species.mako')
def species(context, request):
    """The dex page of a Pokémon species.

    Under the hood, this is actually the dex page for a form.  But it's clearer
    to present it as the page for a species and pretend the particular form is
    just a detail.
    """

    return {'pokemon': context}

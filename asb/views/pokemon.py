from collections import OrderedDict

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
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

class PokemonSpeciesField(wtforms.StringField):
    """A field for a Pokémon species that also fetches the corresponding
    species from the database, and makes sure that it's buyable, for Quick Buy.

    When I get lookup working, it will replace this.
    """

    def _value(self):
        if self.data:
            return self.data[0]
        else:
            return ''

    def process_data(self, value):
        """"""

        if value is None:
            self.data = ('', None)
        else:
            self.data = (value.name, value)

    def process_formdata(self, valuelist):
        name, = valuelist

        try:
            identifier = models.identifier(name)
        except ValueError:
            # Reduces to empty identifier; obviously not going to be a species
            self.data = (name, None)
            return

        # Deal with the Nidorans
        if identifier in ('nidoran-female', 'nidoranf'):
            identifier = 'nidoran-f'
        elif identifier in ('nidoran-male', 'nidoranm'):
            identifier = 'nidoran-m'

        # Try to fetch the species
        try:
            species = (models.DBSession.query(models.PokemonSpecies)
                .filter_by(identifier=identifier)
                .one()
            )

            self.data = (name, species)
        except NoResultFound:
            self.data = (name, None)

    def pre_validate(self, form):
        """Make sure that we actually found a buyable species."""

        name, species = self.data
        if species is None:
            raise wtforms.validators.ValidationError('No such Pokémon found')
        elif species.rarity is None:
            raise wtforms.validators.ValidationError(
                "{0} isn't buyable".format(species.name))

class PokemonCheckoutForm(CSRFTokenForm):
    """A form for actually buying all the Pokémon in the trainer's cart.

    The Pokémon subforms must be created dynamically, using the method
    pokemon_checkout_form (below).
    """

    submit = wtforms.SubmitField('Done')

class QuickBuyForm(CSRFTokenForm):
    """A form for typing in the name of a Pokémon to buy."""

    pokemon = PokemonSpeciesField('Quick buy')
    submit = wtforms.SubmitField('Go!')

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

def pokemon_checkout_form(cart, request):
    """Return a PokemonCheckoutForm based on the given cart."""

    class ContainerForm(wtforms.Form):
        """A container for all the Pokémon subforms."""

        pass

    # We want to get all the species in one query, but we also want to keep
    # cart order, so we use a copy of the cart (it's an OrderedDict, remember)
    # and just change its values to include the species objects
    pokemon = cart.copy()

    specieses = (models.DBSession.query(models.PokemonSpecies)
        .filter(models.PokemonSpecies.identifier.in_(pokemon))
        .all())

    total = 0

    for species in specieses:
        quantity = pokemon[species.identifier]
        pokemon[species.identifier] = (species, quantity)

    # Now for all the subforms.  We're going to need to set the name species in
    # a class in a moment, hence the underscore on this one.
    for species_, quantity in pokemon.values():
        # Figure out ability choices
        abilities = [(ability.slot, ability.ability.name)
            for ability in species_.default_form.abilities
            if not ability.is_hidden]

        if species_.identifier == 'basculin':
            # Fuck it, this is the only buyable Pokémon it matters for
            abilities[0] = (1, 'Reckless (Red)/Rock Head (Blue)')

        class Subform(wtforms.Form):
            """A subform for setting an individual Pokémon's info at checkout.

            Has fields for name, gender, ability, and form (as in e.g. West vs
            East Shellos), but any combination of the last three fields may be
            omitted if they'd only have one option.
            """

            name_ = wtforms.TextField('Name', default=species_.name)

            # Gender field, if the Pokémon can be more than one gender
            if len(species_.genders) > 1:
                gender = wtforms.SelectField('Gender', coerce=int,
                    choices=[(1, 'Female'), (2, 'Male')], default=1)

            # Ability field, if the Pokémon can have more than one ability
            if len(abilities) > 1:
                ability = wtforms.SelectField('Ability', coerce=int,
                    choices=abilities, default=1)

            # Form field, if the Pokémon has different forms
            if len(species_.forms) > 1:
                form_ = wtforms.SelectField('Form', coerce=int,
                    choices=[(f.id, f.identifier) for f in species_.forms],
                    default=species_.default_form.id)

            species = species_  # Hang on to this; we'll need it

        for n in range(quantity):
            subform_name = '{0}-{1}'.format(species.identifier, n + 1)
            setattr(ContainerForm, subform_name, wtforms.FormField(Subform))

    class Form(PokemonCheckoutForm):
        pokemon = wtforms.FormField(ContainerForm)

    form = Form(request.POST, csrf_context=request.session)

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

@view_config(route_name='buy_pokemon', permission='manage-account',
  request_method='GET', renderer='/buy/pokemon.mako')
def buy_pokemon(context, request):
    """A page for buying Pokémon."""

    quick_buy = QuickBuyForm(csrf_context=request.session)

    rarities = (models.DBSession.query(models.Rarity)
        .options(subqueryload('pokemon_species'))
        .order_by(models.Rarity.id)
        .all())

    return {'rarities': rarities, 'quick_buy': quick_buy}

@view_config(route_name='buy_pokemon', permission='manage-account',
  request_method='POST', renderer='/buy/pokemon.mako')
def buy_pokemon_process(context, request):
    """Process a request to add a Pokémon to the cart or quick-buy a
    Pokémon.
    """

    quick_buy = QuickBuyForm(request.POST, csrf_context=request.session)

    if quick_buy.validate():
        species = quick_buy.pokemon.data[1]
        request.session['cart'] = OrderedDict({species.identifier: 1})
        return httpexc.HTTPSeeOther('/pokemon/buy/checkout')

    rarities = (models.DBSession.query(models.Rarity)
        .options(subqueryload('pokemon_species'))
        .order_by(models.Rarity.id)
        .all())

    return {'rarities': rarities, 'quick_buy': quick_buy}

@view_config(route_name='pokemon_checkout', permission='manage-account',
  request_method='GET', renderer='/buy/pokemon_checkout.mako')
def pokemon_checkout(context, request):
    """A page for actually buying all the Pokémon in the trainer's cart."""

    if 'cart' not in request.session or not request.session['cart']:
        request.session.flash('Your cart is empty')
        return httpexc.HTTPSeeOther('/pokemon/buy')

    form = pokemon_checkout_form(request.session['cart'], request)

    return {'form': form}

@view_config(route_name='pokemon_checkout', permission='manage-account',
  request_method='POST', renderer='/buy/pokemon_checkout.mako')
def pokemon_checkout_commit(context, request):
    """"""

    trainer = request.user

    if 'cart' not in request.session or not request.session['cart']:
        request.session.flash('Your cart is empty')
        return httpexc.HTTPSeeOther('/pokemon/buy')

    form = pokemon_checkout_form(request.session['cart'], request)

    if not form.validate():
        return {'form': form}

    squad_count = len(trainer.squad)

    # Ok this is it.  Time to actually create these Pokémon.
    for subform in form.pokemon:
        # Get the next ID
        nextval = models.Pokemon.pokemon_id_seq.next_value()
        id, = select([nextval]).execute().fetchone()

        if hasattr(subform, 'form_'):
            form_id = subform.form_.data
        else:
            form_id = subform.species.default_form.id

        if hasattr(subform, 'gender'):
            gender_id = subform.gender.data
        else:
            gender_id = subform.species.genders[0].id

        if hasattr(subform, 'ability'):
            ability_slot = subform.ability.data
        else:
            ability_slot = 1

        to_squad = squad_count < 10
        squad_count += to_squad

        pokemon = models.Pokemon(
            id=id,
            identifier='temp-{0}'.format(subform.name_.data),
            name=subform.name_.data,
            pokemon_form_id=form_id,
            gender_id=gender_id,
            trainer_id=trainer.id,
            is_in_squad=to_squad,
            ability_slot=ability_slot
        )

        models.DBSession.add(pokemon)
        pokemon.update_identifier()

        trainer.money -= subform.species.rarity.price

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

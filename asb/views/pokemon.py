from collections import OrderedDict
import itertools

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy import func
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
import transaction
import wtforms

from asb import db
from asb.resources import PokemonIndex, SpeciesIndex
import asb.forms


### GENERALLY-USEFUL METHODS

def can_evolve(pokemon):
    """Return whether or not this Pokémon can evolve at all."""

    return any(can_evolve_species(pokemon, evo)[0] for evo in
        pokemon.species.evolutions)

def can_evolve_species(pokemon, species):
    """Return three things: whether or not this Pokémon can evolve into this
    species, whether or not they'll have to pay, and whether or not the
    appropriate item will have to be consumed.
    """

    # Make sure this species is an option in the first place
    if species.evolves_from_species_id != pokemon.form.species_id:
        return (False, False, False)

    evo = species.evolution_method

    # Shedinja has no evolution method
    if evo is None:
        return (False, False, False)

    # Gender requirements apply to all other methods
    if evo.gender_id is not None and pokemon.gender_id != evo.gender_id:
        return (False, False, False)

    # Go through all the methods
    if evo.experience is not None and pokemon.experience >= evo.experience:
        return (True, False, False)
    elif evo.happiness is not None and pokemon.happiness >= evo.happiness:
        return (True, False, False)
    elif (evo.buyable_price is not None and
      pokemon.trainer.money >= evo.buyable_price):
        return (True, True, False)
    elif species in pokemon.unlocked_evolutions:
        return (True, False, evo.item_id is not None)
    else:
        # No dice
        return (False, False, False)

def check_form_condition(pokemon, form):
    """Check the specified Pokémon form's conditions, and return whether the
    Pokémon meets them.

    This method does not check whether the Pokémon is the same species.  For
    example, when evolving a Darumaka, you'll want to check whether it fulfils
    the conditions for Zen Darmanitan, and that works.

    It also does not check whether this Pokémon can actually switch to this
    form.  For example, a Shellos will show up as fulfilling the conditions for
    both its forms.  This is also intentional, because a pre-db Shellos /can/
    switch, exactly once.
    """

    c = form.condition

    if c is None:
        # No condition!  Woo!
        return True

    if c.gender_id is c.item_id is c.ability_id is None:
        # There is a condition, but its parameters are all blank at the moment,
        # meaning it requires an item that hasn't been added yet
        return False

    if c.gender_id is not None and pokemon.gender_id != c.gender_id:
        # Wrong gender
        return False

    if c.item_id is not None and pokemon.trainer_item.item_id != c.item_id:
        # Wrong held item
        return False

    if c.ability_id is not None:
        # Check the ability that this Pokémon would have if it were this  form
        try:
            pfa = DBSession.query(db.PokemonFormAbility).get(
               (form.id, pokemon.ability_slot))
        except sqla.orm.exc.NoResultFound:
            # Welp
            return False

        if pfa.ability_id != c.ability_id:
            # Wrong ability
            return False

    # If we haven't bailed yet, we're good to go
    return True


### WTFORMS CLASSES

class EditPokemonForm(asb.forms.CSRFTokenForm):
    """A form for editing a Pokémon."""

    name = wtforms.TextField('Name', [asb.forms.name_validator])
    form = wtforms.SelectField(coerce=int)
    save = wtforms.SubmitField('Save')

class PokemonEvolutionForm(asb.forms.CSRFTokenForm):
    """A form for evolving a Pokémon.

    The choices for the evolution field must be added dynamically.
    """

    evolution = wtforms.RadioField(coerce=int)
    submit = wtforms.SubmitField('Confirm')

class PokemonMovingForm(asb.forms.CSRFTokenForm):
    """A form for selecting Pokémon to deposit or withdraw.

    Several parts of this form must be created dynamically, using
    pokemon_deposit_form or pokemon_withdraw_form (below).
    """

    pokemon = asb.forms.MultiCheckboxField(coerce=int)
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
            identifier = db.identifier(name)
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
            species = (db.DBSession.query(db.PokemonSpecies)
                .filter_by(identifier=identifier)
                .options(joinedload('default_form'))
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

class PokemonCheckoutForm(asb.forms.CSRFTokenForm):
    """A form for actually buying all the Pokémon in the trainer's cart.

    The Pokémon subforms must be created dynamically, using the method
    pokemon_checkout_form (below).
    """

    submit = wtforms.SubmitField('Done')

class QuickBuyForm(asb.forms.CSRFTokenForm):
    """A form for typing in the name of a Pokémon to buy."""

    pokemon = PokemonSpeciesField('Quick buy')
    quickbuy = wtforms.SubmitField('Go!')


### FORM-CREATING METHODS

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

    total = 0

    # Keep track of how many of each species we've seen so far, in case they're
    # buying more than one of something
    species_seen = {}

    # Now for all the subforms.  We're going to need to set the name species in
    # a class in a moment, hence the underscore on this one.
    for species_ in cart:
        species_ = db.DBSession.merge(species_)
        species_seen.setdefault(species_.identifier, 0)
        species_seen[species_.identifier] += 1
        n = species_seen[species_.identifier]

        # Figure out ability choices
        abilities = [(ability.slot, ability.ability.name)
            for ability in species_.default_form.abilities
            if not ability.is_hidden]

        if species_.identifier == 'basculin':
            # Fuck it, this is the only buyable Pokémon it matters for
            abilities[0] = (1, 'Reckless (Red)/Rock Head (Blue)')

        # Figure out Pokémon form choices
        # XXX At some point in the future we'll actually have to look at what
        # the condition is
        forms = [form for form in species_.forms if form.condition is None]

        class Subform(wtforms.Form):
            """A subform for setting an individual Pokémon's info at checkout.

            Has fields for name, gender, ability, and form (as in e.g. West vs
            East Shellos), but any combination of the last three fields may be
            omitted if they'd only have one option.
            """

            name_ = wtforms.TextField('Name', [asb.forms.name_validator],
                default=species_.name)

            # Gender field, if the Pokémon can be more than one gender
            if len(species_.genders) > 1:
                gender = wtforms.SelectField('Gender', coerce=int,
                    choices=[(1, 'Female'), (2, 'Male')], default=1)

            # Ability field, if the Pokémon can have more than one ability
            if len(abilities) > 1:
                ability = wtforms.SelectField('Ability', coerce=int,
                    choices=abilities, default=1)

            # Form field, if the Pokémon has different forms
            if len(forms) > 1:
                form_ = wtforms.SelectField('Form', coerce=int,
                    choices=[(f.id, f.form_name or 'Default') for f in forms],
                    default=species_.default_form.id)

            species = species_  # Hang on to this; we'll need it
            number = n  # This too

        # Add this subform to the container form
        if n > 1:
            subform_name = '{0}-{1}'.format(species_.identifier, n)
        else:
            subform_name = species_.identifier

        setattr(ContainerForm, subform_name, wtforms.FormField(Subform))

    # Create the form!
    class Form(PokemonCheckoutForm):
        pokemon = wtforms.FormField(ContainerForm)

    form = Form(request.POST, csrf_context=request.session)

    return form


### POKÉMON PAGES

@view_config(context=PokemonIndex, renderer='/indices/pokemon.mako')
def pokemon_index(context, request):
    """The index page for everyone's Pokémon."""

    pokemon = (
        db.DBSession.query(db.Pokemon)
        .join(db.Trainer)
        .filter(db.Trainer.unclaimed_from_hack == False)
        .join(db.PokemonForm)
        .join(db.PokemonSpecies)
        .order_by(db.PokemonSpecies.order, db.Pokemon.name)
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

@view_config(context=db.Pokemon, renderer='/pokemon.mako')
def pokemon(context, request):
    """An individual Pokémon's info page."""

    evolve = can_evolve(context)

    return {'pokemon': context, 'can_evolve': evolve}


### MANAGING POKÉMON

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

@view_config(name='manage', context=PokemonIndex, permission='account.manage',
  request_method='GET', renderer='/manage/pokemon.mako')
def manage_pokemon(context, request):
    """A page for depositing and withdrawing one's Pokémon."""

    trainer = request.user

    if trainer.squad:
        deposit = pokemon_deposit_form(trainer, request)
    else:
        deposit = None

    if trainer.pc:
        withdraw = pokemon_withdraw_form(trainer, request)
    else:
        withdraw = None

    return {'trainer': trainer, 'deposit': deposit, 'withdraw': withdraw}

@view_config(name='manage', context=PokemonIndex, permission='account.manage',
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

    to_toggle = (db.DBSession.query(db.Pokemon)
        .filter(db.Pokemon.id.in_(form.pokemon.data))
        .all())

    for pokemon in to_toggle:
        pokemon.is_in_squad = is_in_squad

    return httpexc.HTTPSeeOther('/pokemon/manage')


### BUYING POKÉMON

def fetch_cart(cart):
    """Turn a cart, i.e. a list of PokemonSpecies identifiers, into a list of
    PokemonSpecies.
    """

    # Fetch all the Pokémon in the cart
    new_cart = (db.DBSession.query(db.PokemonSpecies)
        .filter(db.PokemonSpecies.identifier.in_(cart))
        .options(joinedload('rarity'), joinedload('default_form'))
        .all())

    # Fix duplicates
    new_cart = {species.identifier: species for species in new_cart}
    new_cart = [new_cart[identifier] for identifier in cart]

    return new_cart

def get_rarities():
    """Fetch all the rarities and all the info we'll need about their Pokémon
    for the "buy Pokémon" page.
    """

    return (db.DBSession.query(db.Rarity)
        .options(
            subqueryload('pokemon_species'),
            subqueryload('pokemon_species.default_form'),
            subqueryload('pokemon_species.default_form.types'),
            subqueryload('pokemon_species.default_form.abilities'),
            subqueryload('pokemon_species.default_form.abilities.ability')
        )
        .order_by(db.Rarity.id)
        .all())

@view_config(route_name='pokemon.buy', permission='account.manage',
  request_method='GET', renderer='/buy/pokemon.mako')
def buy_pokemon(context, request):
    """A page for buying Pokémon."""

    quick_buy = QuickBuyForm(csrf_context=request.session)
    rarities = get_rarities()
    cart = fetch_cart(request.session.get('cart', []))

    return {'rarities': rarities, 'quick_buy': quick_buy, 'cart': cart}

@view_config(route_name='pokemon.buy', permission='account.manage',
  request_method='POST', renderer='/buy/pokemon.mako')
def buy_pokemon_process(context, request):
    """Process a request to quick-buy a Pokémon, add one to the user's cart, or
    remove one from the user's cart.
    """

    quick_buy = None

    if 'quickbuy' in request.POST:
        # Quick buy (well, more like quick add-to-cart)
        quick_buy = QuickBuyForm(request.POST, csrf_context=request.session)

        if quick_buy.validate():
            species = quick_buy.pokemon.data[1]
            request.session.setdefault('cart', []).append(species.identifier)
            return httpexc.HTTPSeeOther('/pokemon/buy')
    elif 'add' in request.POST:
        # Add to cart
        identifier = request.POST['add']

        # Make sure it's a real, buyable Pokémon
        try:
            species = (db.DBSession.query(db.PokemonSpecies)
                .filter_by(identifier=identifier)
                .options(joinedload('rarity'), joinedload('default_form'))
                .one()
            )
        except NoResultFound:
            # The only way something can go wrong here is if someone's mucking
            # around, so I don't really care about figuring out errors
            pass
        else:
            if species.rarity_id is not None:
                # Valid Pokémon; add it to the cart
                request.session.setdefault('cart', []).append(species.identifier)
                return httpexc.HTTPSeeOther('/pokemon/buy')
    elif 'remove' in request.POST and 'cart' in request.session:
        # Remove from cart
        identifier = request.POST['remove']

        try:
            request.session['cart'].remove(identifier)
        except ValueError:
            # Again, if they're trying to remove something that's not in their
            # cart, who cares?  Let them quietly fall back to the buy page.
            pass

        return httpexc.HTTPSeeOther('/pokemon/buy')

    # If we haven't returned yet, something's gone wrong; back to the buy page

    if quick_buy is None:
        quick_buy = QuickBuyForm(csrf_context=request.session)

    rarities = get_rarities()
    cart = fetch_cart(request.session.get('cart', []))

    return {'rarities': rarities, 'quick_buy': quick_buy, 'cart': cart}

@view_config(route_name='pokemon.buy.checkout', permission='account.manage',
  request_method='GET', renderer='/buy/pokemon_checkout.mako')
def pokemon_checkout(context, request):
    """A page for actually buying all the Pokémon in the trainer's cart."""

    # Make sure they actually have something to check out
    if 'cart' not in request.session or not request.session['cart']:
        request.session.flash('Your cart is empty')
        return httpexc.HTTPSeeOther('/pokemon/buy')

    cart = fetch_cart(request.session['cart'])

    # Make sure they can afford everything
    grand_total = sum(species.rarity.price for species in cart)
    if grand_total > request.user.money:
        request.session.flash("You can't afford all that!")
        return httpexc.HTTPSeeOther('/pokemon/buy')

    # And go
    form = pokemon_checkout_form(cart, request)

    return {'form': form}

@view_config(route_name='pokemon.buy.checkout', permission='account.manage',
  request_method='POST', renderer='/buy/pokemon_checkout.mako')
def pokemon_checkout_commit(context, request):
    """Process a checkout form and actually give the user their new Pokémon."""

    trainer = request.user

    # Make sure they actually, uh, have something to buy
    if 'cart' not in request.session or not request.session['cart']:
        request.session.flash('Your cart is empty')
        return httpexc.HTTPSeeOther('/pokemon/buy')

    cart = fetch_cart(request.session['cart'])

    # Make sure they actually have enough money
    grand_total = sum(species.rarity.price for species in cart)
    if grand_total > trainer.money:
        request.session.flash("You can't afford all that!")
        return httpexc.HTTPSeeOther('/pokemon/buy')

    # Double-check their checkout form
    form = pokemon_checkout_form(cart, request)

    if not form.validate():
        return {'form': form}

    # Okay this is it.  Time to actually create these Pokémon.
    squad_count = len(trainer.squad)

    for subform in form.pokemon:
        # Get the next available ID for this Pokémon
        nextval = db.Pokemon.pokemon_id_seq.next_value()
        id, = db.DBSession.execute(select([nextval])).fetchone()

        # Figure out form/gender/ability
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

        # Plop it in the squad if there's still room
        to_squad = squad_count < 10
        squad_count += to_squad

        # Aaaaand create it.
        pokemon = db.Pokemon(
            id=id,
            identifier='temp-{0}'.format(subform.name_.data),
            name=subform.name_.data or subform.species.name,
            pokemon_form_id=form_id,
            gender_id=gender_id,
            trainer_id=trainer.id,
            is_in_squad=to_squad,
            ability_slot=ability_slot
        )

        db.DBSession.add(pokemon)
        pokemon.update_identifier()

    # Finish up and return to the "Your Pokémon" page
    trainer.money -= grand_total
    del request.session['cart']

    return httpexc.HTTPSeeOther('/pokemon/manage')


### EVOLVING POKÉMON

def get_evolutions(pokemon):
    """Return all the Pokémon forms that this Pokémon can evolve into."""

    evo_forms = []  # Each element will be (form, needs_buying, needs_item)

    for species in pokemon.species.evolutions:
        # Figure out if this species is a possibility
        can_evolve, buy, item = can_evolve_species(pokemon, species)

        if can_evolve:
            # Figure out which of this species' forms are possibliities
            can_pick_forms = (len(pokemon.species.forms) == 1 or
                pokemon.species.can_switch_forms)

            for form in species.forms:
                if can_pick_forms:
                    # If this Pokémon can switch forms, or doesn't have forms
                    # (yet), it gets to choose its post-evolution form
                    # e.g. Burmy, Spewpa, technically Pikachu
                    can_evolve = check_form_condition(pokemon, form)
                else:
                    # But if it's already constrained to a particular form, it
                    # needs to evolve into the corresponding one
                    # e.g. Shellos, Flabébé
                    can_evolve = form.form_order == pokemon.form.form_order

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


### SPECIES PAGES
def or_iter():
    """A simple iterator to join evolution criteria with "OR", without having
    to make a list.  (Making a list would make appending an item link really
    ugly.)
    """

    yield ''

    while True:
        yield ' <em>OR</em> '

@view_config(context=SpeciesIndex, renderer='/indices/pokemon_species.mako')
def species_index(context, request):
    """The index page for all the species of Pokémon.

    (Forms, actually.  Whatever.)
    """

    # A subquery to count how many of each Pokémon form there are in the league
    population_subquery = (
        db.DBSession.query(db.Pokemon.pokemon_form_id,
            func.count('*').label('population'))
        .select_from(db.Pokemon)
        .join(db.Trainer)
        .filter(db.Trainer.unclaimed_from_hack == False)
        .group_by(db.Pokemon.pokemon_form_id)
        .subquery()
    )

    # Get all the Pokémon and population counts.  Making this an OrderedDict
    # means we can just pass it to pokemon_form_table as is.
    pokemon = OrderedDict(
        db.DBSession.query(db.PokemonForm,
            population_subquery.c.population)
        .select_from(db.PokemonForm)
        .join(db.PokemonSpecies)
        .outerjoin(population_subquery)
        .options(
             joinedload('species'),
             subqueryload('abilities'),
             subqueryload('abilities.ability'),
             subqueryload('types')
        )
        .order_by(db.PokemonForm.order)
        .all()
    )

    return {'pokemon': pokemon}

@view_config(context=db.PokemonForm, renderer='/pokemon_species.mako')
def species(pokemon, request):
    """The dex page of a Pokémon species.

    Under the hood, this is actually the dex page for a form.  But it's clearer
    to present it as the page for a species and pretend the particular form is
    just a detail.
    """

    # Get this Pokémon's abilities but strip out the duplicates
    abilities = []
    for ability in pokemon.abilities:
        if ability.ability_id not in (a.ability_id for a in abilities):
            abilities.append(ability)


    # Build the evolution tree.  n.b. this algorithm assumes that all final
    # evolutions within a family are at the same evo stage.  I'd be surprised
    # if that ever stopped being true, though.

    family = pokemon.species.family

    # Start with all the final evolutions
    prevos = set(species.pre_evolution for species in family.species)
    finals = [pokemon for pokemon in family.species if pokemon not in prevos]
    evo_tree = [finals]

    # Build backwards, with each pre-evo appearing "above" its evo.  Pokémon
    # with multiple evos (now or at a later stage) will appear multiple times.
    while evo_tree[0][0].evolves_from_species_id is not None:
        evo_tree.insert(0, [evo.pre_evolution for evo in evo_tree[0]])

    # Collapse each layer; for example, [A, A, B] would become [(A, 2), (B, 1)]
    for n, layer in enumerate(evo_tree):
        evo_tree[n] = [(evo, sum(1 for _ in group))
            for evo, group in itertools.groupby(layer)]


    # Find all the Pokémon of this species/form in the league
    census = (
        db.DBSession.query(db.Pokemon)
        .join(db.Trainer)
        .filter(db.Pokemon.pokemon_form_id == pokemon.id)
        .filter(db.Trainer.unclaimed_from_hack == False)
        .options(
             joinedload('ability'),
             joinedload('trainer'),
             joinedload('gender')
        )
        .order_by(db.Pokemon.name)
        .all()
    )

    return {'pokemon': pokemon, 'abilities': abilities, 'evo_tree': evo_tree,
        'or_iter': or_iter, 'census': census}

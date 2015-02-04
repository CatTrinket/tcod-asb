import datetime

from pyramid.view import view_config
import pyramid.httpexceptions as httpexc
import sqlalchemy as sqla
import wtforms

from asb import db
import asb.forms


class PokemonBrowseForm(asb.forms.CSRFTokenForm):
    """A form for browsing through Pokémon, and adding one to the cart."""

    # Avoid coercing None; happily keep strings as strings
    add = asb.forms.MultiSubmitField(coerce=lambda value: value)

class PokemonCartForm(asb.forms.CSRFTokenForm):
    """A form representing the user's cart, with buttons to remove Pokémon from
    it.
    """

    # Avoid coercing None; happily keep strings as strings
    remove = asb.forms.MultiSubmitField(coerce=lambda value: value)

class PokemonCheckoutForm(asb.forms.CSRFTokenForm):
    """A form for actually buying all the Pokémon in the trainer's cart.

    The Pokémon subforms must be created dynamically, using the method
    pokemon_checkout_form (below).
    """

    submit = wtforms.SubmitField('Done')

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
            identifier = db.helpers.identifier(name)
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
                .options(sqla.orm.joinedload('default_form'))
                .one()
            )

            self.data = (name, species)
        except sqla.orm.exc.NoResultFound:
            self.data = (name, None)

    def pre_validate(self, form):
        """Make sure that we actually found a buyable species."""

        name, species = self.data
        if species is None:
            raise wtforms.validators.ValidationError('No such Pokémon found')
        elif species.rarity is None:
            raise wtforms.validators.ValidationError(
                "{0} isn't buyable".format(species.name))

class QuickBuyForm(asb.forms.CSRFTokenForm):
    """A form for typing in the name of a Pokémon to buy."""

    pokemon = PokemonSpeciesField('Quick buy')
    quickbuy = wtforms.SubmitField('Go!')


def fetch_cart(cart):
    """Take a cart — a list of (species, promotion) tuples, where each species
    and promotion is an identifier — and return the same list, except with the
    actual species and promotion objects.
    """

    species = (species for (species, promotion) in cart)
    promotions = (promotion for (species, promotion) in cart)

    # Fetch all the Pokémon in the cart
    species = (
        db.DBSession.query(db.PokemonSpecies)
        .filter(db.PokemonSpecies.identifier.in_(species))
        .options(
            sqla.orm.joinedload('rarity'),
            sqla.orm.joinedload('default_form')
        )
        .all()
    )
    species = {species.identifier: species for species in species}

    promotions = (
        db.DBSession.query(db.Promotion)
        .filter(db.Promotion.identifier.in_(promotions))
        .all()
    )
    promotions = {promotion.identifier: promotion for promotion in promotions}

    # Fix duplicates
    new_cart = [
        (species[a_species], promotion and promotions[promotion])
        for (a_species, promotion) in cart
    ]

    return new_cart

def get_pokemon_buying_stuff(request):
    cart = request.session.setdefault('cart', [])

    stuff = {
        'quick_buy': QuickBuyForm(request.POST,
            csrf_context=request.session),
        'browse': PokemonBrowseForm(request.POST,
            csrf_context=request.session),
        'cart_form': PokemonCartForm(request.POST,
            csrf_context=request.session),
        'promotions': [],
        'cart': cart,
        'cart_species': fetch_cart(cart),
        'rarities': get_rarities()
    }

    stuff['browse'].add.choices = [
        (species.identifier, '+')
        for rarity in stuff['rarities']
        for species in rarity.pokemon_species
    ]

    stuff['cart_form'].remove.choices = [
        ('{}:{}'.format(species, promotion)
            if promotion is not None else species, 'X')
        for (species, promotion) in cart
    ]

    # Promotions
    used_promotions = {promotion for (species, promotion) in cart}

    for promotion in request.user.promotions:
        if (promotion.identifier not in used_promotions and
          promotion.pokemon_species):
            form = PokemonBrowseForm(
                request.POST,
                csrf_context=request.session,
                prefix=promotion.identifier
            )

            form.add.choices=[
                (species.identifier, '+')
                for species in promotion.pokemon_species
            ]

            stuff['promotions'].append((promotion, form))

    return stuff

def get_rarities():
    """Fetch all the rarities and all the info we'll need about their Pokémon
    for the "buy Pokémon" page.
    """

    return (
        db.DBSession.query(db.Rarity)
        .options(
            sqla.orm.subqueryload_all(
                'pokemon_species.default_form.abilities.ability'
            ),
            sqla.orm.subqueryload('pokemon_species.default_form.types'),
        )
        .order_by(db.Rarity.id)
        .all()
    )

def pokemon_checkout_form(cart, request):
    """Return a PokemonCheckoutForm based on the given cart."""

    class ContainerForm(wtforms.Form):
        """A container for all the Pokémon subforms."""

        pass

    total = 0

    # Keep track of how many of each species we've seen so far, in case they're
    # buying more than one of something
    species_seen = {}

    # Now for all the subforms.  We're going to need to set these names in a
    # class definition in a moment, hence the underscore on these ones.
    for (species_, promotion_) in cart:
        species_ = db.DBSession.merge(species_)
        species_seen.setdefault(species_.identifier, 0)
        species_seen[species_.identifier] += 1
        n = species_seen[species_.identifier]

        # Figure out ability choices
        allow_hidden_ability = (promotion_ is not None and
            promotion_.hidden_ability)

        abilities = []

        for ability in species_.default_form.abilities:
            if not ability.is_hidden:
                abilities.append((ability.slot, ability.ability.name))
            elif allow_hidden_ability:
                abilities.append((ability.slot,
                    '{} (hidden)'.format(ability.ability.name)))

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
                    choices=abilities, default=3 if allow_hidden_ability else 1)

            # Form field, if the Pokémon has different forms
            if len(forms) > 1:
                form_ = wtforms.SelectField('Form', coerce=int,
                    choices=[(f.id, f.form_name or 'Default') for f in forms],
                    default=species_.default_form.id)

            # Hang onto these; we'll need them
            species = species_
            promotion = promotion_
            number = n

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


@view_config(route_name='pokemon.buy', permission='account.manage',
  request_method='GET', renderer='/buy/pokemon.mako')
def buy_pokemon(context, request):
    """A page for buying Pokémon."""

    return get_pokemon_buying_stuff(request)

@view_config(route_name='pokemon.buy', permission='account.manage',
  request_method='POST', renderer='/buy/pokemon.mako')
def buy_pokemon_process(context, request):
    """Process a request to quick-buy a Pokémon, add one to the user's cart, or
    remove one from the user's cart.
    """

    stuff = get_pokemon_buying_stuff(request)

    if stuff['quick_buy'].quickbuy.data:
        if not stuff['quick_buy'].validate():
            return stuff

        species = stuff['quick_buy'].pokemon.data[1]
        stuff['cart'].append((species.identifier, None))
    elif stuff['browse'].add.data:
        if not stuff['browse'].validate():
            return stuff

        stuff['cart'].append((stuff['browse'].add.data, None))
    elif stuff['cart_form'].remove.data:
        if not stuff['cart_form'].validate():
            return stuff

        pokemon, sep, promotion = stuff['cart_form'].remove.data.partition(':')
        stuff['cart'].remove((pokemon, promotion or None))
    else:
        for (promotion, form) in stuff['promotions']:
            if form.add.data:
                if not form.validate():
                    return stuff

                stuff['cart'].append((form.add.data, promotion.identifier))
                break

    return httpexc.HTTPSeeOther('/pokemon/buy')

@view_config(route_name='pokemon.buy.checkout', permission='account.manage',
  request_method='GET', renderer='/buy/pokemon_checkout.mako')
def pokemon_checkout(context, request):
    """A page for actually buying all the Pokémon in the trainer's cart."""

    cart = request.session.get('cart')

    # Make sure they actually have something to check out
    if not cart:
        request.session.flash('Your cart is empty')
        return httpexc.HTTPSeeOther('/pokemon/buy')

    cart = fetch_cart(cart)

    # Make sure they can afford everything
    grand_total = sum(
        (promotion or species.rarity).price
        for (species, promotion) in cart
    )

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
    grand_total = sum(
        (promotion or species.rarity).price
        for (species, promotion) in cart
    )

    if grand_total > trainer.money:
        request.session.flash("You can't afford all that!")
        return httpexc.HTTPSeeOther('/pokemon/buy')

    # Double-check their checkout form
    form = pokemon_checkout_form(cart, request)

    if not form.validate():
        return {'form': form}

    # Okay this is it.  Time to actually create these Pokémon.
    squad_count = len(trainer.squad)
    today = datetime.date.today()

    for subform in form.pokemon:
        # Get the next available ID for this Pokémon
        id = db.DBSession.execute(db.Pokemon.pokemon_id_seq)

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
            name=subform.name_.data.strip() or subform.species.name,
            pokemon_form_id=form_id,
            gender_id=gender_id,
            trainer_id=trainer.id,
            is_in_squad=to_squad,
            ability_slot=ability_slot,
            birthday=today,
            was_from_hack=False
        )

        db.DBSession.add(pokemon)
        pokemon.update_identifier()

        # Mark the promotion as recieved, if applicable
        if subform.promotion is not None:
            promotion_recipient = db.PromotionRecipient(
                promotion_id=subform.promotion.id,
                trainer_id=trainer.id,
                received=True
            )

            db.DBSession.merge(promotion_recipient)

    # Finish up and return to the "Your Pokémon" page
    trainer.money -= grand_total
    del request.session['cart']

    return httpexc.HTTPSeeOther('/pokemon/manage')

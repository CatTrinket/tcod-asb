import itertools

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.orm.exc import NoResultFound
import wtforms

from asb import db
from asb.resources import ItemIndex
import asb.forms

class GiveItemForm(asb.forms.CSRFTokenForm):
    """A form for choosing a Pokémon to give a particular item or use an item
    on.
    """

    pokemon = asb.forms.MultiSubmitField(coerce=int)

class TakeItemsForm(asb.forms.CSRFTokenForm):
    """A form for selecting Pokémon whose held items to return to the bag."""

    holders = asb.forms.MultiCheckboxField(coerce=int)  # Values will be ids
    take = wtforms.SubmitField('Take items')


@view_config(context=ItemIndex, renderer='/indices/items.mako')
def item_index(context, request):
    """The index of all the different items."""

    item_categories = (
        db.DBSession.query(db.ItemCategory)
        .options(subqueryload(db.ItemCategory.items))
        .order_by(db.ItemCategory.order)
        .all()
    )

    return {'item_categories': item_categories}

def _manage_items_queries(trainer):
    """Perform the queries needed for the "manage items" page and return the
    results.

    The same queries are needed for both the GET and POST views, so this avoids
    repeating some complex query code.
    """

    # A subquery to count how many of each item a trainer has in their bag
    quantity = (
        db.DBSession.query(db.TrainerItem.item_id,
            func.count('*').label('quantity'))
        .filter(db.TrainerItem.trainer_id == trainer.id,
            db.TrainerItem.pokemon_id == None)
        .group_by(db.TrainerItem.item_id)
        .subquery()
    )

    # Get the trainer's bag, including the quantity of each item w/ subquery
    holdable = (
        db.DBSession.query(db.Item, quantity.c.quantity)
        .join(quantity, db.Item.id == quantity.c.item_id)
        .order_by(db.Item.name)
        .all()
    )

    # Get a list of the trainer's Pokémon who are holding items
    holders = (
        db.DBSession.query(db.Pokemon)
        .filter(db.Pokemon.trainer_id == trainer.id)
        .join(db.TrainerItem)
        .join(db.Item)
        .order_by(db.Pokemon.is_in_squad.desc(), db.Item.name,
            db.TrainerItem.id)
        .all()
    )

    return (holdable, holders)

@view_config(name='manage', context=ItemIndex, permission='account.manage',
  request_method='GET', renderer='/manage/items.mako')
def manage_items(context, request):
    """A page for managing one's items."""

    trainer = request.user

    holdable, holders = _manage_items_queries(trainer)

    take_form = TakeItemsForm(csrf_context=request.session)
    take_form.holders.choices = [(pokemon.id, '') for pokemon in holders]

    return {'holdable': holdable, 'holders': holders, 'take_form': take_form}

@view_config(name='manage', context=ItemIndex, permission='account.manage',
  request_method='POST', renderer='/manage/items.mako')
def manage_items_commit(context, request):
    """Process a request to take items.

    Giving items happens elsewhere.
    """

    trainer = request.user

    holdable, holders = _manage_items_queries(trainer)

    # Validate the form
    take_form = TakeItemsForm(request.POST, csrf_context=request.session)
    take_form.holders.choices = [(pokemon.id, '') for pokemon in holders]

    if not take_form.validate():
        return {'holdable': holdable, 'holders': holders,
            'take_form': take_form}

    # Find the items held by the specified Pokémon
    to_take = (db.DBSession.query(db.TrainerItem)
        .filter(db.TrainerItem.pokemon_id.in_(
            take_form.holders.data))
        .all()
    )

    # Return them to the bag
    for trainer_item in to_take:
        trainer_item.pokemon_id = None

    return httpexc.HTTPSeeOther('/items/manage')

@view_config(context=db.Item, renderer='/item.mako')
def item(context, request):
    """An item's dex page."""

    return {'item': context}


### ITEM GIVING

def item_pokemon_choices(trainer, item, form):
    """Determine which of the trainer's Pokémon this item can be given to/used
    on, set choices for the form's pokemon field accordingly, and return the
    list of Pokémon grouped into squad and PC.
    """

    # Query this trainer's Pokémon
    query = (
        db.DBSession.query(db.Pokemon)
        .filter_by(trainer_id=trainer.id)
        .order_by(db.Pokemon.is_in_squad.desc(), db.Pokemon.id)
    )

    # For the Ability Capsule, narrow it down to Pokémon that have a non-hidden
    # ability and another non-hidden ability to switch to
    if item.identifier == 'ability-capsule':
        query = query.filter(db.Pokemon.ability_slot.in_([1, 2]))
        query = query.filter(
            db.DBSession.query(db.PokemonFormAbility)
            .filter(db.PokemonFormAbility.pokemon_form_id ==
                db.Pokemon.pokemon_form_id)
            .filter_by(slot=2)
            .exists()
        )

    pokemon = query.all()

    # Set choices
    if item.identifier in ['ability-capsule', 'rare-candy']:
        label = 'Use'
    else:
        label = 'Give'

    form.pokemon.choices = [(a_pokemon.id, label) for a_pokemon in pokemon]

    # Group and return Pokémon
    return [
        list(pokemon) for is_in_squad, pokemon in
        itertools.groupby(pokemon, lambda a_pokemon: a_pokemon.is_in_squad)
    ]

@view_config(name='give', context=db.Item, permission='account.manage',
  request_method='GET', renderer='/manage/give_item.mako')
def give_item(item, request):
    """A page for choosing a Pokémon to give an item to/use an item on,
    depending on the item.
    """

    trainer = request.user

    # Make sure this trainer actually has this item in their bag
    has_item = (
        db.DBSession.query(db.TrainerItem)
        .filter_by(trainer_id=trainer.id, item_id=item.id, pokemon_id=None)
    )

    has_item, = db.DBSession.query(has_item.exists()).one()

    if not has_item:
        raise httpexc.HTTPForbidden("You don't have this item in your bag!")

    # Make form
    form = GiveItemForm(request.POST, csrf_context=request.session)
    pokemon = item_pokemon_choices(trainer, item, form)

    return {'item': item, 'form': form, 'pokemon': pokemon}

@view_config(name='give', context=db.Item, permission='account.manage',
  request_method='POST', renderer='/manage/give_item.mako')
def give_item_commit(item, request):
    """Process a request to give an item to a Pokémon or use an item on a
    Pokémon, depending on the item.
    """

    trainer = request.user

    # Find this item in the trainer's bag
    trainer_item = (
        db.DBSession.query(db.TrainerItem)
        .filter_by(trainer_id=trainer.id, item_id=item.id, pokemon_id=None)
        .first()
    )

    if trainer_item is None:
        raise httpexc.HTTPForbidden("You don't have this item in your bag!")

    # Validate form
    form = GiveItemForm(request.POST, csrf_context=request.session)
    pokemon = item_pokemon_choices(trainer, item, form)

    if not form.validate():
        return {'item': item, 'form': form, 'pokemon': pokemon}

    # Give item to/use item on (as the case may be) the Pokémon
    pokemon = db.DBSession.query(db.Pokemon).get(form.pokemon.data)

    if item.identifier == 'rare-candy':
        # Rare Candy: give it 1 exp and happiness and delete the Candy
        pokemon.experience += 1
        pokemon.happiness += 1

        db.DBSession.delete(trainer_item)
    elif item.identifier == 'ability-capsule':
        # Ability Capsule: switch to the other ability and delete the Capsule
        if pokemon.ability_slot == 1:
            pokemon.ability_slot = 2
        elif pokemon.ability_slot == 2:
            pokemon.ability_slot = 1

        db.DBSession.delete(trainer_item)
    else:
        # Plain old held item: give it the item and replace current item if any
        if pokemon.trainer_item is not None:
            request.session.flash("{}'s {} was replaced with the {}.".format(
                pokemon.name, pokemon.item.name, item.name))

            pokemon.trainer_item.pokemon_id = None
            db.DBSession.flush()

        trainer_item.pokemon_id = pokemon.id

    return httpexc.HTTPSeeOther('/items/manage')


### ITEM-BUYING

class ItemField(wtforms.TextField):
    """A text field for the name of an item to buy, which also fetches and
    validates  the item.
    """

    def process_formdata(self, valuelist):
        """Fetch the item and stash it in an attribute."""

        name, = valuelist
        self.data = name

        # Fudge fuzzy-matching by turning the input into an identifier
        try:
            identifier = db.identifier(name)
        except ValueError:
            # Reduces to empty identifier; obviously not going to be an item
            self.item = None
            return

        # Try to fetch the item
        try:
            item = (
                db.DBSession.query(db.Item)
                .filter_by(identifier=identifier)
                .one()
            )

            self.item = item
        except NoResultFound:
            self.item = None

    def pre_validate(self, form):
        """Make sure we got an actual, buyable item."""

        if self.item is None:
            raise wtforms.validators.ValidationError('No such item found.')
        elif self.item.price is None:
            raise wtforms.validators.ValidationError(
                '{} is unbuyable.'.format(self.item.name))

class QuickBuyForm(asb.forms.CSRFTokenForm):
    """A form for typing in the name of an item to buy."""

    item = ItemField('Quick buy')
    quick_buy = wtforms.SubmitField('Go!')

class ItemCartFormShell(asb.forms.CSRFTokenForm):
    """A form for the item cart, minus the actual cart bits, which will have to
    be added dynamically.
    """

    update = wtforms.SubmitField('Update')
    buy = wtforms.SubmitField('Buy')

def get_item_buying_stuff(request):
    """Return various things that both the GET and POST views for the item-
    buying page will need.

    - A query to get all the buyable items; it is up to the caller method to
      actually execute the query if it needs to
    - A quick buy form
    - A list of items in the cart, rather than identifiers (n.b. no quantities)
    - A form for the item cart
    """

    # One: the item query
    item_query = (
        db.DBSession.query(db.Item)
        .join(db.ItemCategory)
        .options(joinedload('category'))
        .filter(db.Item.price.isnot(None))
        .order_by(db.ItemCategory.order, db.Item.order, db.Item.price,
            db.Item.name)
    )

    # Two: the quick buy form
    quick_buy = QuickBuyForm(request.POST, csrf_context=request.session)
    quick_buy.csrf_token.id = 'csrf_token_quick_buy'

    # Three: the cart
    cart = request.session.get('item_cart')

    if not cart:
        # If it's absent/empty, just return what we have
        return (item_query, quick_buy, None, None)

    items = item_query.filter(db.Item.identifier.in_(cart)).all()

    # Four: the cart form
    # Stick all the item fields in a subform for easy iterating
    class ItemCartSubform(wtforms.Form):
        pass

    for item in items:
        field = wtforms.IntegerField(
            default=cart[item.identifier],
            validators=[
                wtforms.validators.Optional(),
                wtforms.validators.NumberRange(min=0, max=999)
            ]
        )

        setattr(ItemCartSubform, item.identifier, field)

    class ItemCartForm(ItemCartFormShell):
        items = wtforms.FormField(ItemCartSubform)

    form = ItemCartForm(request.POST, csrf_context=request.session)
    form.id = 'csrf_token_item_cart'

    return (item_query, quick_buy, items, form)

@view_config(route_name='items.buy', permission='account.manage',
  request_method='GET', renderer='/buy/items.mako')
def buy_items(context, request):
    """A page for buying items."""

    item_query, quick_buy, cart, cart_form = get_item_buying_stuff(request)
    items = itertools.groupby(item_query.all(), lambda item: item.category)

    return {'items': items, 'quick_buy': quick_buy, 'cart': cart,
        'cart_form': cart_form}

@view_config(route_name='items.buy', permission='account.manage',
  request_method='POST', renderer='/buy/items.mako')
def buy_items_process(context, request):
    """Process a request from any of the several forms on the item-buying
    page.
    """

    # Check if we're adding an item before anything else, since we're handling
    # that separately
    if 'add' in request.POST:
        identifier = request.POST['add']

        # Check if this item exists and is buyable
        is_valid_item = (
           db.DBSession.query(db.Item)
           .filter_by(identifier=identifier)
           .filter(db.Item.price.isnot(None))
           .exists()
        )

        is_valid_item = db.DBSession.query(is_valid_item).one()

        # If so, add it
        if is_valid_item:
            (request.session.setdefault('item_cart', {})
                .setdefault(identifier, 0))
            request.session['item_cart'][identifier] += 1

        # If not, it means they were messing around with the form, so I'm not
        # going to bother giving a useful error

        return httpexc.HTTPSeeOther('/items/buy')

    # Otherwise, handle the various forms
    item_query, quick_buy, cart, cart_form = get_item_buying_stuff(request)

    # Figure out which form we're handling here and validate it
    if quick_buy.quick_buy.data:
        is_valid = quick_buy.validate()
    else:
        is_valid = cart_form is not None and cart_form.validate()

    if not is_valid:
        items = itertools.groupby(item_query.all(), lambda item: item.category)

        return {'items': items, 'quick_buy': quick_buy, 'cart': cart,
            'cart_form': cart_form}

    if quick_buy.quick_buy.data:
        # Quick buy: just add the item to the cart
        identifier = quick_buy.item.item.identifier
        request.session.setdefault('item_cart', {}).setdefault(identifier, 0)
        request.session['item_cart'][identifier] += 1

        return httpexc.HTTPSeeOther('/items/buy')
    elif cart_form.update.data:
        # Update the cart
        for item, field in zip(cart, cart_form.items):
            if not field.data:
                # Quantity 0 or blank quantity means remove from cart
                del request.session['item_cart'][item.identifier]
            else:
                # Otherwise, update the quantity
                request.session['item_cart'][item.identifier] = field.data

        return httpexc.HTTPSeeOther('/items/buy')
    elif cart_form.buy.data:
        # Buy!  Start buy pairing items with quantities.
        final_cart = [(item, field.data) for item, field in
            zip(cart, cart_form.items)]

        # Make sure they have enough
        grand_total = sum(item.price * qty for item, qty in final_cart)

        if grand_total > request.user.money:
            cart_form.buy.errors.append("You can't afford all that!")
            items = itertools.groupby(item_query.all(),
                lambda item: item.category)
            return {'items': items, 'quick_buy': quick_buy, 'cart': cart,
                'cart_form': cart_form}

        # Give them the items
        for item, quantity in final_cart:
            for n in range(quantity):
                new_item = db.TrainerItem(trainer_id=request.user.id,
                    item_id=item.id)
                db.DBSession.add(new_item)

        request.user.money -= grand_total
        del request.session['item_cart']

        return httpexc.HTTPSeeOther('/items/manage')

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.sql import func
from sqlalchemy.orm.exc import NoResultFound
import wtforms

import asb.models as models
from asb.resources import ItemIndex
from asb.forms import CSRFTokenForm, MultiCheckboxField

class TakeItemsForm(CSRFTokenForm):
    """A form for selecting Pokémon whose held items to return to the bag."""

    holders = MultiCheckboxField(coerce=int)
    take = wtforms.SubmitField('Take items')


@view_config(context=ItemIndex, renderer='/indices/items.mako')
def item_index(context, request):
    """The index of all the different items."""

    items = (
        models.DBSession.query(models.Item)
        .order_by(models.Item.name)
        .all()
    )

    return {'items': items}

def _manage_items_queries(trainer):
    """Perform the queries needed for the "manage items" page and return the
    results.
    """

    quantity = (
        models.DBSession.query(models.TrainerItem.item_id,
            func.count('*').label('quantity'))
        .filter(models.TrainerItem.trainer_id == trainer.id,
            models.TrainerItem.pokemon_id == None)
        .group_by(models.TrainerItem.item_id)
        .subquery()
    )

    holdable = (
        models.DBSession.query(models.Item, quantity.c.quantity)
        .join(quantity, models.Item.id == quantity.c.item_id)
        .order_by(models.Item.name)
        .all()
    )

    holders = (
        models.DBSession.query(models.Pokemon)
        .filter(models.Pokemon.trainer_id == trainer.id)
        .join(models.TrainerItem)
        .join(models.Item)
        .order_by(models.Pokemon.is_in_squad.desc(), models.Item.name,
            models.TrainerItem.id)
        .all()
    )

    return (holdable, holders)

@view_config(name='manage', context=ItemIndex, permission='manage-account',
  request_method='GET', renderer='/manage/items.mako')
def manage_items(context, request):
    """A page for managing one's items."""

    trainer = request.user

    holdable, holders = _manage_items_queries(trainer)

    take_form = TakeItemsForm(csrf_context=request.session)
    take_form.holders.choices = [(pokemon.id, '') for pokemon in holders]

    return {'holdable': holdable, 'holders': holders, 'take_form': take_form}

@view_config(name='manage', context=ItemIndex, permission='manage-account',
  request_method='POST', renderer='/manage/items.mako')
def manage_items_commit(context, request):
    """Process a request to take items.

    Giving items happens elsewhere.
    """

    trainer = request.user

    holdable, holders = _manage_items_queries(trainer)

    take_form = TakeItemsForm(request.POST, csrf_context=request.session)
    take_form.holders.choices = [(pokemon.id, '') for pokemon in holders]

    if not take_form.validate():
        return {'holdable': holdable, 'holders': holders,
            'take_form': take_form}

    to_take = (models.DBSession.query(models.TrainerItem)
        .filter(models.TrainerItem.pokemon_id.in_(
            take_form.holders.data))
        .all()
    )

    for trainer_item in to_take:
        trainer_item.pokemon_id = None

    return httpexc.HTTPSeeOther('/items/manage')

@view_config(context=models.Item, renderer='/item.mako')
def item(context, request):
    """An item's dex page."""

    return {'item': context}

@view_config(name='give', context=models.Item, permission='manage-account',
  request_method='GET', renderer='/manage/give_item.mako')
def give_item(item, request):
    """A page for choosing a Pokémon to give an item to."""

    # Make sure this trainer actually has this item in their bag
    has_item = (models.DBSession.query(models.TrainerItem)
        .filter(models.TrainerItem.trainer_id == request.user.id,
                models.TrainerItem.item_id == item.id,
                models.TrainerItem.pokemon_id == None)
    )

    has_item, = models.DBSession.query(has_item.exists()).one()

    if not has_item:
        raise httpexc.HTTPForbidden("You don't have this item in your bag!")

    return {'item': item, 'csrf_failure': False}

@view_config(name='give', context=models.Item, permission='manage-account',
  request_method='POST', renderer='/manage/give_item.mako')
def give_item_commit(item, request):
    """Process a request to give an item to a Pokémon."""

    # WTForms can't do multiple submit buttons by default, and I don't feel
    # like writing my own goddamn form class or whatever, so we're going to be
    # handling the POST data manually.

    trainer = request.user

    # First, find the actual item
    trainer_item = (models.DBSession.query(models.TrainerItem)
        .filter_by(trainer_id=trainer.id, item_id=item.id, pokemon_id=None)
        .first()
    )

    if trainer_item is None:
        raise httpexc.HTTPForbidden("You don't have this item in your bag!")

    # Make sure the request data is actually all there...
    if 'pokemon' not in request.POST:
        raise httpexc.HTTPForbidden('what')

    # Check CSRF
    if ('csrf_token' not in request.POST or
      request.POST['csrf_token'] != request.session.get_csrf_token()):
        return {'item': item, 'csrf_failure': True}

    # Find the Pokémon we're giving the item to
    pokemon = (models.DBSession.query(models.Pokemon)
        .filter_by(id=request.POST['pokemon'])
        .first()
    )

    if pokemon is None or pokemon.trainer_id != trainer.id:
        raise httpexc.HTTPForbidden("... That isn't one of your Pokémon...")

    # FINALLY, give it the item, replacing its current item (if any)
    if pokemon.trainer_item is not None:
        request.session.flash("{0}'s {1} was replaced with the {2}.".format(
            pokemon.name, pokemon.item.name, item.name))
        pokemon.trainer_item.pokemon_id = None

    trainer_item.pokemon_id = pokemon.id

    return httpexc.HTTPSeeOther('/items/manage')

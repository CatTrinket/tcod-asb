import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

import asb.db as db
import asb.forms
from asb.resources import TradeIndex

class NewTradeForm(asb.forms.CSRFTokenForm):
    """A form for beginning the trade process."""

    recipient = None
    recipient_name = wtforms.StringField(
        'Who do you want to give a gift?',
        [wtforms.validators.Required()]
    )

    contents = asb.forms.MultiCheckboxField(
        'What would you like to include?',
        choices=[
            ('money', 'Money'),
            ('items', 'Items'),
            ('pokemon', 'Pokémon')
        ],

        validators=[wtforms.validators.Length(
            min=1,
            message='You have to include something'
        )]
    )

    submit = wtforms.SubmitField('Next')

    def validate_recipient_name(form, field):
        """Fetch the named trainer from the database; raise a validation error
        if they're not found.
        """

        try:
            form.recipient = (
                db.DBSession.query(db.Trainer)
                .filter(sqla.func.lower(db.Trainer.name) == field.data.lower())
                .one()
            )
        except sqla.orm.exc.NoResultFound:
            raise wtforms.validators.ValidationError('Unknown trainer')

class ConfirmTradeForm(asb.forms.CSRFTokenForm):
    """A form for deciding whether to edit, confirm, or cancel a trade."""

    edit = wtforms.SubmitField('Edit')
    confirm = wtforms.SubmitField('Confirm')
    cancel = wtforms.SubmitField('Cancel')

class ReconsiderTradeForm(asb.forms.CSRFTokenForm):
    """A form for un-proposing or cancelling a trade that has already been
    proposed.
    """

    draft = wtforms.SubmitField('Return to draft stage')
    cancel = wtforms.SubmitField('Cancel')

def trade_form(request, contents):
    """Dynamically build a trade form with the required pieces."""

    class TradeForm(asb.forms.CSRFTokenForm):
        if 'money' in contents:
            money = wtforms.IntegerField('Amount', [
                wtforms.validators.NumberRange(
                   min=1, max=request.user.money,
                   message="You can't give less than $1 or more than you have"
                )
            ])

        if 'items' in contents:
            items = wtforms.FormField(trade_items_form(request.user))

        if 'pokemon' in contents:
            pokemon = asb.forms.MultiCheckboxField(coerce=int, choices=[
                (pokemon.id, '')
                for pokemon_group in [request.user.squad, request.user.pc]
                for pokemon in pokemon_group
            ])

        next = wtforms.SubmitField('Next')

    return TradeForm(request.POST, prefix='trade',
                     csrf_context=request.session)

def trade_items_form(trainer):
    """Dynamically build and return a subform class for selecting items to
    include in a trade.
    """

    # Build the subform
    class TradeItemsForm(wtforms.Form):
        items = trainer.bag

    for (item, quantity) in trainer.bag:
        field = wtforms.IntegerField(item.name, [
            wtforms.validators.Optional(),
            wtforms.validators.NumberRange(min=0, max=quantity)
        ])

        setattr(TradeItemsForm, item.identifier, field)

    return TradeItemsForm

def trade_redirect(state):
    if state == 'new':
        return httpexc.HTTPSeeOther('/trade')
    elif state == 'build':
        return httpexc.HTTPSeeOther('/trade/build')
    elif state == 'confirm':
        return httpexc.HTTPSeeOther('/trade/confirm')

@view_config(context=TradeIndex, permission='account.manage',
  request_method='GET', renderer='/trade/new.mako')
def start_trade(context, request):
    """Ask the user who to trade with and what to include."""

    trade_info = request.session.get('trade')

    if trade_info is not None:
        state = trade_info['state']

        if 'back' in request.GET or state == 'new':
            form = NewTradeForm(trade_info, csrf_context=request.session)
            trade_info['state'] = 'new'
        else:
            return trade_redirect(state)
    else:
        form = NewTradeForm(csrf_context=request.session)

    pending_trades = (
        db.DBSession.query(db.TradeLot)
        .filter_by(sender_id=request.user.id)
        .all()
    )

    return {'pending_trades': pending_trades, 'form': form}

@view_config(context=TradeIndex, permission='account.manage',
  request_method='POST', renderer='/trade/new.mako')
def start_trade_process(context, request):
    """Process the start trade form."""

    if 'trade' in request.session:
        return httpexc.HTTPSeeOther('/trade/new')

    form = NewTradeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    request.session['trade'] = {
        'state': 'build',
        'recipient': form.recipient.id,
        'recipient_name': form.recipient.name,
        'contents': form.contents.data
    }

    return httpexc.HTTPSeeOther('/trade/build')

@view_config(name='build', context=TradeIndex, permission='account.manage',
  request_method='GET', renderer='/trade/build.mako')
def build_trade(trainer, request):
    """Show the actual trade form."""

    trade_info = request.session.get('trade')

    if trade_info is None:
        request.session.flash('You have no unfinished trade proposals')
        return httpexc.HTTPSeeOther('/trade')
    elif 'back' in request.GET:
        trade_info['state'] = 'build'
    elif trade_info['state'] != 'build':
        return trade_redirect(trade_info['state'])

    return {
        'form': trade_form(request, trade_info['contents']),
        'trade_info': trade_info
    }

@view_config(name='build', context=TradeIndex, permission='account.manage',
  request_method='POST', renderer='/trade/build.mako')
def build_trade_post(context, request):
    """Process the actual trade form."""

    # Get trade info & form
    trade_info = request.session.get('trade')

    if trade_info is None:
        request.session.flash('You have no unfinished trade proposals')
        return httpexc.HTTPSeeOther('/trade')
    elif trade_info['state'] != 'build':
        return trade_redirect(trade_info['state'])

    contents = trade_info['contents']
    form = trade_form(request, contents)

    # Validate
    if not form.validate():
        return {'form': form, 'trade_info': trade_info}

    # Actually build this thing.  Assume it's a Christmas gift for now.
    trade = db.Trade(is_gift=True, reveal_date=datetime.date(2015, 12, 25))
    db.DBSession.add(trade)
    db.DBSession.flush()

    # Add lot
    lot = db.TradeLot(
        trade_id=trade.id,
        sender_id=request.user.id,
        recipient_id=trade_info['recipient']
    )

    db.DBSession.add(lot)
    db.DBSession.flush()

    # Add stuff
    if 'money' in contents:
        request.user.money -= form.money.data
        lot.money = form.money.data

    if 'items' in contents:
        for (field, (item, in_bag)) in zip(form.items, form.items.items):
            if field.data:
                bag_items = (
                    db.DBSession.query(db.TrainerItem)
                    .filter_by(
                        item_id=item.id,
                        trainer_id=request.user.id,
                        pokemon_id=None
                    )
                    .limit(field.data)
                    .all()
                )

                for bag_item in bag_items:
                    db.DBSession.add(db.TradeLotItem(
                        trade_lot_id=lot.id,
                        trainer_item_id=bag_item.id,
                        item_id=bag_item.item_id
                    ))

    if 'pokemon' in contents:
        pokemon = (
            db.DBSession.query(db.Pokemon)
            .filter(db.Pokemon.id.in_(form.pokemon.data))
            .all()
        )

        for a_pokemon in pokemon:
            a_pokemon.is_in_squad = False

            db.DBSession.add(db.TradeLotPokemon(
                trade_lot_id=lot.id,
                pokemon_id=a_pokemon.id
            ))

            if a_pokemon.trainer_item is not None:
                db.DBSession.add(db.TradeLotItem(
                    trade_lot_id=lot.id,
                    trainer_item_id=a_pokemon.trainer_item.id,
                    item_id=a_pokemon.trainer_item.item_id
                ))

    del request.session['trade']

    return httpexc.HTTPSeeOther(
        request.resource_path(trade.__parent__, trade.__name__)
    )

@view_config(context=db.Trade, request_method='GET',
             renderer='/trade/trade.mako')
def trade(context, request):
    """View and possibly do something with a trade."""

    stuff = {'trade': context}

    for lot in context.lots:
        if lot.sender_id == request.user.id:
            if lot.state == 'draft':
                form = ConfirmTradeForm(csrf_context=request.session)
                stuff['confirm_form'] = form
            elif lot.state == 'proposed':
                form = ReconsiderTradeForm(csrf_context=request.session)
                stuff['reconsider_form'] = form

    return stuff

@view_config(context=db.Trade, request_method='POST',
             renderer='/trade/trade.mako')
def trade_process(context, request):
    """Process any of the various forms that can be included on the actual
    trade page.
    """

    for lot in context.lots:
        if lot.sender_id == request.user.id:
            if lot.state == 'draft':
                return trade_confirm(lot, request)
            elif lot.state == 'proposed':
                return trade_reconsider(lot, request)

    # Not sure what they're here for
    return httpexc.HTTPSeeOther(request.path)

def trade_confirm(lot, request):
    """Process a ConfirmTradeForm."""

    form = ConfirmTradeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'trade': lot.trade, 'confirm_form': form}

    if form.edit.data:
        return httpexc.HTTPSeeOther(request.resource_path(lot.trade, 'edit'))
    elif form.confirm.data:
        lot.state = 'proposed'
        lot.notify_recipient = True
        return httpexc.HTTPSeeOther(request.path)
    elif form.cancel.data:
        return cancel_lot(lot, request)

def trade_reconsider(lot, request):
    """Process a ReconsiderTradeForm."""

    form = ReconsiderTradeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'trade': lot.trade, 'reconsider_form': form}

    if form.draft.data:
        lot.state = 'draft'
        lot.notify_recipient = False

        return httpexc.HTTPSeeOther(
            request.resource_path(lot.trade.__parent__, lot.trade.__name__)
        )
    elif form.cancel.data:
        return cancel_lot(lot, request)

def cancel_lot(lot, request):
    """Cancel a trade lot."""

    trade = lot.trade

    if lot.money is not None:
        lot.sender.money += lot.money

    db.DBSession.delete(lot)
    db.DBSession.expire(trade)

    if not trade.lots:
        # This was the only lot; trade cancelled
        db.DBSession.delete(trade)
        request.session.flash('Trade cancelled.')
        return httpexc.HTTPSeeOther('/trade')
    else:
        # It's an actual trade, and the other person still has a lot.  I don't
        # know what to do with this yet.
        raise ValueError("Two-way trading hasn't been implemented yet")

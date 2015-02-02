import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

import asb.db as db
import asb.forms

class FlavorEditForm(asb.forms.CSRFTokenForm):
    summary = wtforms.StringField('Summary')
    description = wtforms.TextAreaField('Description')
    preview = wtforms.SubmitField('Preview')
    save = wtforms.SubmitField('Save')

@view_config(name='edit', context=db.Move, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_move(move, request):
    """A flavor-editing page for moves."""

    form = FlavorEditForm(csrf_context=request.session)
    form.summary.data = move.summary
    form.description.data = move.description

    return {'form': form, 'thing': move}

@view_config(name='edit', context=db.Move, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_move(move, request):
    """"""

    form = FlavorEditForm(request.POST, csrf_context=request.session)

    if not form.validate() or form.preview.data:
        return {'form': form, 'thing': move}

    new_effect = db.MoveEffect(
        move_id=move.id,
        edit_time=datetime.datetime.now(),
        edited_by_trainer_id=request.user.id,
        summary=form.summary.data,
        description=form.description.data,
        is_current=True
    )

    move.effect.is_current = False
    db.DBSession.add(new_effect)

    return httpexc.HTTPSeeOther(
        request.resource_path(move.__parent__, move.__name__)
    )

@view_config(name='edit', context=db.Item, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_item(item, request):
    """A flavor-editing page for items."""

    form = FlavorEditForm(csrf_context=request.session)
    form.summary.data = item.summary
    form.description.data = item.description

    return {'form': form, 'thing': item}

@view_config(name='edit', context=db.Item, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_item(item, request):
    """"""

    form = FlavorEditForm(request.POST, csrf_context=request.session)

    if not form.validate() or form.preview.data:
        return {'form': form, 'thing': item}

    new_effect = db.ItemEffect(
        item_id=item.id,
        edit_time=datetime.datetime.now(),
        edited_by_trainer_id=request.user.id,
        summary=form.summary.data,
        description=form.description.data,
        is_current=True
    )

    item.effect.is_current = False
    db.DBSession.add(new_effect)

    return httpexc.HTTPSeeOther(
        request.resource_path(item.__parent__, item.__name__)
    )

@view_config(name='edit', context=db.Ability, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_ability(ability, request):
    """A flavor-editing page for abilitys."""

    form = FlavorEditForm(csrf_context=request.session)
    form.summary.data = ability.summary
    form.description.data = ability.description

    return {'form': form, 'thing': ability}

@view_config(name='edit', context=db.Ability, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_ability(ability, request):
    """"""

    form = FlavorEditForm(request.POST, csrf_context=request.session)

    if not form.validate() or form.preview.data:
        return {'form': form, 'thing': ability}

    new_effect = db.AbilityEffect(
        ability_id=ability.id,
        edit_time=datetime.datetime.now(),
        edited_by_trainer_id=request.user.id,
        summary=form.summary.data,
        description=form.description.data,
        is_current=True
    )

    ability.effect.is_current = False
    db.DBSession.add(new_effect)

    return httpexc.HTTPSeeOther(
        request.resource_path(ability.__parent__, ability.__name__)
    )

import datetime

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import wtforms

import asb.db as db
import asb.forms

class FlavorEditForm(asb.forms.CSRFTokenForm):
    """A form for editing something's flavor text."""

    edit_time = wtforms.HiddenField()
    summary = wtforms.StringField('Summary')
    description = wtforms.TextAreaField('Description')
    notes = wtforms.TextAreaField('Notes')
    preview = wtforms.SubmitField('Preview')
    save = wtforms.SubmitField('Save')

class MoveEditForm(FlavorEditForm):
    """A form for editing a move's flavor and energy."""

    energy = wtforms.IntegerField('Energy', [wtforms.validators.Optional()])

def timestamp(effect):
    """Return a string timestamp representing the edit time of the given
    effect, which may be None.
    """

    if effect is None:
        return 'never'
    else:
        return effect.edit_time.isoformat()

def edit_flavor(thing, request, form_class=FlavorEditForm):
    """A flavor-editing page for whatever."""

    form = form_class(csrf_context=request.session)
    form.summary.data = thing.summary
    form.description.data = thing.description
    form.notes.data = thing.notes
    form.edit_time.data = timestamp(thing.effect)

    if hasattr(form, 'energy'):
        form.energy.data = thing.energy

    return {'form': form, 'thing': thing}

def process_edit_flavor(thing, request, effect_class, foreign_key_name,
                        form_class=FlavorEditForm):
    """Process a flavor editing form."""

    form = form_class(request.POST, csrf_context=request.session)
    valid = form.validate()
    edit_time = timestamp(thing.effect)

    if form.edit_time.data != edit_time:
        valid = False
        form.edit_time.data = edit_time
        form.edit_time.errors.append(
            '{0} has edited {1} since you started editing.  The current '
            'revision is shown below; please incorporate any changes into '
            'your version.'
            .format(thing.effect.editor.name, move.name)
        )

    if not valid or form.preview.data:
        return {'form': form, 'thing': thing}

    new_effect = effect_class(
        edit_time=datetime.datetime.utcnow(),
        edited_by_trainer_id=request.user.id,
        summary=form.summary.data,
        description=form.description.data,
        notes=form.notes.data,
        is_current=True
    )

    setattr(new_effect, foreign_key_name, thing.id)

    if isinstance(new_effect, db.MoveEffect):
        new_effect.energy = form.energy.data

    if thing.effect is not None:
        thing.effect.is_current = False

    db.DBSession.add(new_effect)

    return httpexc.HTTPSeeOther(
        request.resource_path(thing.__parent__, thing.__name__)
    )

@view_config(name='edit', context=db.Move, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_move(move, request):
    return edit_flavor(move, request, form_class=MoveEditForm)

@view_config(name='edit', context=db.Move, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_move(move, request):
    return process_edit_flavor(move, request, db.MoveEffect, 'move_id',
                               form_class=MoveEditForm)

@view_config(name='edit', context=db.Item, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_item(item, request):
    return edit_flavor(item, request)

@view_config(name='edit', context=db.Item, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_item(item, request):
    return process_edit_flavor(item, request, db.ItemEffect, 'item_id')

@view_config(name='edit', context=db.Ability, permission='flavor.edit',
  request_method='GET', renderer='/edit_flavor.mako')
def edit_ability(ability, request):
    return edit_flavor(ability, request)

@view_config(name='edit', context=db.Ability, permission='flavor.edit',
  request_method='POST', renderer='/edit_flavor.mako')
def process_edit_ability(ability, request):
    return process_edit_flavor(ability, request, db.AbilityEffect,
                               'ability_id')

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

import unicodedata

from asb import db
import asb.forms


def name_validator(form, field):
    """Validate a signature move or attribute name."""

    name = field.data

    # Check name length; saves having to add a Length validator separately
    if len(name) > 50:
        raise wtforms.validators.ValidationError('Maximum fifty characters.')

    # Check for weird characters that are very unlikely to be used legitimately
    for character in name:
        category = unicodedata.category(character)

        if category.startswith('M'):
            raise wtforms.validators.ValidationError(
                'Combining characters are not allowed.')
        elif category.startswith('C') or category in ['Zl', 'Zp']:
            raise wtforms.validators.ValidationError(
                'Printable characters only please.')

class SigAttributeForm(asb.forms.CSRFTokenForm):
    """A form."""

    name = wtforms.TextField(
        'Name',
        [name_validator, wtforms.validators.Required()])
    bio = wtforms.TextAreaField('Bio')
    effects = wtforms.TextAreaField(
        'Effects',
        [wtforms.validators.Required()])
    submit = wtforms.SubmitField('Submit')

class SigMoveForm(asb.forms.CSRFTokenForm):
    """A form."""

    name = wtforms.TextField(
        'Name',
        validators=[name_validator, wtforms.validators.Required()])
    description = wtforms.TextAreaField(
        'Description',
        validators=[wtforms.validators.Required()])
    type = wtforms.SelectField('Type', coerce=int)
    damage_class = wtforms.SelectField('Damage Class', coerce=int)
    bp = wtforms.IntegerField(
        'Base Power',
        validators=[wtforms.validators.NumberRange(min=0),
                    wtforms.validators.Optional()])
    energy = wtforms.IntegerField(
        'Energy Cost',
        validators=[wtforms.validators.NumberRange(min=1),
                    wtforms.validators.Optional()])
    accuracy = wtforms.IntegerField(
        'Accuracy',
        validators=[wtforms.validators.NumberRange(min=0),
                    wtforms.validators.Optional()])
    target = wtforms.SelectField('Target', coerce=int)
    duration = wtforms.TextField('Duration')
    usage_gap = wtforms.TextField(
        'Usage Gap',
        [wtforms.validators.Required()])
    effects = wtforms.TextAreaField(
        'Effects',
        [wtforms.validators.Required()])
    submit = wtforms.SubmitField('Submit')

    def populate_form_choices(self):
        """Query the DB for a list of types for the type field."""

        types = db.DBSession.query(db.Type).all()
        self.type.choices = [(t.id, t.name) for t in types]

        damage_classes = db.DBSession.query(db.DamageClass).all()
        self.damage_class.choices = [(c.id, c.name.capitalize())
                                     for c in damage_classes]

        targets = db.DBSession.query(db.MoveTarget).all()
        self.target.choices = [(t.id, t.name) for t in targets]


@view_config(name='attribute', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='/sig_stuff/submit_sig_attribute.mako')
def submit_sig_attribute(pokemon, request):
    """A page for submitting a signature attribute for approval."""

    form = SigAttributeForm(csrf_context=request.session)

    return {'pokemon': pokemon, 'form': form, 'action': 'attribute'}

@view_config(name='attribute', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='/sig_stuff/submit_sig_attribute.mako')
def submit_sig_attribute_commit(pokemon, request):
    """Process a request to submit a signature attribute for approval."""

    form = SigAttributeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form, 'action': 'attribute'}

    attribute = db.BodyModification(
        pokemon_id=pokemon.id,
        name=form.name.data,
        is_repeatable=False,  # what even is this
        description=form.bio.data,
        effect=form.effects.data)
    db.DBSession.add(attribute)

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#body-mod")

@view_config(name='attribute-edit', context=db.Pokemon,
  permission='edit.basics', request_method='GET',
  renderer='/sig_stuff/submit_sig_attribute.mako')
def edit_sig_attribute(pokemon, request):
    """A page for editing a signature attribute that's pending approval."""

    mod = pokemon.body_modification
    form = SigAttributeForm(csrf_context=request.session)
    form.name.data = mod.name
    form.bio.data = mod.description
    form.effects.data = mod.effect

    return {'pokemon': pokemon, 'form': form, 'action': 'attribute-edit'}

@view_config(name='attribute-edit', context=db.Pokemon,
  permission='edit.basics', request_method='POST',
  renderer='/sig_stuff/submit_sig_attribute.mako')
def edit_sig_attribute_commit(pokemon, request):
    """Process a request to edit a signature attribute pending approval."""

    form = SigAttributeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form, 'action': 'attribute-edit'}

    attribute = pokemon.body_modification
    attribute.name = form.name.data
    attribute.description = form.bio.data
    attribute.effect = form.effects.data

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#body-mod")

@view_config(name='move', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='/sig_stuff/submit_sig_move.mako')
def submit_sig_move(pokemon, request):
    """A page for submitting a signature move for approval."""

    form = SigMoveForm(csrf_context=request.session)
    form.populate_form_choices()

    return {'pokemon': pokemon, 'form': form, 'action': 'move'}

@view_config(name='move', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='/sig_stuff/submit_sig_move.mako')
def submit_sig_move_commit(pokemon, request):
    """Process a request to submit a signature move for approval."""

    form = SigMoveForm(request.POST, csrf_context=request.session)
    form.populate_form_choices()

    if not form.validate():
        return {'pokemon': pokemon, 'form': form, 'action': move}

    move = db.MoveModification(
        pokemon_id=pokemon.id,
        name=form.name.data,
        type_id=form.type.data,
        power=form.bp.data,
        energy=form.energy.data,
        accuracy=form.accuracy.data,
        target_id=form.target.data,
        gap=form.usage_gap.data,
        duration=form.duration.data,
        damage_class_id=form.damage_class.data,
        description=form.description.data,
        effect=form.effects.data)
    db.DBSession.add(move)

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#move-mod")

@view_config(name='move-edit', context=db.Pokemon,
    permission='edit.basics', request_method='GET',
    renderer='/sig_stuff/submit_sig_move.mako')
def edit_sig_move(pokemon, request):
    """A page for editing a signature move that's pending approval."""

    mod = pokemon.move_modification
    form = SigMoveForm(csrf_context=request.session)
    form.populate_form_choices()

    form.name.data = mod.name
    form.description.data = mod.description
    form.type.data = mod.type_id
    form.damage_class.data = mod.damage_class_id
    form.bp.data =  mod.power
    form.energy.data = mod.energy
    form.accuracy.data = mod.accuracy
    form.target.data = mod.target_id
    form.duration.data = mod.duration
    form.usage_gap.data = mod.gap
    form.effects.data = mod.effect

    return {'pokemon': pokemon, 'form': form, 'action': 'move-edit'}

@view_config(name='move-edit', context=db.Pokemon,
  permission='edit.basics', request_method='POST',
  renderer='/sig_stuff/submit_sig_move.mako')
def edit_sig_move_commit(pokemon, request):
    """Process a request to edit a signature move pending approval."""

    form = SigMoveForm(request.POST, csrf_context=request.session)
    form.populate_form_choices()

    if not form.validate():
        return {'pokemon': pokemon, 'form': form, 'action': 'move-edit'}

    move = pokemon.move_modification
    move.name = form.name.data
    move.description = form.description.data
    move.type_id = form.type.data
    move.damage_class_id = form.damage_class.data
    move.power = form.bp.data
    move.energy = form.energy.data
    move.accuracy = form.accuracy.data
    move.target_id = form.target.data
    move.duration = form.duration.data
    move.gap = form.usage_gap.data
    move.effect = form.effects.data

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#move-mod")

@view_config(name='approve-move', permission='bank.approve',
  request_method='GET', renderer='/sig_stuff/sig_move_approve.mako')
def approve_sig_move(context, request):
    """The signature move approving page."""

    pending_moves = (
        db.DBSession.query(db.MoveModification)
        .filter_by(needs_approval=True)
        .all()
    )

    return {'moves': pending_moves}

@view_config(name='approve-attribute', permission='bank.approve',
  request_method='GET', renderer='/sig_stuff/sig_attribute_approve.mako')
def approve_sig_attribute(context, request):
    """The signature attribute approving page."""

    pending_attributes = (
        db.DBSession.query(db.BodyModification)
        .filter_by(needs_approval=True)
        .all()
    )

    return {'attributes': pending_attributes}


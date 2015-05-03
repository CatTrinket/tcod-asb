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
    """A form for submitting or editing a signature attribute."""

    name = wtforms.TextField(
        'Name',
        [name_validator, wtforms.validators.Required()])
    bio = wtforms.TextAreaField('Bio')
    effects = wtforms.TextAreaField(
        'Effects',
        [wtforms.validators.Required()])
    submit = wtforms.SubmitField('Submit')

class SigMoveForm(asb.forms.CSRFTokenForm):
    """A form for submitting or editing a signature move."""

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

def fill_attribute_form(form, mod):
    """Pre-fill the given SigAttributeForm with the data from mod."""

    form.name.data = mod.name
    form.bio.data = mod.description
    form.effects.data = mod.effect

@view_config(name='attribute', context=db.Pokemon, permission='sigattr.edit',
  request_method='GET', renderer='/sig_stuff/submit_sig_attribute.mako')
def modify_sig_attribute(pokemon, request):
    """A page for submitting or editing a signature attribute for approval."""

    form = SigAttributeForm(csrf_context=request.session)

    # Pre-fill the form if necessary
    if pokemon.body_modification:
        fill_attribute_form(form, pokemon.body_modification)

    return {'pokemon': pokemon, 'form': form}

def submit_sig_attribute(form, pokemon):
    """Process a request to submit a signature attribute for approval."""

    attribute = db.BodyModification(
        pokemon_id=pokemon.id,
        name=form.name.data,
        is_repeatable=False,  # what even is this
        description=form.bio.data,
        effect=form.effects.data)
    db.DBSession.add(attribute)

def edit_sig_attribute(form, attribute):
    """Process a request to edit a signature attribute pending approval."""

    attribute.name = form.name.data
    attribute.description = form.bio.data
    attribute.effect = form.effects.data

@view_config(name='attribute', context=db.Pokemon, permission='sigattr.edit',
  request_method='POST', renderer='/sig_stuff/submit_sig_attribute.mako')
def modify_sig_attribute_commit(pokemon, request):
    """
    Process a request to submit or edit a signature attribute for approval.
    """

    form = SigAttributeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    # Edit existing signature attribute
    if pokemon.body_modification:
        edit_sig_attribute(form, pokemon.body_modification)
    # Submit new signature attribute
    else:
        submit_sig_attribute(form, pokemon)

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#body-mod")

def fill_move_form(form, mod):
    """Prefill the given SigMoveForm with the data from mod."""

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

@view_config(name='move', context=db.Pokemon, permission='sigmove.edit',
  request_method='GET', renderer='/sig_stuff/submit_sig_move.mako')
def modify_sig_move(pokemon, request):
    """A page for submitting or editing a signature move for approval."""

    form = SigMoveForm(csrf_context=request.session)
    form.populate_form_choices()

    # Pre-fill the form if necessary
    if pokemon.move_modification:
        fill_move_form(form, pokemon.move_modification)

    return {'pokemon': pokemon, 'form': form}

def submit_sig_move(form, pokemon):
    """Process a request to submit a signature move for approval."""

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

def edit_sig_move(form, move):
    """Process a request to edit a signature move pending approval."""

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

@view_config(name='move', context=db.Pokemon, permission='sigmove.edit',
  request_method='POST', renderer='/sig_stuff/submit_sig_move.mako')
def modify_sig_move_commit(pokemon, request):
    """Process a request to submit or edit a signature move for approval."""

    form = SigMoveForm(request.POST, csrf_context=request.session)
    form.populate_form_choices()

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    # Edit an existing signature move
    if pokemon.move_modification:
        edit_sig_move(form, pokemon.move_modification)
    # Submit a new signature move
    else:
        submit_sig_move(form, pokemon)

    request.session.flash(
        "Success!  You'll need to paste the info from the text box below in "
        "the [something] thread to proceed with the approval process.")

    return httpexc.HTTPSeeOther(request.resource_url(pokemon) + "#move-mod")

class SigApprovalForm(wtforms.Form):
    """A form for approving or denying signature moves and attributes."""

    pass

class SigApprovalSubForm(wtforms.Form):
    """A form for approving or denying a single signature move or attribute."""

    approve = wtforms.SubmitField('Approve')
    deny = wtforms.SubmitField('Deny')

def sig_approval_form(sigs, *args, **kwargs):
    """
    Create and return a SigApprovalForm populated with SigApprovalSubForms
    for the items in sigs.
    """

    class SubForm(wtforms.Form):
        """A form to hold a bunch of SigApprovalSubForms."""

        pass

    for (i, sig_thing) in enumerate(sigs):
        class SubSubForm(SigApprovalSubForm):
            """A SigApprovalSubForm that holds the sig thing it's for."""

            sig = sig_thing

        setattr(SubForm, 'sig-{}'.format(i), wtforms.FormField(SubSubForm))

    class Form(SigApprovalForm):
        sigs = wtforms.FormField(SubForm)

    return Form(*args, **kwargs)

def sig_attribute_approval_form(user, *args, **kwargs):
    """
    Create and return a SigApprovalForm populated with SigApprovalSubForms for
    signature attributes.
    """

    attributes = (
        db.DBSession.query(db.BodyModification)
        .filter_by(needs_approval=True)
        .all())

    # Filter out the user's own submitted attributes
    attributes = [att for att in attributes
                  if att.pokemon.trainer_id != user.id]

    return sig_approval_form(attributes, *args, **kwargs)

def sig_move_approval_form(user, *args, **kwargs):
    """
    Create and return a SigApprovalForm populates with SigApprovalSubForms for
    signature moves.
    """

    moves = (
        db.DBSession.query(db.MoveModification)
        .filter_by(needs_approval=True)
        .all())

    # Filter out the user's own submitted attributes
    moves = [move for move in moves if move.pokemon.trainer_id != user.id]

    return sig_approval_form(moves, *args, **kwargs)

@view_config(name='approve-move', permission='sigmove.approve',
  request_method='GET', renderer='/sig_stuff/sig_move_approve.mako')
def approve_sig_move(context, request):
    """The signature move approving page."""

    return {'form': sig_move_approval_form(request.user)}

@view_config(name='approve-move', permission='sigmove.approve',
    request_method='POST', renderer='/sig_stuff/sig_move_approve.mako')
def approve_sig_move_commit(context, request):
    """Process a request to approve or deny a signature move."""

    form = sig_move_approval_form(request.user, request.POST)

    for subform in form.sigs:
        # Approve; just change the approval flag
        if subform.approve.data:
            subform.sig.needs_approval = False
            request.session.flash('Success! "{}"" has been approved.'.format(
                subform.sig.name))

        # Deny; delete from the database
        # TODO: probably don't delete altogether
        elif subform.deny.data:
            db.DBSession.delete(subform.sig)
            request.session.flash('Success! "{}" has been denied.'.format(
                subform.sig.name))

    return {'form': sig_move_approval_form(request.user)}

@view_config(name='approve-attribute', permission='sigattr.approve',
  request_method='GET', renderer='/sig_stuff/sig_attribute_approve.mako')
def approve_sig_attribute(context, request):
    """The signature attribute approving page."""

    return {'form': sig_attribute_approval_form(request.user)}

@view_config(name='approve-attribute', permission='sigattr.approve',
    request_method='POST', renderer='/sig_stuff/sig_attribute_approve.mako')
def approve_sig_attribute_commit(context, request):
    """Process a request to approve or deny a signature attribute."""

    form = sig_attribute_approval_form(request.user, request.POST)

    for subform in form.sigs:
        # Approve; just change the approval flag
        if subform.approve.data:
            subform.sig.needs_approval = False
            request.session.flash("Success! {} has been approved.".format(
                subform.sig.name))

        # Deny; delete from the database
        # TODO: probably don't delete altogether
        elif subform.deny.data:
            db.DBSession.delete(subform.sig)
            request.session.flash('Success! "{}" has been denied.'.format(
                subform.sig.name))

    return {'form': sig_attribute_approval_form(request.user)}


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
        [name_validator, wtforms.validators.Required()])
    description = wtforms.TextAreaField(
        'Description',
        [wtforms.validators.Required()])
    move_type = wtforms.SelectField('Type', coerce=int)
    damage_class = wtforms.SelectField('Damage Class', coerce=int)
    bp = wtforms.IntegerField(
        'Base Power',
        validators=[wtforms.validators.NumberRange(min=0)])
    energy = wtforms.IntegerField(
        'Energy Cost',
        validators=[wtforms.validators.NumberRange(min=1)])
    accuracy = wtforms.IntegerField(
        'Accuracy',
        validators=[wtforms.validators.NumberRange(min=0)])
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
        self.move_type.choices = [(t.id, t.name) for t in types]

        damage_classes = db.DBSession.query(db.DamageClass).all()
        self.damage_class.choices = [(c.id, c.name.capitalize())
                                     for c in damage_classes]

        targets = db.DBSession.query(db.MoveTarget).all()
        self.target.choices = [(t.id, t.name) for t in targets]


@view_config(name='attribute', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='submit_sig_attribute.mako')
def submit_sig_attribute(pokemon, request):
    """A page for submitting a signature attribute for approval."""

    form = SigAttributeForm(csrf_context=request.session)

    return {'pokemon': pokemon, 'form': form}

@view_config(name='attribute', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='submit_sig_attribute.mako')
def submit_sig_attribute_commit(pokemon, request):
    """Process a request to submit a signature attribute for approval."""

    form = SigAttributeForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    # Do stuff

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

@view_config(name='move', context=db.Pokemon, permission='edit.basics',
  request_method='GET', renderer='submit_sig_move.mako')
def submit_sig_move(pokemon, request):
    """A page for submitting a signature move for approval."""

    form = SigMoveForm(csrf_context=request.session)
    form.populate_form_choices()

    return {'pokemon': pokemon, 'form': form}

@view_config(name='move', context=db.Pokemon, permission='edit.basics',
  request_method='POST', renderer='submit_sig_move.mako')
def submit_sig_move_commit(pokemon, request):
    """Process a request to submit a signature move for approval."""

    form = SigMoveForm(request.POST, csrf_context=request.session)
    form.populate_form_choices()

    if not form.validate():
        return {'pokemon': pokemon, 'form': form}

    # Do stuff

    return httpexc.HTTPSeeOther(request.resource_url(pokemon))

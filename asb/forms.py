"""Some reusable WTForms bits."""

import unicodedata

import sqlalchemy as sqla
import wtforms
import wtforms.ext.csrf

from asb import db
import asb.markup
import asb.tcodf

class CSRFTokenForm(wtforms.ext.csrf.SecureForm):
    """A SecureForm that requires a Pyramid session for its CSRF context."""

    def generate_csrf_token(self, session):
        """Get the session's CSRF token."""

        return session.get_csrf_token()

    def validate_csrf_token(form, field):
        """Validate the CSRF token."""

        if field.data != field.current_token:
            raise wtforms.validators.ValidationError(
                'Invalid CSRF token; the form probably expired.  Try again.')

class TextAreaField(wtforms.TextAreaField):
    r"""A TextAreaField that replaces '\r\n' newlines with '\n'.

    '\r\n' is what HTTP mandates; we don't have to worry about plain '\r'.
    """

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[0].replace('\r\n', '\n')

class MarkupFormatField(wtforms.RadioField):
    """A set of radio buttons for choosing a markup language."""

    def __init__(self, *args, choices=(), **kwargs):
        if not choices:
            choices = [
                (language, language.value)
                for language in asb.markup.MarkupLanguage
            ]

        kwargs.setdefault('default', asb.markup.MarkupLanguage.bbcode)
        kwargs.setdefault('coerce', self.coerce)

        super().__init__(*args, choices=choices, **kwargs)

    def coerce(self, value):
        """Coerce a string back to a MarkupLanguage or None.

        Don't coerce any other type; form data and default values added on the
        Python end are both passed through here.
        """

        # XXX It would be nice to use process_formdata instead and avoid
        # checking type, but then the format is left unselected when previewing
        # fsr.

        if isinstance(value, str):
            if value:
                return asb.markup.MarkupLanuage[value]
            else:
                return None

        return value

class MultiCheckboxField(wtforms.SelectMultipleField):
    """A SelectMultipleField that presents its options as checkboxes.

    Lifted from the WTForms docs, at the bottom of "Solving Specific Problems":
    http://wtforms.readthedocs.org/en/latest/specific_problems.html
    """

    widget = wtforms.widgets.ListWidget(prefix_label=False)
    option_widget = wtforms.widgets.CheckboxInput()

class ButtonSubmitInput(wtforms.widgets.Input):
    """A <button type="submit">."""

    def __call__(self, field, **kwargs):
        return wtforms.widgets.HTMLString(
            '<button {params}>{label}</button>'.format(
                params=wtforms.widgets.html_params(
                    type='submit',
                    name=field.name,
                    value=field.data,
                    **kwargs
                ),

                label=field.label.text
            )
        )

class MultiSubmitField(wtforms.SelectField):
    """A SelectField that presents its options as submit buttons."""

    widget = wtforms.widgets.ListWidget(prefix_label=False)
    option_widget = ButtonSubmitInput()

class PostLinkField(wtforms.TextField):
    """A text field for a link to a post on the forums that parses and stores
    the post ID as part of validation.
    """

    post_id = None

    def pre_validate(self, form):
        try:
            self.post_id = asb.tcodf.post_id(self.data)
        except ValueError as error:
            self.errors.append('Invalid link ({0})'.format(error))

class TrainerField(wtforms.StringField):
    """A string field that also fetches the registered trainer with that name,
    if any, from the database.
    """

    trainer = None

    def process_formdata(self, valuelist):
        [self.data] = valuelist

        try:
            self.trainer = (
                db.DBSession.query(db.Trainer)
                .filter(sqla.func.lower(db.Trainer.name) == self.data.lower())
                .filter_by(unclaimed_from_hack=False)
                .options(sqla.orm.joinedload('ban'))
                .one()
            )
        except sqla.orm.exc.NoResultFound:
            pass

class PokemonSpeciesField(wtforms.StringField):
    """A field for a Pokémon species that also fetches the corresponding
    species from the database.

    When I get lookup working, it will replace this.
    """

    def _value(self):
        """Retrieve the original input string from the (input, species)
        tuple.
        """

        if self.data:
            return self.data[0]
        else:
            return ''

    def process_data(self, value):
        """Store the (input, species) tuple given just a species."""

        if value is None:
            self.data = ('', None)
        else:
            self.data = (value.name, value)

    def process_formdata(self, valuelist):
        """Take the initial string input and retrieve the corresponding
        species, if possible.  Store both as an (input, species) tuple.
        """

        [name] = valuelist

        try:
            identifier = db.helpers.identifier(name)
        except ValueError:
            # Reduces to empty identifier; obviously not going to be a species
            self.data = (name, None)
            return

        # Deal with the Nidorans
        if identifier in ['nidoran-female', 'nidoranf']:
            identifier = 'nidoran-f'
        elif identifier in ['nidoran-male', 'nidoranm']:
            identifier = 'nidoran-m'

        # Try to fetch the species
        try:
            species = (
                db.DBSession.query(db.PokemonSpecies)
                .filter_by(identifier=identifier)
                .options(sqla.orm.joinedload('default_form'))
                .one()
            )

            self.data = (name, species)
        except sqla.orm.exc.NoResultFound:
            self.data = (name, None)

def name_validator(form, field):
    """Validate a Pokémon or trainer name."""

    name = field.data

    # Check name length; saves having to add a Length validator separately
    if len(name) > 30:
        raise wtforms.validators.ValidationError('Maximum thirty characters.')

    # Check for weird characters that are very unlikely to be used legitimately
    for character in name:
        category = unicodedata.category(character)

        if category.startswith('M'):
            raise wtforms.validators.ValidationError(
                'Combining characters are not allowed.')
        elif category.startswith('C') or category in ['Zl', 'Zp']:
            raise wtforms.validators.ValidationError(
                'Printable characters only please.')

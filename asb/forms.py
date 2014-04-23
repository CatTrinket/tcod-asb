"""Some reusable WTForms bits."""

import unicodedata

import wtforms
import wtforms.ext.csrf

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

class MultiCheckboxField(wtforms.SelectMultipleField):
    """A SelectMultipleField that presents its options as checkboxes.

    Lifted from the WTForms docs, at the bottom of "Solving Specific Problems":
    http://wtforms.readthedocs.org/en/latest/specific_problems.html
    """

    widget = wtforms.widgets.ListWidget(prefix_label=False)
    option_widget = wtforms.widgets.CheckboxInput()

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

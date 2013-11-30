"""Some reusable WTForms bits."""

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

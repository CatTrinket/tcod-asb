import datetime
import email.headerregistry
import email.mime.text
import random
import smtplib

import pyramid.httpexceptions as httpexc
import pyramid.security
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

import asb.db as db
import asb.forms


email_template = """\
You can reset your password at: http://asb.dragonflycave.com/reset-password/{0}

This link will work for one hour.  If you didn't request a password reset, \
then someone else is probably just being a pest and you can safely ignore \
this email.
"""

class PasswordResetRequestForm(asb.forms.CSRFTokenForm):
    """A form for requesting a password reset."""

    username = asb.forms.TrainerField('Username')
    submit = wtforms.SubmitField('Submit')

    def validate_username(form, field):
        """Make sure we got a valid user."""

        trainer = field.trainer

        if trainer is None:
            # Make sure we got a user
            raise wtforms.validators.ValidationError('Unknown username')
        elif trainer.ban is not None:
            # Make sure they're not banned
            raise wtforms.validators.ValidationError(
                'You have been banned by {0} for the following reason: {1}'
                .format(trainer.ban.banned_by.name, trainer.ban.reason)
            )
        elif not trainer.email:
            # Make sure they have an email address set
            raise wtforms.validators.ValidationError(
                'No email address for that username.  PM Trinket to get '
                'things sorted out.'
            )
        else:
            # Check if they've already sent three password requests today
            midnight = (datetime.datetime.utcnow()
                        .replace(hour=0, minute=0, second=0, microsecond=0))

            recent_requests = (
                db.DBSession.query(db.PasswordResetRequest)
                .filter_by(trainer_id=trainer.id)
                .filter(db.PasswordResetRequest.timestamp >= midnight)
                .count()
            )

            if recent_requests >= 3:
                raise wtforms.validators.ValidationError(
                    'You can only send three password reset requests per day.'
                )

class PasswordResetForm(asb.forms.CSRFTokenForm):
    """A form for actually resetting one's password."""

    new_password = wtforms.PasswordField(
        'New password',
        [wtforms.validators.InputRequired("Your password can't be empty")]
    )

    confirm_password = wtforms.PasswordField(
        'Confirm',
        [wtforms.validators.EqualTo('new_password', "Passwords don't match")]
    )

    submit = wtforms.SubmitField('Submit')

def new_token():
    """Generate a new password reset token."""

    return ''.join(
        random.choice('abcdefghijklmnopqrstuvwxyz'
                      'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                      '012346789')
        for n in range(32)
    )


### Requesting a password reset

@view_config(route_name='reset-password',
             renderer='/reset_password/request.mako', request_method='GET')
def reset_password_request(context, request):
    """The password reset request page."""

    return {'form': PasswordResetRequestForm(csrf_context=request.session)}

@view_config(route_name='reset-password',
             renderer='/reset_password/request.mako', request_method='POST')
def reset_password_request_process(context, request):
    """Process a password reset request."""

    # Process form
    form = PasswordResetRequestForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    trainer = form.username.trainer

    # Add a password reset token
    pw_request = db.PasswordResetRequest(
        trainer_id=trainer.id,
        token=new_token()
    )
    db.DBSession.add(pw_request)

    # Send it
    # XXX Pull all this info from config, and also figure out how to format
    #     weird usernames/emails in the "To" field
    message = email.mime.text.MIMEText(email_template.format(pw_request.token))
    message['Subject'] = 'TCoD ASBdb password reset'
    message['From'] = ('The Cave of Dragonflies ASB Database '
                       '<tcod-asb@catseyemarble.com>')
    message['Reply-To'] = 'Trinket <trinket@catseyemarble.com>'
    message['To'] = str(email.headerregistry.Address(
        trainer.name, addr_spec=trainer.email))

    with smtplib.SMTP('localhost') as smtp:
        smtp.sendmail('tcod-asb@catseyemarble.com', [trainer.email],
                      message.as_string())

    return httpexc.HTTPSeeOther('/reset-password/sent')

@view_config(route_name='reset-password.sent',
             renderer='/reset_password/sent.mako')
def reset_password_sent(context, request):
    """A simple "an email has been sent" page."""

    return {}


### Resetting the password

def fetch_reset_request(token):
    """Fetch the password reset request corresponding to the given token, and
    make sure it hasn't expired.
    """

    # Fetch the request corresponding to this token
    try:
        pw_request = (
            db.DBSession.query(db.PasswordResetRequest)
            .filter_by(token=token)
            .one()
        )
    except sqla.orm.exc.NoResultFound:
        raise httpexc.HTTPNotFound('Invalid token')

    # Make sure it hasn't expired
    expired = (
        pw_request.completed or
        datetime.datetime.utcnow() - pw_request.timestamp >
            datetime.timedelta(hours=1)
    )

    if expired:
        raise httpexc.HTTPForbidden('Expired token')

    # Whoop
    return pw_request

@view_config(route_name='reset-password.reset',
             renderer='/reset_password/reset.mako', request_method='GET')
def reset_password(context, request):
    """A page for actually resetting one's password."""

    # We don't actually need it but we need to fetch it to make sure it's valid
    fetch_reset_request(request.matchdict['token'])

    return {'form': PasswordResetForm(csrf_context=request.session)}

@view_config(route_name='reset-password.reset',
             renderer='/reset_password/reset.mako', request_method='POST')
def reset_password_process(context, request):
    """Reset someone's password."""

    pw_request = fetch_reset_request(request.matchdict['token'])
    form = PasswordResetForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    # Reset their password
    pw_request.trainer.set_password(form.new_password.data)
    pw_request.completed = True

    # Log them in
    headers = pyramid.security.remember(request, pw_request.trainer.id)
    request.session.flash('Welcome back, {0}!'.format(pw_request.trainer.name))

    return httpexc.HTTPSeeOther('/', headers=headers)

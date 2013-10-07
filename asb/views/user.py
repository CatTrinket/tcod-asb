import pbkdf2
import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
import transaction
import wtforms

import asb.models as models

class UsernameField(wtforms.StringField):
    def _value(self):
        if self.data:
            return self.data[0]
        else:
            return ''

    def process_formdata(self, valuelist):
        username, = valuelist

        try:
            trainer = (models.DBSession.query(models.Trainer)
                .filter_by(name=username)
                .one()
            )

            self.data = (username, trainer)
        except NoResultFound:
            self.data = (username, None)

class RegistrationForm(wtforms.Form):
    what_do = wtforms.RadioField(
        'What would you like to do?',

        [wtforms.validators.InputRequired(
            'How did you manage to select neither?')],

        default='new',
        choices=[
           ('new', 'Create a new profile'),
           ('old', 'Recover an old profile from the vB hack')
        ],
    )

    username = UsernameField('TCoD forum username',
        [wtforms.validators.InputRequired('Please enter your username')])
    password = wtforms.PasswordField('Choose a password',
        [wtforms.validators.InputRequired("Your password can't be empty")])
    password_confirm = wtforms.PasswordField('Confirm')
    email = wtforms.StringField('Email (optional)')
    submit = wtforms.SubmitField('Register')

    def validate_password_confirm(form, field):
        """Make sure the passwords match."""

        if field.data != form.password.data:
            raise wtforms.validators.ValidationError("Passwords don't match")

    def validate_username(form, field):
        """Depending on whether the person registering is trying to create a
        new profile or reclaim an old one, make sure we did or didn't find a
        preexisting trainer as appropriate.
        """

        username, user = field.data

        # Make sure they're not trying to register as an already-registered user
        if user is not None and not user.unclaimed_from_hack:
            raise wtforms.validators.ValidationError(
                'The username {0} has already been registered.  If someone '
                'else is using your username, contact an ASB mod.'
                .format(username))

        # If they're trying to reclaim an old profile, make sure we actually
        # found that profile
        if form.what_do.data == 'old' and user is None:
            raise wtforms.validators.ValidationError(
                "No profile found for the username {0}.  If double-checking "
                "the spelling and trying previous usernames doesn't work, "
                "contact Zhorken.".format(username))

@view_config(route_name='register', renderer='/register.mako',
  request_method='GET')
def Register(context, request):
    return {'form': RegistrationForm()}

@view_config(route_name='register', renderer='/register.mako',
  request_method='POST')
def RegisterCommit(context, request):
    session = models.DBSession()

    form = RegistrationForm(request.POST)

    if not form.validate():
        return {'form': form}

    username, user = form.username.data

    if user is not None:
        # Update the old user
        # XXX user.id = nextval should work but doesn't; not my fault
        nextval = models.Trainer.trainers_id_seq.next_value()
        id, = select([nextval]).execute().fetchone()

        user.id = id
        user.unclaimed_from_hack = False
    else:
        # Create a new user
        identifier = 'temp-{0}'.format(username)
        user = models.Trainer(name=username, identifier=identifier)
        session.add(user)

    session.flush()
    user.set_password(form.password.data)
    user.update_identifier()
    transaction.commit()

    return httpexc.HTTPSeeOther('/register/done')

@view_config(route_name='register_done', renderer='/registered.mako')
def RegisterDone(context, request):
    return {}

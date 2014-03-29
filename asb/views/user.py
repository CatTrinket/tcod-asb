import pbkdf2
import pyramid.httpexceptions as httpexc
import pyramid.security
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
import transaction
import wtforms

from asb import db
from asb.forms import CSRFTokenForm

def get_user(request):
    """Get the logged-in user or a request."""

    id = pyramid.security.unauthenticated_userid(request)

    if id is None:
        return None

    try:
        user = (db.DBSession.query(db.Trainer)
            .filter_by(id=id)
            .one()
        )
    except NoResultFound:
        return None

    return user

def get_user_roles(userid, request):
    # XXX get DB ones

    try:
        user = (db.DBSession.query(db.Trainer)
            .filter_by(id=userid)
            .one()
        )
    except NoResultFound:
        return None

    roles = ['user:{0}'.format(userid)]

    return roles

class UsernameField(wtforms.StringField):
    """A username field that also fetches the corresponding user, if any, from
    the database.
    """

    def _value(self):
        if self.data:
            return self.data[0]
        else:
            return ''

    def process_formdata(self, valuelist):
        username, = valuelist

        try:
            trainer = (db.DBSession.query(db.Trainer)
                .filter_by(name=username)
                .one()
            )

            self.data = (username, trainer)
        except NoResultFound:
            self.data = (username, None)

class LoginForm(CSRFTokenForm):
    """A login form, used both at the top of every page and on /login."""

    username = UsernameField('Username')
    password = wtforms.PasswordField('Password')
    log_in = wtforms.SubmitField('Log in')

    # n.b. we don't want the username and password fields to present separate
    # errors to the user because that might look like a security risk to the
    # average person (even though there's a public userlist)
    def validate_username(form, field):
        """Make sure we actually found a current user for this username."""

        username, user = field.data

        if user is None or user.unclaimed_from_hack:
            raise wtforms.validators.ValidationError

    def validate_password(form, field):
        """If we got a valid user, check their password against the password
        we got.
        """

        username, user = form.username.data

        if user is None or user.unclaimed_from_hack:
            # The username field will raise an error; there's no sensible
            # second error to be raised here
            return None

        if not user.check_password(field.data):
            raise wtforms.validators.ValidationError

class RegistrationForm(CSRFTokenForm):
    """A registration form."""

    what_do = wtforms.RadioField(
        'What would you like to do?',

        [wtforms.validators.InputRequired(
            'Please select one of these options.')],

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
def register(context, request):
    """Return a blank registration form."""

    return {'form': RegistrationForm(csrf_context=request.session)}

@view_config(route_name='register', renderer='/register.mako',
  request_method='POST')
def register_commit(context, request):
    """Process a registration form.  Send the user back to the form if there
    are any errors; create their account otherwise.
    """

    session = db.DBSession()

    form = RegistrationForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    username, user = form.username.data

    if user is not None:
        # Update the old user
        # XXX user.id = nextval should work but doesn't; not my fault
        nextval = db.Trainer.trainers_id_seq.next_value()
        id, = select([nextval]).execute().fetchone()

        user.id = id
        user.unclaimed_from_hack = False

        # Same with all their Pokémon
        if form.what_do.data == 'old':
            nextval = select([db.Pokemon.pokemon_id_seq.next_value()])

            for pokemon in user.pokemon:
                id, = nextval.execute().fetchone()
                pokemon.id = id
                pokemon.unclaimed_from_hack = False

                session.flush()
                pokemon.update_identifier()
    else:
        # Create a new user
        identifier = 'temp-{0}'.format(username)
        user = db.Trainer(name=username, identifier=identifier)
        session.add(user)

    session.flush()
    user.set_password(form.password.data)
    user.update_identifier()
    transaction.commit()

    return httpexc.HTTPSeeOther('/')

@view_config(route_name='login', renderer='/login.mako',
  request_method='GET')
def login_page(context, request):
    """Return a blank login form in the unlikely event that anyone ever GETs
    /login.
    """

    return {'form': LoginForm(csrf_context=request.session)}

@view_config(route_name='login', renderer='/login.mako',
  request_method='POST')
def login(context, request):
    """Process a login form."""

    form = LoginForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    username, user = form.username.data
    headers = pyramid.security.remember(request, user.id)

    return httpexc.HTTPSeeOther('/', headers=headers)

@view_config(route_name='logout')
def logout(context, request):
    if request.params['csrf_token'] == request.session.get_csrf_token():
        headers = pyramid.security.forget(request)
        return httpexc.HTTPSeeOther('/', headers=headers)
    else:
        # what do I do
        request.session.flash('Invalid CSRF token; the logout link probably '
            'expired.  Try again.')

        return httpexc.HTTPSeeOther('/')

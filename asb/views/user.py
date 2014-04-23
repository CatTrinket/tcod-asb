import datetime

import pbkdf2
import pyramid.httpexceptions as httpexc
import pyramid.security
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql import select
import transaction
import wtforms

from asb import db
import asb.forms

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

class LoginForm(asb.forms.CSRFTokenForm):
    """A login form, used both at the top of every page and on /login."""

    username = UsernameField('Username', [asb.forms.name_validator])
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

class RegistrationForm(asb.forms.CSRFTokenForm):
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
        [wtforms.validators.InputRequired('Please enter your username'),
         wtforms.validators.length(max=30)])
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
        id, = db.DBSession.execute(select([nextval])).fetchone()

        user.id = id
        user.unclaimed_from_hack = False

        # Same with all their Pokémon
        if form.what_do.data == 'old':
            nextval = select([db.Pokemon.pokemon_id_seq.next_value()])

            for pokemon in user.pokemon:
                id, = db.DBSession.execute(nextval).fetchone()
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


### BANK STUFF

class AllowanceForm(asb.forms.CSRFTokenForm):
    """A simple form for collecting allowance."""

    collect = wtforms.SubmitField('Collect allowance')

def can_collect_allowance(trainer):
    """Return whether or not this trainer can collect allowance."""

    # If they've never collected allowance, then of course they can!
    if trainer.last_collected_allowance is None:
        return True

    # Find the most recent Friday, possibly today.  Subtracting the weekday
    # brings us back to Monday; three days further is Friday; modulo one week.
    today = datetime.date.today()
    last_friday = today - datetime.timedelta(days=(today.weekday() + 3) % 7)

    return trainer.last_collected_allowance < last_friday

@view_config(route_name='bank', request_method='GET', renderer='/bank.mako',
  permission='manage-account')
def bank(context, request):
    """The bank page."""

    if can_collect_allowance(request.user):
        allowance_form = AllowanceForm(csrf_context=request.session)
    else:
        allowance_form = None

    return {'allowance_form': allowance_form}

@view_config(route_name='bank', request_method='POST', renderer='/bank.mako',
  permission='manage-account')
def bank_process(context, request):
    """Give the trainer their allowance, if they haven't already collected it
    this week.
    """

    trainer = request.user

    if not can_collect_allowance(trainer):
        raise httpexc.HTTPForbidden(
            "You've already collected this week's allowance!")

    form = AllowanceForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'allowance_form': form}

    trainer.money += 3
    trainer.last_collected_allowance = datetime.date.today()

    return httpexc.HTTPSeeOther('/bank')

import datetime

import pbkdf2
import pyramid.httpexceptions as httpexc
import pyramid.security
from pyramid.view import view_config
import sqlalchemy as sqla
import sqlalchemy.orm
import wtforms

from asb import db
import asb.forms
import asb.tcodf

def get_user(request):
    """Get the logged-in user for a request."""

    id = pyramid.security.unauthenticated_userid(request)

    if id is None:
        return None

    user = (
        db.DBSession.query(db.Trainer)
        .options(sqla.orm.joinedload('ban'))
        .get(id)
    )

    if user.ban is not None:
        request.session.flash(
            'You have been banned by {0} for the following reason: {1}'
            .format(user.ban.banned_by.name, user.ban.reason)
        )
        request.response.headers.extend(pyramid.security.forget(request))
        return None

    return user

def get_user_roles(userid, request):
    """Get a user's roles for Pyramid authorization."""

    try:
        user = (
            db.DBSession.query(db.Trainer)
            .filter_by(id=userid)
            .options(sqla.orm.subqueryload('roles'))
            .one()
        )
    except sqla.orm.exc.NoResultFound:
        return None

    roles = [role.identifier for role in user.roles]
    roles.append('user:{}'.format(userid))

    if user.is_validated:
        roles.append('validated')

    return roles

class LoginForm(asb.forms.CSRFTokenForm):
    """A login form, used both at the top of every page and on /login."""

    username = asb.forms.TrainerField('Username')
    password = wtforms.PasswordField('Password')
    log_in = wtforms.SubmitField('Log in')

    # n.b. we don't want the username and password fields to present separate
    # errors to the user because that might look like a security risk to the
    # average person (even though there's a public userlist)
    def validate_username(form, field):
        """Check that we got a valid user."""

        trainer = field.trainer

        if trainer is None:
            raise wtforms.validators.ValidationError(
                'Invalid username or password'
            )
        elif trainer.ban is not None:
            raise wtforms.validators.ValidationError(
                'You have been banned by {0} for the following reason: {1}'
                .format(trainer.ban.banned_by.name, trainer.ban.reason)
            )

    def validate_password(form, field):
        """If we got a valid user, check their password against the password
        we got.
        """

        trainer = form.username.trainer

        if trainer is None:
            # The username field will raise an error; there's no sensible
            # second error to be raised here
            return None

        if not trainer.check_password(field.data):
            raise wtforms.validators.ValidationError(
                'Invalid username or password'
            )

class RegistrationForm(asb.forms.CSRFTokenForm):
    """A registration form."""

    username = asb.forms.TrainerField('TCoD forum username',
        [wtforms.validators.InputRequired(), asb.forms.name_validator])
    password = wtforms.PasswordField('Choose a password',
        [wtforms.validators.InputRequired("Your password can't be empty")])
    password_confirm = wtforms.PasswordField('Confirm')
    email = wtforms.StringField('Email (optional)',
        [wtforms.validators.Optional(), wtforms.validators.Email(),
            wtforms.validators.Length(max=60)])
    submit = wtforms.SubmitField('Register')

    def validate_password_confirm(form, field):
        """Make sure the passwords match."""

        if field.data != form.password.data:
            raise wtforms.validators.ValidationError("Passwords don't match")

    def validate_username(form, field):
        """Make sure they're not trying to register as an already-registered
        trainer.
        """

        if field.trainer is not None:
            raise wtforms.validators.ValidationError(
                'The username {0} has already been registered.  If someone '
                'else is using your username, contact an ASB mod.'
                .format(field.data)
            )

class ResetAccountForm(asb.forms.CSRFTokenForm):
    """A form for resetting or deleting one's account, and making sure the user
    is doing so on purpose.
    """

    confirmation = 'I understand and wish to reset or delete my account.'

    i_understand = wtforms.TextField('Sentence', validators=[
        wtforms.validators.AnyOf([confirmation],
            'Please enter the sentence exactly as shown.')
    ])

    # Weird name so as not to clash with the password field on SettingsForm.
    # Validated later to avoid having to pass the user object around.
    reset_pass = wtforms.PasswordField('Password')

    reset = wtforms.SubmitField('Reset account')
    delete = wtforms.SubmitField('Delete account')

class SettingsForm(asb.forms.CSRFTokenForm):
    """A settings form."""

    # These three fields *together* are optional — they must be all filled out,
    # or all blank.  This is super annoying to write as a validator, so we just
    # check that manually later.
    password = wtforms.PasswordField('Current password')
    new_password = wtforms.PasswordField('New password',
        [wtforms.validators.Optional()])
    new_password_confirm = wtforms.PasswordField('Confirm new password',
        [wtforms.validators.EqualTo('new_password', "Passwords don't match")])
    email = wtforms.TextField('Email',
        [wtforms.validators.Optional(), wtforms.validators.Email(),
            wtforms.validators.Length(max=60)])

    save = wtforms.SubmitField('Save')

class UpdateUsernameForm(asb.forms.CSRFTokenForm):
    """A single button to tell the app to check the user's TCoDf profile and
    update their username to match it.
    """

    update_username = wtforms.SubmitField('Poink!')

class UserLinkField(wtforms.StringField):
    """A field for a forum profile link that also retrieves profile info."""

    tcodf_user_id = None
    preexisting_trainer = None
    tcodf_user_info = None

    def process_formdata(self, valuelist):
        """Process form data, and also retreive profile info."""

        [self.data] = valuelist
        self.tcodf_user_id = asb.tcodf.user_id(self.data)
        self.tcodf_user_info = asb.tcodf.user_info(self.tcodf_user_id)

        # See if there's already a trainer with this TCoDf ID
        try:
            self.preexisting_trainer = (
                db.DBSession.query(db.Trainer)
                .filter_by(tcodf_user_id=self.tcodf_user_id)
                .one()
            )
        except sqla.orm.exc.NoResultFound:
            pass

    def pre_validate(self, form):
        """Make sure nobody else has already validated using this forum
        account.

        Yes, we also have to check that the right profile link is in the right
        place, but we do that elsewhere to avoid having to pass the user id all
        over.
        """

        if (self.preexisting_trainer is not None and not
          self.preexisting_trainer.unclaimed_from_hack):
            raise wtforms.validators.ValidationError('That forum account is '
                'already associated with an ASB profile')

class ValidationForm(asb.forms.CSRFTokenForm):
    """An account validation form."""

    profile_link = UserLinkField(validators=[wtforms.validators.Required()])
    submit = wtforms.SubmitField('Validate')

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

    form = RegistrationForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    # Create a new user
    username = form.username.data
    identifier = 'temp-{0}'.format(username)
    user = db.Trainer(
        name=username,
        identifier=identifier,
        email=form.email.data
    )

    db.DBSession.add(user)
    db.DBSession.flush()  # Set their ID

    user.set_password(form.password.data)
    user.update_identifier()

    # Log them in
    headers = pyramid.security.remember(request, user.id)

    return httpexc.HTTPSeeOther('/validate', headers=headers)

@view_config(route_name='validate', renderer='/validate.mako',
  permission='account.validate', request_method='GET')
def validate_page(context, request):
    """The validation page."""

    return {'form': ValidationForm(csrf_context=request.session)}

@view_config(route_name='validate', renderer='/validate.mako',
  permission='account.validate', request_method='POST')
def validate(context, request):
    """Validate a user, and give them back their old profile if applicable."""

    form = ValidationForm(request.POST, csrf_context=request.session)
    return_dict = {'form': form}

    if not form.validate():
        return return_dict

    trainer = request.user
    old_trainer = form.profile_link.preexisting_trainer
    info = form.profile_link.tcodf_user_info

    # Check the profile link, but be lenient about the slug
    link = info['profile_link']

    if link is None:
        form.profile_link.errors.append("Couldn't find an ASB profile link on "
            "that forum profile")
        return return_dict
    else:
        path, sep, slug = info['profile_link'].path.partition('-')

        if path != '/trainers/{}'.format(trainer.id):
            form.profile_link.errors.append('Found an ASB link on that forum '
                "profile, but it's the wrong link")
            return return_dict

    if old_trainer:
        # We found an old profile from the vB hack — replace this user with it
        id = trainer.id
        identifier = trainer.identifier
        old_trainer.password_hash = trainer.password_hash
        old_trainer.name = trainer.name

        db.DBSession.delete(trainer)
        db.DBSession.flush()

        trainer = old_trainer
        trainer.id = id
        trainer.identifier = identifier
        trainer.unclaimed_from_hack = False

        # Update all their Pokémon's IDs
        for pokemon in trainer.pokemon:
            pokemon.id = db.DBSession.execute(asb.db.Pokemon.pokemon_id_seq)
            pokemon.birthday = datetime.datetime.utcnow().date()
            pokemon.update_identifier()

    username = info['username']

    if trainer.name != username:
        request.session.flash('Your username has been updated to match your '
            'forum profile.')
        trainer.name = username
        trainer.update_identifier()

    trainer.tcodf_user_id = form.profile_link.tcodf_user_id
    trainer.is_validated = True

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

    headers = pyramid.security.remember(request, form.username.trainer.id)

    return httpexc.HTTPSeeOther('/', headers=headers)

@view_config(route_name='logout')
def logout(context, request):
    if request.params['csrf_token'] == request.session.get_csrf_token():
        headers = pyramid.security.forget(request)
        return httpexc.HTTPSeeOther('/', headers=headers)
    else:
        request.session.flash('Invalid CSRF token; the logout link probably '
            'expired.  Try again.')

        return httpexc.HTTPSeeOther('/')

@view_config(route_name='settings', renderer='/settings.mako',
  permission='account.manage', request_method='GET')
def settings(context, request):
    """The settings page."""

    settings = SettingsForm(csrf_context=request.session)
    settings.email.data = request.user.email

    return {
        'update_username': UpdateUsernameForm(csrf_context=request.session),
        'settings': settings,
        'reset_delete': ResetAccountForm(csrf_context=request.session)
    }

@view_config(route_name='settings', renderer='/settings.mako',
  permission='account.manage', request_method='POST')
def settings_process(context, request):
    """Process any of the various forms on the settings page."""

    update_username = UpdateUsernameForm(request.POST,
        csrf_context=request.session)
    settings = SettingsForm(request.POST, csrf_context=request.session)
    reset_delete = ResetAccountForm(request.POST, csrf_context=request.session)

    trainer = request.user
    return_dict = {
        'update_username': update_username,
        'settings': settings,
        'reset_delete': reset_delete
    }

    if update_username.update_username.data:
        if not update_username.validate():
            return return_dict

        # Try to update their username
        try:
            info = asb.tcodf.user_info(trainer.tcodf_user_id)
        except ValueError:
            update_username.update_username.errors.append('Something went '
                'wrong checking your forum profile; try again later')
            return return_dict

        trainer.name = info['username']
        trainer.update_identifier()
    elif settings.save.data:
        if not settings.validate():
            return return_dict

        # Check their password, since we don't do this with a validator
        if not trainer.check_password(settings.password.data):
            settings.password.errors.append('Current password incorrect')
            return return_dict

        if settings.new_password.data:
            trainer.set_password(settings.new_password.data)

        if settings.email.data:
            trainer.email = settings.email.data
    elif reset_delete.reset.data or reset_delete.delete.data:
        # Validate form and also check their password
        correct_password = trainer.check_password(reset_delete.reset_pass.data)

        if not (reset_delete.validate() and correct_password):
            if not correct_password:
                reset_delete.reset_pass.errors.append('Wrong password')

            return return_dict

        # Delete their stuff from other tables
        pokemon_ids = [pokemon.id for pokemon in trainer.pokemon]

        for table in [db.PokemonUnlockedEvolution, db.BodyModification,
          db.MoveModification]:
            db.DBSession.execute(sqla.sql.delete(table,
                table.pokemon_id.in_(pokemon_ids)))

        for table in [db.TrainerItem, db.Pokemon, db.BankTransaction,
          db.PromotionRecipient]:
            db.DBSession.execute(sqla.sql.delete(table,
                table.trainer_id == trainer.id))

        if reset_delete.delete.data:
            # DELETE THEM
            # Roles carry over on reset, so we only delete them here
            db.DBSession.execute(sqla.sql.delete(db.TrainerRole,
                db.TrainerRole.trainer_id == trainer.id))

            db.DBSession.delete(trainer)

            return httpexc.HTTPSeeOther('/',
                headers=pyramid.security.forget(request))
        else:
            # Reset them
            trainer.money = 45
            trainer.is_newbie = True
            trainer.last_collected_allowance = None

    return httpexc.HTTPSeeOther('/')

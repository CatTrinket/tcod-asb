import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import sqlalchemy.orm
import wtforms

from asb import db
import asb.forms
import asb.tcodf
from asb.resources import TrainerIndex

class TrainerEditForm(asb.forms.CSRFTokenForm):
    """A form for editing a trainer.

    To be expanded as need arises.
    """

    money_add = wtforms.IntegerField('Money', [wtforms.validators.Optional()])
    roles = asb.forms.MultiCheckboxField('Roles')
    save = wtforms.SubmitField('Save')

    def set_roles(self, trainer):
        """Set the choices for the roles field."""

        self.roles.choices = (
            db.DBSession.query(db.Role.identifier, db.Role.name)
            .order_by(db.Role.id)
            .all()
        )

        if self.roles.data is None:
            self.roles.data = [role.identifier for role in trainer.roles]


@view_config(context=TrainerIndex, renderer='/indices/trainers.mako')
def trainer_index(context, request):
    """The index of all the trainers in the league."""

    pokemon_count = (
        db.DBSession.query(db.Pokemon.trainer_id, sqla.func.count('*')
            .label('count'))
        .select_from(db.Pokemon)
        .group_by(db.Pokemon.trainer_id)
        .subquery()
    )

    trainers = (
        db.DBSession.query(db.Trainer, pokemon_count.c.count)
        .select_from(db.Trainer)
        .join(pokemon_count, pokemon_count.c.trainer_id == db.Trainer.id)
        .options(sqla.orm.subqueryload('squad'))
        .filter(db.Trainer.unclaimed_from_hack == False)
        .order_by(db.Trainer.name)
        .all()
    )

    return {'trainers': trainers}

@view_config(context=db.Trainer, renderer='/trainer.mako')
def trainer(trainer, request):
    """A trainer's info page."""

    profile_link = asb.tcodf.user_forum_link(trainer.tcodf_user_id)
    return {'trainer': trainer, 'profile_link': profile_link}

@view_config(name='edit', context=db.Trainer, renderer='/edit_trainer.mako',
  request_method='GET', permission='trainer.edit')
def edit(trainer, request):
    """A page for editing a trainer."""

    form = TrainerEditForm(csrf_context=request.session)
    form.set_roles(trainer)

    return {'trainer': trainer, 'form': form}

@view_config(name='edit', context=db.Trainer, renderer='/edit_trainer.mako',
  request_method='POST', permission='trainer.edit')
def edit_commit(trainer, request):
    """Process a request to edit a trainer."""

    form = TrainerEditForm(request.POST, csrf_context=request.session)
    form.set_roles(trainer)

    if not form.validate():
        return {'trainer': trainer, 'form': form}

    if form.money_add.data is not None:
        trainer.money += form.money_add.data

    if form.roles.data is not None:
        trainer.roles = (
            db.DBSession.query(db.Role)
            .filter(db.Role.identifier.in_(form.roles.data))
            .all()
        )

    # Calling it like this avoids the trailing slash and thus a second redirect
    return httpexc.HTTPSeeOther(
        request.resource_path(trainer.__parent__, trainer.__name__)
    )

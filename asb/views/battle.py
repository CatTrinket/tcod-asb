import collections
import datetime
import itertools
import re

import pyramid.httpexceptions as httpexc
from pyramid.view import view_config
import sqlalchemy as sqla
import wtforms

from asb import db
import asb.forms
from asb.resources import BattleIndex
import asb.tcodf

length_labels = collections.OrderedDict([
    ('full', 'It finished normally'),
    ('short', 'The battlers agreed to end it partway through'),
    ('dq', 'The loser was disqualified'),
    ('cancelled', 'It ended before anything happened')
])

class BattleApproveForm(asb.forms.CSRFTokenForm):
    """A form for letting a mod approve the prizes given out after a battle."""

    action = wtforms.RadioField(
        'You can either:',
        choices=[
            ('approve', 'Approve this battle, if everything looks right, or'),
            ('reopen', "Reopen this battle, if it shouldn't have been closed.")
        ],
        default='approve'
    )

    submit = wtforms.SubmitField('Go!')

class BattleClosePokemonForm(wtforms.Form):
    """A subform for info about a particular Pokémon's participation in a
    battle.
    """

    participated = wtforms.BooleanField()
    kos = wtforms.IntegerField(validators=[wtforms.validators.Optional()])

class BattleCloseForm(asb.forms.CSRFTokenForm):
    """A form for closing a battle and distributing prizes.

    Use the battle_close_form method below to build one of these with choices
    for who_won and a subform for info about the Pokémon that participated.
    """

    who_won = wtforms.RadioField('Who won?', [wtforms.validators.Required()],
        coerce=int)

    length = wtforms.RadioField(
        'How did it end?',
        [wtforms.validators.Required()],
        choices=list(length_labels.items())
    )

    submit = wtforms.SubmitField('Close battle')

    def pokemon_by_squad(self):
        """Return this battle's Pokémon, grouped by trainer, with their
        subforms.

        n.b. The squads are grouped with itertools.groupby, so remember that
        each squad becomes unavailable after you advance to the next.
        """

        # self.pokemon is added by the battle_close_form method
        squads = zip(self.db_pokemon, self.pokemon)
        squads = itertools.groupby(squads, lambda squad: squad[0].trainer)
        return squads

def battle_close_form(battle, request):
    """Set up the form as usual but also do some other stuff"""

    # Add Pokémon subform, with all its subsubforms
    battle_pokemon = [
        pokemon
        for team in battle.teams
        for trainer in team.trainers
        for pokemon in trainer.pokemon
    ]

    class PokemonForm(wtforms.Form):
        """A subform to hold all the BattleClosePokemonForm sub-subforms."""

        pass

    for pokemon in battle_pokemon:
        field = wtforms.FormField(BattleClosePokemonForm)
        setattr(PokemonForm, str(pokemon.id), field)

    class FullBattleCloseForm(BattleCloseForm):
        """The full form, with Pokémon."""

        db_pokemon = battle_pokemon
        pokemon = wtforms.FormField(PokemonForm)

    form = FullBattleCloseForm(request.POST, csrf_context=request.session)

    # Set choices for who_won
    form.who_won.choices = [
        (team.team_number, '/'.join(trainer.name for trainer in team.trainers))
        for team in battle.teams
    ]

    # XXX What about battles where some teams tie and some other teams lose
    form.who_won.choices.append((-1, 'It was a tie'))

    return form

class BattleEditRefForm(wtforms.Form):
    """A single row for a ref in a BattleEditForm."""

    ref = asb.forms.TrainerField()
    current = wtforms.BooleanField()
    emergency = wtforms.BooleanField()

    def validate_ref(form, field):
        """Make sure we got a valid trainer."""

        if field.data and field.trainer is None:
            raise wtforms.validators.ValidationError('Unknown trainer')

class BattleEditForm(asb.forms.CSRFTokenForm):
    """An admin-only form for editing a battle."""

    title = wtforms.TextField('Title')
    refs = wtforms.FieldList(
        wtforms.FormField(BattleEditRefForm, [wtforms.validators.Optional()]),
    )
    save = wtforms.SubmitField('Save')

    def set_refs(self, battle):
        """Set data for the ref table based on the battle's current refs."""

        for ref in battle.all_refs:
            print(self.refs.data)
            self.refs.append_entry({
                'ref': ref.trainer.name,
                'current': ref.is_current_ref,
                'emergency': ref.is_emergency_ref
            })

        # Also add one blank row
        self.refs.append_entry()

class BattleLinkForm(asb.forms.CSRFTokenForm):
    """A form for pasting a link to a battle's thread on the forums."""

    link = wtforms.StringField('Link', [wtforms.validators.Required()])
    submit = wtforms.SubmitField('Go!')

    thread_id = None

    def validate_link(form, field):
        """Parse the thread ID out of the link, and let WTForms turn any
        exception the thread_id function raises into a validation error.
        """

        form.thread_id = asb.tcodf.thread_id(field.data)

class BattleTrainerField(wtforms.TextAreaField):
    """A field for entering trainers who will participate in a battle."""

    _teams = None

    def process_formdata(self, valuelist):
        """Split the input into lists of names."""

        # Split the text into teams, and each team into a list of names
        [teams] = valuelist

        teams = [
            team.splitlines() for team in
            re.split(
                '(?:\r\n|\n){2,}',  # 2+ newlines, i.e. one or more empty lines
                teams.strip()
            )
        ]

        # If there's only one list, then it's just every trainer for themself;
        # put each trainer on their own team
        if len(teams) == 1:
            teams = [[trainer] for trainer in teams[0]]

        self.data = teams

    def _value(self):
        """Re-join all the lists of names into one string."""

        if not self.data:
            return ''
        elif all(len(team) == 1 for team in self.data):
            return '\n'.join(trainer for [trainer] in self.data)
        else:
            return '\n\n'.join('\n'.join(team) for team in self.data)

    def pre_validate(self, form):
        """Do some validation."""

        # Make sure there are at least two trainers
        if len(self.data) == 1:
            self.errors.append(
                'A battle has to involve at least two trainers'
            )

        # Make sure nobody is listed more than once
        counts = collections.Counter(name for team in self.data for name in team)
        for name, count in counts.items():
            if count > 1:
                self.errors.append('{} is listed more than once'.format(name))

        # Make sure all these trainers exist
        try:
            self.teams
        except KeyError as error:
            self.errors.append(
                "Unknown trainer: {}".format(*error.args)
            )

    @property
    def teams(self):
        """Return all the DB records corresponding to the listed trainers,
        grouped into teams.
        """

        if self._teams is not None:
            return self._teams

        # Turn the names into actual trainer objects
        names = [trainer.lower() for team in self.data for trainer in team]
        trainers = (
            db.DBSession.query(db.Trainer)
            .filter(sqla.func.lower(db.Trainer.name).in_(names))
            .filter_by(is_validated=True)
            .all()
        )
        trainers = {trainer.name.lower(): trainer for trainer in trainers}

        # Sort these trainer objects back into teams
        try:
            teams = [
                [trainers[name.lower()] for name in team]
                for team in self.data
            ]
        except KeyError:
            # Find ALL the problematic names.  Kind of silly to go through
            # again but it's a lot shorter than doing both in one pass.
            raise KeyError(', '.join(
               name for team in self.data for name in team
               if name.lower() not in trainers
            ))

        self._teams = teams
        return teams

class NewBattleForm(asb.forms.CSRFTokenForm):
    """A form for listing trainers for a new battle."""

    trainers = BattleTrainerField()
    submit = wtforms.SubmitField('Submit')

def format_outcome(battle):
    """
    Return a tuple of the format (outcome, length) where outcome is a formatted
    description of who won Battle battle and length is a formatted description
    of how battle ended.
    """

    winners = [team for team in battle.teams
               if team.outcome in ['win', 'draw']]

    if winners[0].outcome == 'win':
        team = ' and '.join(trainer.name for trainer in winners[0].trainers)
        outcome = '{} won.'.format(team)
    else:
        teams = ' and '.join(
            '/'.join(trainer.name for trainer in team.trainers)
            for team in winners
        )

        outcome = '{} tied.'.format(teams)

    return (outcome, length_labels[battle.length])


@view_config(context=BattleIndex, renderer='/indices/battles.mako')
def battle_index(context, request):
    """The index of all battles."""

    battles = {'open': [], 'approval': [], 'closed': []}
    all_battles = db.DBSession.query(db.Battle).order_by(db.Battle.id).all()

    for battle in all_battles:
        if battle.end_date is None:
            battles['open'].append(battle)
        elif battle.needs_approval:
            battles['approval'].append(battle)
        elif battle.length != 'cancelled':
            battles['closed'].append(battle)

    return battles

@view_config(context=db.Battle, renderer='/battle.mako', request_method='GET')
def battle(battle, request):
    """A battle."""

    if battle.end_date is not None:
        outcome, length = format_outcome(battle)
    else:
        outcome = None
        length = None

    return {
        'battle': battle,
        'team_battle': any(len(team.trainers) > 1 for team in battle.teams),
        'link_form': BattleLinkForm(csrf_context=request.session),
        'outcome': outcome,
        'length': length
    }

@view_config(context=db.Battle, renderer='/battle.mako', request_method='POST',
  permission='battle.link')
def battle_link(battle, request):
    """Add a forum link to a battle."""

    link_form = BattleLinkForm(request.POST, csrf_context=request.session)

    if not link_form.validate():
        return {
            'battle': battle,
            'team_battle': any(len(team.trainers) > 1 for team in
                battle.teams),
            'link_form': link_form
        }

    battle.tcodf_thread_id = link_form.thread_id
    return httpexc.HTTPSeeOther(request.resource_path(battle))

@view_config(context=db.Battle, name='edit', renderer='/edit_battle.mako',
  request_method='GET', permission='battle.edit')
def edit_battle(battle, request):
    """A page for editing a battle."""

    form = BattleEditForm(csrf_context=request.session)
    form.title.data = battle.name
    form.set_refs(battle)

    return {'form': form, 'battle': battle}

@view_config(context=db.Battle, name='edit', renderer='/edit_battle.mako',
  request_method='POST', permission='battle.edit')
def edit_battle_process(battle, request):
    """Process a request to edit a battle."""

    form = BattleEditForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form, 'battle': battle}

    for ref in battle.all_refs:
        db.DBSession.delete(ref)

    for row in form.refs:
        if row.ref.trainer is not None:
            db.DBSession.add(db.BattleReferee(
                battle_id=battle.id,
                trainer_id=row.ref.trainer.id,
                is_current_ref=row.current.data,
                is_emergency_ref=row.emergency.data
            ))

    if form.title.data:
        battle.name = form.title.data
        battle.set_identifier()

    return httpexc.HTTPSeeOther(request.resource_path(battle))

@view_config(context=db.Battle, name='close', renderer='/close_battle.mako',
  request_method='GET', permission='battle.close')
def close_battle(battle, request):
    """A page for closing a battle and distributing prizes."""

    return {
        'battle': battle,
        'team_battle': any(len(team.trainers) > 1 for team in battle.teams),
        'form': battle_close_form(battle, request)
    }

@view_config(context=db.Battle, name='close', renderer='/close_battle.mako',
  request_method='POST', permission='battle.close')
def close_battle_submit(battle, request):
    """Figure out prizes upon closing a battle."""

    form = battle_close_form(battle, request)

    if not form.validate():
        return {
            'battle': battle,
            'team_battle': any(len(team.trainers) > 1 for team in
                battle.teams),
            'form': form
        }

    battle.end_date = datetime.datetime.utcnow().date()
    battle.length = form.length.data

    # Figure out who won
    if form.who_won.data == -1:
        for team in battle.teams:
            team.outcome = 'draw'
    else:
        for team in battle.teams:
            if team.team_number == form.who_won.data:
                team.outcome = 'win'
            else:
                team.outcome = 'loss'

    for (pokemon, subform) in zip(form.db_pokemon, form.pokemon):
        pokemon.participated = subform.participated.data
        pokemon.kos = subform.kos.data or 0

        # Figure out experience/happiness
        if not pokemon.participated:
            pokemon.experience_gained = 0
            pokemon.happiness_gained = 0
        else:
            pokemon.experience_gained = 1 + pokemon.kos
            pokemon.happiness_gained = 1 + pokemon.kos

            # Account for Lucky Egg/Soothe Bell
            if pokemon.item is None:
                pass
            elif pokemon.item.identifier == 'lucky-egg':
                pokemon.experience_gained += 1
            elif pokemon.item.identifier == 'soothe-bell':
                pokemon.happiness_gained += 1

    battle.needs_approval = True

    return httpexc.HTTPSeeOther(request.resource_path(battle))

@view_config(context=db.Battle, name='approve', request_method='GET',
  renderer='/approve_battle.mako', permission='battle.approve')
def approve_battle(battle, request):
    """A page for reviewing the prizes set to be given out for a closed battle,
    and approving them.
    """

    outcome, length = format_outcome(battle)

    return {
        'form': BattleApproveForm(csrf_context=request.session),
        'battle': battle,
        'outcome': outcome,
        'length': length
    }

@view_config(context=db.Battle, name='approve', request_method='POST',
  renderer='/approve_battle.mako', permission='battle.approve')
def approve_battle_submit(battle, request):
    """Process a battle approval form and carry out the appropiate action."""

    form = BattleApproveForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form, 'battle': battle}

    if form.action.data == 'approve':
        return approve_battle_finalize(battle, request)
    elif form.action.data == 'reopen':
        return reopen_battle(battle, request)

def approve_battle_finalize(battle, request):
    """Distribute prizes and mark a battle as approved."""

    if battle.length == 'cancelled':
        # No prizes if the battle never got anywhere
        battle.needs_approval = False
        return httpexc.HTTPSeeOther(request.resource_path(battle))

    # Count up how many Pokémon each team used
    pokemon_used = {team: 0 for team in battle.teams}

    for team in battle.teams:
        for trainer in team.trainers:
            for pokemon in trainer.pokemon:
                if pokemon.participated:
                    pokemon_used[team] += 1

                # Apply experience/happiness gained
                if pokemon.pokemon is not None:
                    pokemon.pokemon.experience += pokemon.experience_gained
                    pokemon.pokemon.happiness += pokemon.happiness_gained

    # Dish out prize/ref money
    ref_money = 0

    for team in battle.teams:
        # Add up how many Pokémon were used *against* this team
        enemy_pokemon_count = sum(
            pokemon for (other_team, pokemon) in pokemon_used.items()
            if team != other_team
        )

        # Figure out what to multiply that by to determine prize money
        if team.outcome == 'win':
            prize_money = 8 * enemy_pokemon_count
            ref_money = 5 * enemy_pokemon_count
        elif team.outcome == 'draw':
            prize_money = 4 * enemy_pokemon_count
            ref_money = max(ref_money, 5 * enemy_pokemon_count)
        elif team.outcome == 'loss':
            if battle.length == 'dq':
                prize_money = 0
            else:
                prize_money = 4 * enemy_pokemon_count

        # Give that much money to each trainer on this team
        for battle_trainer in team.trainers:
            if not battle_trainer.trainer:
                continue

            battle_trainer.trainer.money += prize_money

    # Divide up ref money
    ref_money //= len(battle.all_refs)

    for ref in battle.all_refs:
        ref.trainer.money += ref_money

    battle.needs_approval = False

    return httpexc.HTTPSeeOther(request.resource_path(battle))

def reopen_battle(battle, request):
    """Reopen a closed battle awaiting approval so that everything is as if it
    had never been closed.
    """

    battle.needs_approval = False
    battle.end_date = None
    battle.length = None

    for team in battle.teams:
        team.outcome = None

        for trainer in team.trainers:
            for pokemon in trainer.pokemon:
                pokemon.experience_gained = None
                pokemon.happiness_gained = None
                pokemon.participated = False
                pokemon.kos = None

    return httpexc.HTTPSeeOther(request.resource_path(battle))

@view_config(context=BattleIndex, name='new', renderer='/new_battle.mako',
  request_method='GET', permission='battle.open')
def new_battle(context, request):
    """A page for creating a new battle."""

    return {'form': NewBattleForm(csrf_context=request.session)}

@view_config(context=BattleIndex, name='new', renderer='/new_battle.mako',
  request_method='POST', permission='battle.open')
def new_battle_process(context, request):
    """Create a new battle."""

    form = NewBattleForm(request.POST, csrf_context=request.session)

    if not form.validate():
        return {'form': form}

    # Make sure the ref hasn't listed themselves
    if any(trainer == request.user for team in form.trainers.teams
      for trainer in team):
        form.trainers.errors.append("You can't battle if you're the ref!")
        return {'form': form}

    # Create battle
    battle_id = db.DBSession.execute(db.Battle.battles_id_seq)
    battle = db.Battle(
        id=battle_id,
        name='temp-{}'.format(battle_id),
        identifier='temp-{}'.format(battle_id),
        start_date=datetime.datetime.utcnow().date()
    )

    db.DBSession.add(battle)

    # Add teams, trainers, and Pokémon
    for (number, team) in enumerate(form.trainers.teams, 1):
        battle_team = db.BattleTeam(battle_id=battle_id, team_number=number)
        db.DBSession.add(battle_team)

        for trainer in team:
            battle_trainer = db.BattleTrainer(
                battle_id=battle_id,
                trainer_id=trainer.id,
                name = trainer.name,
                team_number=number
            )

            db.DBSession.add(battle_trainer)
            db.DBSession.flush()

            for pokemon in trainer.squad:
                if pokemon.species.form_carries_into_battle:
                    form_id = pokemon.pokemon_form_id
                else:
                    form_id = pokemon.species.default_form.id

                battle_pokemon = db.BattlePokemon(
                    pokemon_id=pokemon.id,
                    battle_trainer_id=battle_trainer.id,
                    name=pokemon.name,
                    pokemon_form_id=form_id,
                    gender_id=pokemon.gender_id,
                    ability_slot=pokemon.ability_slot,
                    item_id=None if pokemon.item is None else pokemon.item.id,
                    is_shiny=pokemon.is_shiny,
                    experience=pokemon.experience,
                    happiness=pokemon.happiness
                )

                db.DBSession.add(battle_pokemon)

    # Add the ref
    battle_ref = db.BattleReferee(
        battle_id=battle_id,
        trainer_id=request.user.id
    )

    db.DBSession.add(battle_ref)

    battle.set_auto_name()
    db.DBSession.flush()

    return httpexc.HTTPSeeOther(request.resource_path(battle))

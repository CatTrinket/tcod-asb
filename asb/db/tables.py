import pbkdf2
import pyramid.security as sec
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, UniqueConstraint, Sequence
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
import sqlalchemy.schema
from sqlalchemy.sql import and_, or_
from sqlalchemy.types import *
from zope.sqlalchemy import ZopeTransactionExtension

import asb.tcodf
from . import helpers


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class PokedexTable(Base):
    """A class for tables holding general data for the dex pages, like Pokémon
    species, moves etc.

    Data for these tables is stored in CSVs in db/data/.
    """

    __abstract__ = True
    metadata = sqlalchemy.schema.MetaData()

class PlayerTable(Base):
    """A class for tables holding data specific to this instance of the game,
    like trainers and their Pokémon.
    """

    __abstract__ = True
    metadata = sqlalchemy.schema.MetaData()

### POKÉDEX TABLES
# These go first because player tables need to be able to specify foreign keys
# to them without using strings

class Ability(PokedexTable):
    """An ability."""

    __tablename__ = 'abilities'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)

    @property
    def __name__(self):
        """Return this ability's resource name for traversal."""

        return self.identifier

class BankTransactionState(PokedexTable):
    """A possible state for bank transactions.

    Values:
    - pending: A mod has to approve or deny the transaction.
    - processed: The transaction has been approved/denied and the trainer
        should be notified.
    - acknowledged: The trainer has acknowledged that the transaction has been
        approved or denied.

    The primary key is an identifier to mimic an Enum, while not being as
    impossible to update with alembic as an Enum.
    """

    __tablename__ = 'bank_transaction_states'

    identifier = Column(Unicode, primary_key=True)

class BattleLength(PokedexTable):
    """A summary for how close a battle came to completion before it ended.

    Values:
    - full: The battle finished normally.
    - short: Participants agreed to end the battle early.
    - dq: The loser was disqualified.
    - cancelled: The battle was cancelled before anything happened.

    The primary key is an identifier to mimic an Enum, while not being as
    impossible to update with alembic as an Enum.
    """

    __tablename__ = 'battle_lengths'

    identifier = Column(Unicode, primary_key=True)

class BattleOutcome(PokedexTable):
    """A possible outcome for a team in a battle.

    Values:
    - win: This team was the single winning team.
    - draw: This team tied for winner with at least one other team.
    - loss: This team wasn't the winner.

    The primary key is an identifier to mimic an Enum, while not being as
    impossible to update with alembic as an Enum.
    """

    __tablename__ = 'battle_outcomes'

    identifier = Column(Unicode, primary_key=True)

class ContestCategory(PokedexTable):
    """An effect moves can have in a contest."""

    __tablename__ = 'contest_categories'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    supercategory_id = Column(Integer,
        ForeignKey('contest_supercategories.id'), nullable=False)
    description = Column(Unicode, nullable=False)

class ContestSupercategory(PokedexTable):
    """A supercategory that groups contest categories."""

    __tablename__ = 'contest_supercategories'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class DamageClass(PokedexTable):
    """A damage class (physical, special, or non-damaging)."""

    __tablename__ = 'damage_classes'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class Gender(PokedexTable):
    """An enigma."""

    __tablename__ = 'genders'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class Item(PokedexTable):
    """A type of item.

    The order column applies within the item category.
    """

    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    price = Column(Integer, nullable=True)
    item_category_id = Column(Integer, ForeignKey('item_categories.id'),
        nullable=False)
    order = Column(Integer, nullable=True)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)

    @property
    def __name__(self):
        """Return this item's resource name for traversal."""

        return self.identifier

class ItemCategory(PokedexTable):
    """A category for grouping similar items."""

    __tablename__ = 'item_categories'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    order = Column(Unicode, nullable=False)

class Move(PokedexTable):
    """A move (a.k.a. an attack)."""

    __tablename__ = 'moves'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    type_id = Column(Integer, ForeignKey('types.id'), nullable=False)
    damage_class_id = Column(Integer, ForeignKey('damage_classes.id'),
        nullable=False)
    power = Column(Integer, nullable=True)
    energy = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=False)
    target_id = Column(Integer, ForeignKey('move_targets.id'), nullable=False)
    contest_category_id = Column(Integer, ForeignKey('contest_categories.id'),
        nullable=True)
    appeal = Column(Integer, nullable=True)
    bonus_appeal = Column(Integer, nullable=True)
    jam = Column(Integer, nullable=True)
    bonus_jam = Column(Integer, nullable=True)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)
    category = Column(Unicode, nullable=True)  # XXX do something better later

    @property
    def damage(self):
        """Return this move's base damage."""

        if self.power is None:
            return None
        else:
            return self.power // 10

    @property
    def __name__(self):
        """Return this move's resource name for traversal."""

        return self.identifier

class MoveTarget(PokedexTable):
    """A set of Pokémon that a move can target."""

    __tablename__ = 'move_targets'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class PokemonFamily(PokedexTable):
    """An evolutionary family of Pokémon species."""

    __tablename__ = 'pokemon_families'

    id = Column(Integer, primary_key=True)

class PokemonForm(PokedexTable):
    """A particular form of a Pokémon species.

    If a Pokémon only has one form, it still has a row in this table.
    """

    __tablename__ = 'pokemon_forms'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    species_id = Column(Integer, ForeignKey('pokemon_species.id'))
    form_name = Column(Unicode, nullable=True)
    full_name = Column(Unicode, nullable=True)
    form_order = Column(Integer, nullable=False)
    is_default = Column(Boolean, nullable=False)
    order = Column(Integer, unique=True, nullable=False)

    @property
    def name(self):
        """Return a name for this Pokémon form."""

        return self.full_name or self.species.name

    @property
    def __name__(self):
        """Return this form's resource name for traversal."""

        return self.identifier

class PokemonFormAbility(PokedexTable):
    """One of a Pokémon form's abilities."""

    __tablename__ = 'pokemon_form_abilities'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    slot = Column(Integer, primary_key=True)
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=False)
    is_hidden = Column(Boolean, nullable=False)

class PokemonFormCondition(PokedexTable):
    """The conditions a Pokémon must meet in order to change into a particular
    form.
    """

    __tablename__ = 'pokemon_form_conditions'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    is_optional = Column(Boolean, nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=True)
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=True)

class PokemonFormMove(PokedexTable):
    """A move that a Pokémon form can use."""

    __tablename__ = 'pokemon_form_moves'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    move_id = Column(Integer, ForeignKey('moves.id'), primary_key=True)

class PokemonFormType(PokedexTable):
    """One of a Pokémon form's types."""

    __tablename__ = 'pokemon_form_types'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    slot = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('types.id'))

class PokemonSpecies(PokedexTable):
    """A species of Pokémon."""

    __tablename__ = 'pokemon_species'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    pokemon_family_id = Column(Integer, ForeignKey('pokemon_families.id'),
        nullable=False)
    evolves_from_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        nullable=True)
    rarity_id = Column(Integer, ForeignKey('rarities.id'), nullable=True)
    can_switch_forms = Column(Boolean, nullable=False)
    form_carries_into_battle = Column(Boolean, nullable=False)
    forms_are_squashable = Column(Boolean, nullable=False)
    order = Column(Integer, unique=True, nullable=False)
    form_explanation = Column(Unicode, nullable=True)

    # Set up a couple constraints to make sure that evolves_from_species_id
    # points to a Pokémon in the same evolution family
    __table_args__ = (
        UniqueConstraint('id', 'pokemon_family_id'),

        ForeignKeyConstraint(
            ['evolves_from_species_id', 'pokemon_family_id'],
            ['pokemon_species.id', 'pokemon_species.pokemon_family_id'],
        ),
    )

    @property
    def number(self):
        """Return national dex number for canon Pokémon, or an "A##" number for
        fakemon,
        """

        if self.id < 10000:
            return '{0:03}'.format(self.id)
        else:
            return 'A{0:02}'.format(self.id - 10000)

class PokemonSpeciesEvolution(PokedexTable):
    """The method by which a Pokémon species evolves."""

    __tablename__ = 'pokemon_species_evolution'

    evolved_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        primary_key=True)
    experience = Column(Integer, nullable=True)
    happiness = Column(Integer, nullable=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=True)
    buyable_price = Column(Integer, nullable=True)
    can_trade_instead = Column(Boolean, nullable=False)

class PokemonSpeciesGender(PokedexTable):
    """A gender a Pokémon species can have."""

    __tablename__ = 'pokemon_species_genders'

    pokemon_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        primary_key=True)
    gender_id = Column(Integer, ForeignKey('genders.id'), primary_key=True)

class Rarity(PokedexTable):
    """A Pokémon rarity."""

    __tablename__ = 'rarities'

    id = Column(Integer, primary_key=True)
    price = Column(Integer, nullable=False)

class Role(PokedexTable):
    """A role (admin, mod, ref, etc) that a trainer can have."""

    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class Type(PokedexTable):
    """A type (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)


### PLAYER TABLES

class BankTransaction(PlayerTable):
    """A bank transaction."""

    __tablename__ = 'bank_transactions'

    id = Column(Integer, Sequence('bank_transactions_id_seq'),
        primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    amount = Column(Integer, nullable=False)
    tcod_post_id = Column(Integer, nullable=False)
    state = Column(Unicode, ForeignKey(BankTransactionState.identifier),
        nullable=False, default='pending')
    is_approved = Column(Boolean, nullable=False, default=False)
    approver_id = Column(Integer, ForeignKey('trainers.id',
        onupdate='cascade'), nullable=True)
    reason = Column(UnicodeText, nullable=True)

    @property
    def link(self):
        return asb.tcodf.post_link(self.tcod_post_id)

class Battle(PlayerTable):
    """A battle."""

    __tablename__ = 'battles'

    battles_id_seq = Sequence('battles_id_seq')

    id = Column(Integer, battles_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    tcodf_thread_id = Column(Integer, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    length = Column(Unicode, ForeignKey(BattleLength.identifier),
        nullable=True)
    needs_approval = Column(Boolean, nullable=False, default=False)

    @property
    def link(self):
        """A link to this battle's forum thread."""

        return asb.tcodf.thread_link(self.tcodf_thread_id)

    def set_auto_name(self):
        """Automatically generate a name for this battle, then set its
        identifier.
        """

        # Start with something like "A and B vs C and D"
        base_name = name = ' vs '.join(
            ' and '.join(trainer.name for trainer in team.trainers)
            for team in self.teams
        )

        # If necessary, bump a roman numeral until we get a unique name
        # e.g. "A and B vs C and D II"
        n = 1

        while DBSession.query(Battle).filter_by(name=name).count():
            n += 1
            name = '{} {}'.format(base_name, helpers.roman_numeral(n))

        # Go for it
        self.name = name
        self.set_identifier()

    def set_identifier(self):
        """Set an identifier based on ID and name."""

        self.identifier = helpers.identifier(self.name, id=self.id)

    @property
    def __acl__(self):
        """Return an list of permissions for Pyramid's authorization."""

        permissions = []

        # Get ACL identifiers for ref + battlers
        if self.ref is not None:
            ref = 'user:{}'.format(self.ref.id)
        else:
            ref = None

        trainers = [
            'user:{}'.format(trainer.trainer_id)
            for team in self.teams
            for trainer in team.trainers
            if trainer.trainer_id is not None
        ]

        if self.end_date is None:
            # Battle's still going on
            # Let the current ref manage the battle, but not join as an e-ref
            if ref is not None:
                if self.tcodf_thread_id is None:
                    permissions.append((sec.Allow, ref, 'battle.link'))
                else:
                    permissions.append((sec.Allow, ref, 'battle.close'))

                permissions.append((sec.Deny, ref, 'battle.e-ref'))

            # Don't let any of the battlers e-ref, either
            for trainer in trainers:
                permissions.append((sec.Deny, trainer, 'battle.e-ref'))

            # Let any other ref join as an e-ref
            # Actually not yet because I don't have that working
            # permissions.append((sec.Allow, 'referee', 'battle.e-ref'))
        elif self.needs_approval:
            # Battle ended; prizes need approval
            # Let any mod/admin do so, unless they were involved in the battle
            if ref is not None:
                permissions.append((sec.Deny, ref, 'battle.approve'))

            for trainer in trainers:
                permissions.append((sec.Deny, trainer, 'battle.approve'))            

            # XXX Ideally you'd have to be a mod/admin *and* a ref
            permissions.append((sec.Allow, 'mod', 'battle.approve'))
            permissions.append((sec.Allow, 'admin', 'battle.approve'))

        return permissions

    @property
    def __name__(self):
        """Return this battle's resource name for traversal."""

        return self.identifier

class BattlePokemon(PlayerTable):
    """A Pokémon that is part of a trainer's squad for a particular battle, and
    information about it at the time of the battle.

    When a trainer resets or deletes their account, all their Pokémon's
    battle_pokemon rows will stick around, with null pokemon_ids.  This way,
    the battle can keep existing for the other participants' records.
    """

    __tablename__ = 'battle_pokemon'

    id = Column(Integer, Sequence('battle_pokemon_id_seq'), primary_key=True)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id'), nullable=True)
    battle_trainer_id = Column(Integer, ForeignKey('battle_trainers.id'),
        nullable=False)
    name = Column(Unicode, nullable=False)
    pokemon_form_id = Column(Integer, ForeignKey(PokemonForm.id),
        nullable=False)
    gender_id = Column(Integer, ForeignKey(Gender.id), nullable=False)
    ability_slot = Column(Integer, nullable=False)
    item_id = Column(Integer, ForeignKey(Item.id), nullable=True)
    experience = Column(Integer, nullable=False)
    happiness = Column(Integer, nullable=False)
    experience_gained = Column(Integer, nullable=True)
    happiness_gained = Column(Integer, nullable=True)
    participated = Column(Boolean, nullable=False, default=False)
    kos = Column(Integer, nullable=True)

    # Set up a composite foreign key for ability
    __table_args__ = (
        ForeignKeyConstraint(
            [pokemon_form_id, ability_slot],
            [PokemonFormAbility.pokemon_form_id, PokemonFormAbility.slot],
            name='battle_pokemon_ability_fkey', use_alter=True
        ),
    )

class BattleReferee(PlayerTable):
    """A trainer who acted as a referee in a battle.

    Unlike the other battle tables, rows in this table are deleted if the
    trainer deletes their account (and kept if they reset, because why not).
    """

    __tablename__ = 'battle_referees'

    battle_id = Column(Integer, ForeignKey('battles.id'), primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id'), primary_key=True)
    is_emergency_ref = Column(Boolean, nullable=False, default=False)
    is_current_ref = Column(Boolean, nullable=False, default=True)

class BattleTeam(PlayerTable):
    """A team of trainers participating in a battle.

    If a trainer has no teammates, they count as a team of one.
    """

    __tablename__ = 'battle_teams'

    battle_id = Column(Integer, ForeignKey('battles.id'), primary_key=True)
    team_number = Column(Integer, primary_key=True, autoincrement=False)
    outcome = Column(Unicode, ForeignKey(BattleOutcome.identifier),
        nullable=True)

class BattleTrainer(PlayerTable):
    """A trainer participating in a battle.

    When a trainer resets or deletes their account, all their rows in
    battle_trainers will stick around, with null trainer_ids.  This way, the
    battle can keep existing for the other participants' records.
    """

    __tablename__ = 'battle_trainers'

    id = Column(Integer, Sequence('battle_trainers_id_seq'), primary_key=True)
    battle_id = Column(Integer, ForeignKey('battles.id'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    name = Column(Unicode, nullable=False)
    team_number = Column(Integer, autoincrement=False)

    __table_args__ = (
        ForeignKeyConstraint(
            [battle_id, team_number],
            ['battle_teams.battle_id', 'battle_teams.team_number'],
            name='battle_trainer_team_fkey'
        ),

        UniqueConstraint('battle_id', 'trainer_id')
    )

class BodyModification(PlayerTable):
    """A Pokémon's signature attribute or other body mod."""

    __tablename__ = 'body_modifications'

    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        primary_key=True)
    name = Column(Unicode, nullable=False)
    is_repeatable = Column(Boolean, nullable=False)
    flavor = Column(Unicode, nullable=False)
    effect = Column(Unicode, nullable=False)

class MoveModification(PlayerTable):
    """A Pokémon's signature move or other movepool mod.

    This is a direct port of the hack's asb_move_mods table.  I was not the one
    who decided the entire table should just be text.  (The only change I made
    is pokemon_id — Negrek had the foreign key on the pokemon side.)
    """

    __tablename__ = 'move_modifications'

    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        primary_key=True)
    name = Column(Unicode, nullable=False)
    type = Column(Unicode, nullable=True)
    power = Column(Unicode, nullable=True)
    energy = Column(Unicode, nullable=True)
    accuracy = Column(Unicode, nullable=True)
    target = Column(Unicode, nullable=True)
    gap = Column(Unicode, nullable=True)
    duration = Column(Unicode, nullable=True)
    stat = Column(Unicode, nullable=True)
    flavor = Column(Unicode, nullable=True)
    effect = Column(Unicode, nullable=True)

class Pokemon(PlayerTable):
    """An individual Pokémon owned by a trainer."""

    __tablename__ = 'pokemon'

    pokemon_id_seq = Sequence('pokemon_id_seq')

    id = Column(Integer, pokemon_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode(30), nullable=False)
    pokemon_form_id = Column(Integer, ForeignKey(PokemonForm.id),
        nullable=False)
    gender_id = Column(Integer, ForeignKey(Gender.id), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    ability_slot = Column(Integer, nullable=False)
    experience = Column(Integer, nullable=False, default=0)
    happiness = Column(Integer, nullable=False, default=0)
    is_in_squad = Column(Boolean, nullable=False, default=False)
    form_uncertain = Column(Boolean, nullable=False, default=False)

    # Set up a composite foreign key for ability
    __table_args__ = (
        ForeignKeyConstraint(
            [pokemon_form_id, ability_slot],
            [PokemonFormAbility.pokemon_form_id, PokemonFormAbility.slot],
            name='pokemon_ability_fkey', use_alter=True
        ),
    )

    def update_identifier(self):
        """Update this Pokémon's identifier."""

        self.identifier = helpers.identifier(self.name, id=self.id)

    @property
    def __name__(self):
        """Return this Pokémon's resource name for traversal."""

        return self.identifier

    @property
    def __acl__(self):
        """Return an list of permissions for Pyramid's authorization."""

        trainer = 'user:{}'.format(self.trainer_id)

        return [
            (sec.Allow, trainer, 'edit.basics'),
            (sec.Allow, trainer, 'edit.evolve'),
            (sec.Allow, 'admin', 'edit.basics'),
            (sec.Allow, 'admin', 'edit.everything'),
            (sec.Allow, 'mod', 'edit.basics'),
        ]

class PokemonUnlockedEvolution(PlayerTable):
    """A species which a Pokémon has fulfilled the requirements to evolve
    into.

    Evolutions whose requirements can be otherwise verified — i.e. anything
    other than item or trade evolutions — should not be stored here.
    """

    __tablename__ = 'pokemon_unlocked_evolutions'

    # XXX It would be nice if we could constrain evolved_species_id to
    # something the Pokémon can actually evolve into.  It would be even *nicer*
    # if we could do without this table altogether...

    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        primary_key=True)
    evolved_species_id = Column(Integer, ForeignKey(PokemonSpecies.id),
        primary_key=True)

class Promotion(PlayerTable):
    """An opportunity to receive a special Pokémon or item, e.g. a giveaway or
    a tournament prize.
    """

    __tablename__ = 'promotions'

    promotions_id_seq = Sequence('promotions_id_seq')

    id = Column(Integer, promotions_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode(30), unique=True, nullable=False)
    is_public = Column(Boolean, nullable=False)
    price = Column(Integer, nullable=False)
    hidden_ability = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

class PromotionItem(PlayerTable):
    """An item available through a promotion."""

    __tablename__ = 'promotion_items'

    promotion_id = Column(Integer, ForeignKey('promotions.id'),
        primary_key=True)
    item_id = Column(Integer, ForeignKey(Item.id), primary_key=True)

class PromotionPokemonSpecies(PlayerTable):
    """A Pokémon species available through a promotion."""

    __tablename__ = 'promotion_pokemon_species'

    promotion_id = Column(Integer, ForeignKey('promotions.id'),
        primary_key=True)
    pokemon_species_id = Column(Integer, ForeignKey(PokemonSpecies.id),
        primary_key=True)

class PromotionRecipient(PlayerTable):
    """A trainer who has received or is eligible to receive a promotion.

    If the promotion is public, all trainers are eligible recipients, and only
    trainers who have actually received their thing need to be listed here.
    """

    __tablename__ = 'promotion_recipients'

    promotion_id = Column(Integer, ForeignKey('promotions.id'),
        primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        primary_key=True)
    received = Column(Boolean, nullable=False)

class Trainer(PlayerTable):
    """A member of the ASB league and user of this app thing."""

    __tablename__ = 'trainers'

    trainers_id_seq = Sequence('trainers_id_seq')

    id = Column(Integer, trainers_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode(30), nullable=False)
    tcodf_user_id = Column(Integer, unique=True, nullable=True)
    password_hash = Column(Unicode, nullable=True)
    email = Column(Unicode(60), nullable=True)
    money = Column(Integer, nullable=False, default=45)
    last_collected_allowance = Column(Date, nullable=True)
    unclaimed_from_hack = Column(Boolean, nullable=False, default=False)
    is_validated = Column(Boolean, nullable=False, default=False)

    # Prevent two trainers from having the same name, unless one is an actual
    # user and the other is just an old hack profile
    __table_args__ = (UniqueConstraint('name', 'unclaimed_from_hack'),)

    def set_password(self, password):
        """Hash and store the given password."""

        self.password_hash = pbkdf2.crypt(password)

    def check_password(self, password):
        """Check the given password against the stored password hash."""

        return pbkdf2.crypt(password, self.password_hash) == self.password_hash

    def update_identifier(self):
        """Like it says on the tin."""

        self.identifier = helpers.identifier(self.name, id=self.id)

    @property
    def has_items(self):
        """Determine whether or not this trainer has any items without having
        to actually fetch them.
        """

        existence_subquery = (DBSession.query(TrainerItem)
            .filter(TrainerItem.trainer_id == self.id)
            .exists())
        items_exist, = DBSession.query(existence_subquery).one()
        return items_exist

    @property
    def has_pokemon(self):
        """Determine whether or not this trainer has any Pokémon without having
        to actually fetch them.
        """

        existence_subquery = (DBSession.query(Pokemon)
            .filter(Pokemon.trainer_id == self.id)
            .exists())
        pokemon_exist, = DBSession.query(existence_subquery).one()
        return pokemon_exist

    @property
    def promotions(self):
        """Return any promotions this trainer is eligible to receive."""

        my_promotions = (
            DBSession.query(PromotionRecipient)
            .filter_by(trainer_id=self.id)
            .subquery()
        )

        return (
            DBSession.query(Promotion)
            .outerjoin(my_promotions)
            .filter(or_(
                my_promotions.c.received == False,
                and_(
                    Promotion.is_public == True,
                    my_promotions.c.received.is_(None)
                )
            ))
            .all()
        )

    @property
    def __name__(self):
        """Return this trainer's resource name for traversal."""

        return self.identifier

class TrainerItem(PlayerTable):
    """An individual item owned by a trainer and possibly held by a Pokémon."""

    __tablename__ = 'trainer_items'

    id = Column(Integer, Sequence('trainer_items_id_seq'), primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    item_id = Column(Integer, ForeignKey(Item.id), nullable=False)
    # XXX Some RDBMSes don't do nullable + unique right (but postgres does)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        nullable=True, unique=True)

class TrainerRole(PlayerTable):
    """A role that a trainer has."""

    __tablename__ = 'trainer_roles'

    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        primary_key=True)
    role_id = Column(Integer, ForeignKey(Role.id), primary_key=True)

# Relationships go down here so that we don't have to use strings for
# everything
BankTransaction.approver = relationship(Trainer,
    primaryjoin=BankTransaction.approver_id == Trainer.id)
BankTransaction.trainer = relationship(Trainer,
    primaryjoin=BankTransaction.trainer_id == Trainer.id)

Battle.ref = relationship(Trainer, secondary=BattleReferee.__table__,
    primaryjoin=and_(Battle.id == BattleReferee.battle_id,
        BattleReferee.is_current_ref == True),
    uselist=False)
Battle.previous_refs = relationship(Trainer, secondary=BattleReferee.__table__,
    primaryjoin=and_(Battle.id == BattleReferee.battle_id,
        BattleReferee.is_current_ref == False))
Battle.teams = relationship(BattleTeam, order_by=BattleTeam.team_number)

BattlePokemon.ability = relationship(Ability,
    secondary=PokemonFormAbility.__table__, uselist=False)
BattlePokemon.form = relationship(PokemonForm)
BattlePokemon.gender = relationship(Gender)
BattlePokemon.item = relationship(Item)
BattlePokemon.pokemon = relationship(Pokemon)
BattlePokemon.species = association_proxy('form', 'species')
BattlePokemon.trainer = relationship(BattleTrainer, back_populates='pokemon')

BattleTeam.trainers = relationship(BattleTrainer, order_by=BattleTrainer.id)

BattleTrainer.pokemon = relationship(BattlePokemon, order_by=BattlePokemon.id,
    back_populates='trainer')
BattleTrainer.trainer = relationship(Trainer)

ContestCategory.moves = relationship(Move, back_populates='contest_category',
    order_by=Move.name)
ContestCategory.supercategory = relationship(ContestSupercategory,
    back_populates='categories')

ContestSupercategory.categories = relationship(ContestCategory,
    order_by=ContestCategory.id,  back_populates='supercategory')

Item.category = relationship(ItemCategory, back_populates='items')

ItemCategory.items = relationship(Item, back_populates='category',
    order_by=(Item.order, Item.name))

Move.target = relationship(MoveTarget)
Move.type = relationship(Type)
Move.damage_class = relationship(DamageClass)
Move.pokemon_forms = relationship(PokemonForm, back_populates='moves',
    secondary=PokemonFormMove.__table__, order_by=PokemonForm.order)
Move.contest_category = relationship(ContestCategory)

Pokemon.ability = relationship(Ability,
    secondary=PokemonFormAbility.__table__, uselist=False)
Pokemon.body_modification = relationship(BodyModification, uselist=False)
Pokemon.form = relationship(PokemonForm)
Pokemon.gender = relationship(Gender)
Pokemon.item = relationship(Item,
    secondary=TrainerItem.__table__, uselist=False)
Pokemon.trainer_item = relationship(TrainerItem, uselist=False)
Pokemon.move_modification = relationship(MoveModification, uselist=False)
Pokemon.species = association_proxy('form', 'species')
Pokemon.trainer = relationship(Trainer, back_populates='pokemon')
Pokemon.unlocked_evolutions = relationship(PokemonSpecies,
    secondary=PokemonUnlockedEvolution.__table__)

PokemonSpeciesEvolution.gender = relationship(Gender,
    primaryjoin=PokemonSpeciesEvolution.gender_id == Gender.id, uselist=False)
PokemonSpeciesEvolution.item = relationship(Item,
    primaryjoin=PokemonSpeciesEvolution.item_id == Item.id, uselist=False)

PokemonFamily.species = relationship(PokemonSpecies, back_populates='family',
    order_by=PokemonSpecies.order)

PokemonForm.abilities = relationship(PokemonFormAbility,
    order_by=PokemonFormAbility.slot)
PokemonForm.condition = relationship(PokemonFormCondition, uselist=False)
PokemonForm.species = relationship(PokemonSpecies, back_populates='forms')
PokemonForm.moves = relationship(Move, secondary=PokemonFormMove.__table__,
    order_by=Move.name, back_populates='pokemon_forms')
PokemonForm.types = relationship(Type, secondary=PokemonFormType.__table__,
    order_by=PokemonFormType.slot, back_populates='pokemon_forms')

PokemonFormAbility.ability = relationship(Ability)

PokemonSpecies.family = relationship(PokemonFamily, back_populates='species')
PokemonSpecies.forms = relationship(PokemonForm, back_populates='species',
    order_by=PokemonForm.form_order)
PokemonSpecies.default_form = relationship(PokemonForm,
    primaryjoin=and_(PokemonForm.species_id == PokemonSpecies.id,
        PokemonForm.is_default),
    uselist=False)
PokemonSpecies.evolution_method = relationship(PokemonSpeciesEvolution,
    primaryjoin=PokemonSpecies.id == PokemonSpeciesEvolution.evolved_species_id,
    uselist=False)
PokemonSpecies.evolutions = relationship(PokemonSpecies,
    primaryjoin=PokemonSpecies.id == PokemonSpecies.evolves_from_species_id,
    remote_side=[PokemonSpecies.evolves_from_species_id],
    back_populates='pre_evolution')
PokemonSpecies.pre_evolution = relationship(PokemonSpecies,
    primaryjoin=PokemonSpecies.evolves_from_species_id == PokemonSpecies.id,
    remote_side=[PokemonSpecies.id],
    back_populates='evolutions')
PokemonSpecies.genders = relationship(Gender,
    secondary=PokemonSpeciesGender.__table__, order_by=Gender.id)
PokemonSpecies.rarity = relationship(Rarity, back_populates='pokemon_species')

Promotion.items = relationship(Item, secondary=PromotionItem.__table__,
    order_by=Item.name)
Promotion.pokemon_species = relationship(PokemonSpecies,
    secondary=PromotionPokemonSpecies.__table__, order_by=PokemonSpecies.order)

Rarity.pokemon_species = relationship(PokemonSpecies,
    order_by=PokemonSpecies.order, back_populates='rarity')

Trainer.pokemon = relationship(Pokemon, back_populates='trainer',
    order_by=Pokemon.id)
Trainer.squad = relationship(Pokemon,
    primaryjoin=and_(Pokemon.trainer_id == Trainer.id, Pokemon.is_in_squad),
    order_by=Pokemon.id)
Trainer.pc = relationship(Pokemon,
    primaryjoin=and_(Pokemon.trainer_id == Trainer.id, ~Pokemon.is_in_squad),
    order_by=Pokemon.id)

Trainer.bag = relationship(Item, secondary=TrainerItem.__table__,
    primaryjoin=and_(Trainer.id == TrainerItem.trainer_id,
                     TrainerItem.pokemon_id == None))
Trainer.items = relationship(Item, secondary=TrainerItem.__table__)

Trainer.roles = relationship(Role, secondary=TrainerRole.__table__)

Type.pokemon_forms = relationship(PokemonForm,
    secondary=PokemonFormType.__table__, order_by=PokemonFormType.slot,
    back_populates='types')

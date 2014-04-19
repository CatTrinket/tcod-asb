import pbkdf2
import pyramid.security as sec
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, UniqueConstraint, Sequence
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
import sqlalchemy.schema
from sqlalchemy.sql import and_
from sqlalchemy.types import *
from zope.sqlalchemy import ZopeTransactionExtension

from .helpers import identifier


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
    damage = Column(Integer, nullable=True)
    energy = Column(Integer, nullable=True)
    accuracy = Column(Integer, nullable=True)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)
    target = Column(Unicode, nullable=False)  # XXX do something better later
    category = Column(Unicode, nullable=True)  # XXX do something better later

    @property
    def __name__(self):
        """Return this move's resource name for traversal."""

        return self.identifier

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
    is_starter = Column(Boolean, nullable=False)
    can_switch_forms = Column(Boolean, nullable=False)
    form_carries_into_battle = Column(Boolean, nullable=False)
    forms_are_squashable = Column(Boolean, nullable=False)
    is_fake = Column(Boolean, nullable=False)
    order = Column(Integer, unique=True, nullable=False)

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

class Type(PokedexTable):
    """A type (Normal, Fire, etc.)"""

    __tablename__ = 'types'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)


### PLAYER TABLES

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
    unclaimed_from_hack = Column(Boolean, nullable=False, default=False)

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

        self.identifier = identifier(self.name, id=self.id)

    @property
    def __name__(self):
        """Return this Pokémon's resource name for traversal."""

        return self.identifier

    @property
    def __acl__(self):
        """Return an list of permissions for Pyramid's authorization."""

        trainer = 'user:{}'.format(self.trainer_id)

        return [
            (sec.Allow, trainer, 'edit:basics'),
            (sec.Allow, trainer, 'edit:evolve'),
            (sec.Allow, 'admin', 'edit:basics'),
            (sec.Allow, 'admin', 'edit:everything'),
            (sec.Deny, sec.Everyone, sec.ALL_PERMISSIONS)
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

    pokemon_id = Column(Integer, ForeignKey('pokemon.id'), primary_key=True)
    evolved_species_id = Column(Integer, ForeignKey(PokemonSpecies.id),
        primary_key=True)

class Trainer(PlayerTable):
    """A member of the ASB league and user of this app thing."""

    __tablename__ = 'trainers'

    trainers_id_seq = Sequence('trainers_id_seq')

    id = Column(Integer, trainers_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False, default='')
    name = Column(Unicode(30), nullable=False)
    password_hash = Column(Unicode, nullable=True, default='')
    money = Column(Integer, nullable=False, default=45)
    last_collected_allowance = Column(Date, nullable=True)
    is_newbie = Column(Boolean, nullable=False, default=True)
    unclaimed_from_hack = Column(Boolean, nullable=False, default=False)

    def set_password(self, password):
        """Hash and store the given password."""

        self.password_hash = pbkdf2.crypt(password)

    def check_password(self, password):
        """Check the given password against the stored password hash."""

        return pbkdf2.crypt(password, self.password_hash) == self.password_hash

    def update_identifier(self):
        """Like it says on the tin."""

        self.identifier = identifier(self.name, id=self.id)

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
    def __name__(self):
        """Return this trainer's resource name for traversal."""

        return self.identifier

class TrainerItem(PlayerTable):
    """An individual item owned by a trainer and possibly held by a Pokémon."""

    __tablename__ = 'trainer_items'

    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    item_id = Column(Integer, ForeignKey(Item.id), nullable=False)
    # XXX Some RDBMSes don't do nullable + unique right (but postgres does)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        nullable=True, unique=True)

# Relationships go down here so that we don't have to use strings for
# everything
Item.category = relationship(ItemCategory, back_populates='items')

ItemCategory.items = relationship(Item, back_populates='category',
    order_by=(Item.order, Item.name))

Move.type = relationship(Type)
Move.damage_class = relationship(DamageClass)
Move.pokemon_forms = relationship(PokemonForm, back_populates='moves',
    secondary=PokemonFormMove.__table__, order_by=PokemonForm.order)

Pokemon.ability = relationship(Ability,
    secondary=PokemonFormAbility.__table__, uselist=False)
Pokemon.form = relationship(PokemonForm, back_populates='pokemon')
Pokemon.gender = relationship(Gender)
Pokemon.item = relationship(Item,
    secondary=TrainerItem.__table__, uselist=False)
Pokemon.trainer_item = relationship(TrainerItem, uselist=False)
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
PokemonForm.pokemon = relationship(Pokemon, order_by=Pokemon.name,
    primaryjoin=and_(Pokemon.pokemon_form_id == PokemonForm.id,
                     Pokemon.unclaimed_from_hack == False),
    back_populates='form')
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

Type.pokemon_forms = relationship(PokemonForm,
    secondary=PokemonFormType.__table__, order_by=PokemonFormType.slot,
    back_populates='types')

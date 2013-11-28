import re
import unicodedata

import pbkdf2
import pyramid.security as sec
from sqlalchemy import Column, ForeignKey, ForeignKeyConstraint, Sequence
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.sql import and_
from sqlalchemy.types import *
from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

def identifier(name, id=None):
    """Reduce a name to a URL-friendly yet human-readable identifier."""

    # Step one: strip out diacritics
    # XXX This won't simplify e.g. œ to oe
    identifier = ''.join(char for char in unicodedata.normalize('NFKD', name)
        if not unicodedata.combining(char))

    # Step two: convert to a bunch of alphanumeric words separated by hyphens
    identifier = identifier.lower()
    identifier = identifier.replace("'", '')
    identifier = identifier.replace('♀', '-f')
    identifier = identifier.replace('♂', '-m')
    identifier = re.sub('[^a-z0-9]+', '-', identifier)
    identifier = identifier.strip('-')

    # Step three: tack on the ID if provided
    if identifier and id is not None:
        identifier = '{0}-{1}'.format(id, identifier)
    elif id is not None:
        identifier = str(id)
    elif not identifier:
        # Hopefully-avoidable step four: oh god help we still have nothing
        raise ValueError('Name {0!r} reduces to empty identifier'.format(name))

    return identifier


class Ability(Base):
    """An ability."""

    __tablename__ = 'abilities'
    __singlename__ = 'ability'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)

class DamageClass(Base):
    """A damage class (physical, special, or non-damaging)."""

    __tablename__ = 'damage_classes'
    __singlename__ = 'damage_class'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class Gender(Base):
    """An enigma."""

    __tablename__ = 'genders'
    __singlename__ = 'gender'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

class Item(Base):
    """A type of item."""

    __tablename__ = 'items'
    __singlename__ = 'item'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    summary = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)

class Move(Base):
    """A move (a.k.a. an attack)."""

    __tablename__ = 'moves'
    __singlename__ = 'move'

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

class Pokemon(Base):
    """An individual Pokémon owned by a trainer."""

    __tablename__ = 'pokemon'
    __singlename__ = 'pokemon'

    pokemon_id_seq = Sequence('pokemon_id_seq')

    id = Column(Integer, pokemon_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        nullable=False)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    ability_slot = Column(Integer, nullable=False)
    experience = Column(Integer, nullable=False)
    happiness = Column(Integer, nullable=False)
    is_in_squad = Column(Boolean, nullable=False)
    can_evolve = Column(Boolean, nullable=False)
    form_uncertain = Column(Boolean, nullable=False)

    # Set up a composite foreign key for ability
    __table_args__ = (
        ForeignKeyConstraint(
            ['pokemon_form_id', 'ability_slot'],
            ['pokemon_form_abilities.pokemon_form_id',
             'pokemon_form_abilities.slot'],
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

        return [
            (sec.Allow, 'user:{0}'.format(self.trainer_id), 'edit:basics'),
            (sec.Allow, 'admin', 'edit:basics'),
            (sec.Allow, 'admin', 'edit:everything'),
            (sec.Deny, sec.Everyone, sec.ALL_PERMISSIONS)
        ]


class PokemonForm(Base):
    """A particular form of a Pokémon species.

    If a Pokémon only has one form, it still has a row in this table.
    """

    __tablename__ = 'pokemon_forms'
    __singlename__ = 'pokemon_form'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    species_id = Column(Integer, ForeignKey('pokemon_species.id'))
    is_default = Column(Boolean, nullable=False)

    @property
    def name(self):
        """To do"""
        return self.species.name

class PokemonFormAbility(Base):
    """One of a Pokémon form's abilities."""

    __tablename__ = 'pokemon_form_abilities'
    __singlename__ = 'pokemon_form_ability'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    slot = Column(Integer, primary_key=True)
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=False)
    is_hidden = Column(Boolean, nullable=False)

class PokemonSpecies(Base):
    """A species of Pokémon."""

    __tablename__ = 'pokemon_species'
    __singlename__ = 'pokemon_species'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)
    evolves_from_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        nullable=True)
    rarity = Column(Integer, ForeignKey('rarities.id'), nullable=True)
    is_starter = Column(Boolean, nullable=False)
    can_switch_forms = Column(Boolean, nullable=False)

    @property
    def number(self):
        """Return national dex number for canon Pokémon, or an "A##" number for
        fakemon,
        """

        if self.id < 10000:
            return '{0:03}'.format(self.id)
        else:
            return 'A{0:02}'.format(self.id - 10000)

class PokemonSpeciesEvolution(Base):
    """The method by which a Pokémon species evolves."""

    __tablename__ = 'pokemon_species_evolution'
    __singlename__ = 'pokemon_species_evolution'

    evolved_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        primary_key=True)
    experience = Column(Integer, nullable=True)
    happiness = Column(Integer, nullable=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=True)
    buyable_price = Column(Integer, nullable=True)
    can_trade_instead = Column(Boolean, nullable=False)

class Rarity(Base):
    """A Pokémon rarity."""

    __tablename__ = 'rarities'
    __singlename__ = 'rarity'

    id = Column(Integer, primary_key=True)

class Trainer(Base):
    """A member of the ASB league and user of this app thing."""

    __tablename__ = 'trainers'
    __singlename__ = 'trainer'

    trainers_id_seq = Sequence('trainers_id_seq')

    id = Column(Integer, trainers_id_seq, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False, default='')
    name = Column(Unicode, nullable=False)
    password_hash = Column(Unicode, nullable=True, default='')
    money = Column(Integer, nullable=False, default=45)
    can_collect_allowance = Column(Boolean, nullable=False, default=False)
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

class TrainerItem(Base):
    """An individual item owned by a trainer and possibly held by a Pokémon."""

    __tablename__ = 'trainer_items'
    __singlename__ = 'trainer_item'

    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id', onupdate='cascade'),
        nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    # XXX Some RDBMSes don't do nullable + unique right (but postgres does)
    pokemon_id = Column(Integer, ForeignKey('pokemon.id', onupdate='cascade'),
        nullable=True, unique=True)

class Type(Base):
    """A type (Normal, Fire, etc.)"""

    __tablename__ = 'types'
    __singlename__ = 'type'

    id = Column(Integer, primary_key=True)
    identifier = Column(Unicode, unique=True, nullable=False)
    name = Column(Unicode, nullable=False)

# Relationships go down here so that we don't have to use strings for
# everything

Move.type = relationship(Type)

Pokemon.ability = relationship(Ability,
    secondary=PokemonFormAbility.__table__, uselist=False)
Pokemon.form = relationship(PokemonForm)
Pokemon.gender = relationship(Gender)
Pokemon.item = relationship(Item,
    secondary=TrainerItem.__table__, uselist=False)
Pokemon.species = association_proxy('form', 'species')
Pokemon.trainer = relationship(Trainer, back_populates='pokemon')

PokemonForm.species = relationship(PokemonSpecies)

Trainer.pokemon = relationship(Pokemon, back_populates='trainer',
    order_by=Pokemon.id)
Trainer.squad = relationship(Pokemon,
    primaryjoin=and_(Pokemon.trainer_id == Trainer.id, Pokemon.is_in_squad))
Trainer.pc = relationship(Pokemon,
    primaryjoin=and_(Pokemon.trainer_id == Trainer.id, ~Pokemon.is_in_squad))

Trainer.bag = relationship(Item, secondary=TrainerItem.__table__,
    primaryjoin=and_(Trainer.id == TrainerItem.trainer_id,
                     TrainerItem.pokemon_id == None))
Trainer.items = relationship(Item, secondary=TrainerItem.__table__)

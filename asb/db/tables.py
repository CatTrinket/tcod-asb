from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *

TableBase = declarative_base()

class Ability(TableBase):
    """An ability."""
    __tablename__ = 'abilities'
    __singlename__ = 'ability'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

class Gender(TableBase):
    """An enigma."""
    __tablename__ = 'genders'
    __singlename__ = 'gender'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)

class Item(TableBase):
    """A type of item."""
    __tablename__ = 'items'
    __singlename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    description = Column(Unicode, nullable=False)

class Pokemon(TableBase):
    """An individual Pokémon owned by a trainer."""
    __tablename__ = 'pokemon'
    __singlename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        nullable=False)
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    experience = Column(Integer, nullable=False)
    happiness = Column(Integer, nullable=False)
    # XXX Some RDBMSes don't do nullable + unique right (but postgres does)
    held_item_id = Column(Integer, ForeignKey('trainer_items.id'),
        nullable=True, unique=True)
    is_in_squad = Column(Boolean, nullable=False)
    can_evolve = Column(Boolean, nullable=False)
    form_uncertain = Column(Boolean, nullable=False)

class PokemonForm(TableBase):
    """A particular form of a Pokémon.

    If a Pokémon only has one form, it still has a row in this table.
    """
    __tablename__ = 'pokemon_forms'
    __singlename__ = 'pokemon_form'

    id = Column(Integer, primary_key=True)
    species_id = Column(Integer, ForeignKey('pokemon_species.id'))
    is_default = Column(Boolean, nullable=False)

class PokemonFormAbility(TableBase):
    """One of a Pokémon form's abilities."""
    __tablename__ = 'pokemon_form_abilities'
    __singlename__ = 'pokemon_form_ability'

    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        primary_key=True)
    slot = Column(Integer, primary_key=True)
    ability_id = Column(Integer, ForeignKey('abilities.id'), nullable=False)
    is_hidden = Column(Boolean, nullable=False)

class PokemonSpecies(TableBase):
    """A species of Pokémon."""
    __tablename__ = 'pokemon_species'
    __singlename__ = 'pokemon_species'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    evolves_from_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        nullable=True)
    rarity = Column(Integer, ForeignKey('rarities.id'), nullable=False)
    is_starter = Column(Boolean, nullable=False)
    can_switch_forms = Column(Boolean, nullable=False)

class PokemonSpeciesEvolution(TableBase):
    """The method by which a Pokémon species evolves."""
    __tablename__ = 'pokemon_species_evolution'
    __singlename__ = 'pokemon_species_evolution'

    evolved_species_id = Column(Integer, ForeignKey('pokemon_species.id'),
        primary_key=True)
    experience = Column(Integer, nullable=True)
    happiness = Column(Integer, nullable=True)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=True)
    gender = Column(Integer, ForeignKey('genders.id'), nullable=True)
    is_buyable = Column(Boolean, nullable=False)
    can_trade_instead = Column(Boolean, nullable=False)

class Rarity(TableBase):
    """A Pokémon rarity."""
    __tablename__ = 'rarities'
    __singlename__ = 'rarity'

    id = Column(Integer, primary_key=True)

class Trainer(TableBase):
    """A member of the ASB league and user of this app thing."""
    __tablename__ = 'trainers'
    __singlename__ = 'trainer'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    money = Column(Integer, nullable=False)
    can_collect_allowance = Column(Boolean, nullable=False)
    unclaimed_from_hack = Column(Boolean, nullable=False)

class TrainerItem(TableBase):
    """An individual item owned by a trainer.

    Pokémon's held items are kept track of in the pokemon.held_item column.
    """

    __tablename__ = 'trainer_items'
    __singlename__ = 'trainer_item'

    id = Column(Integer, primary_key=True)
    trainer_id = Column(Integer, ForeignKey('trainers.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)

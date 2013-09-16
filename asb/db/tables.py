from sqlalchemy import Column, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import *

TableBase = declarative_base()

class Pokemon(TableBase):
    """An individual Pokémon owned by a trainer."""
    __tablename__ = 'pokemon'
    __singlename__ = 'pokemon'

    id = Column(Integer, primary_key=True)
    pokemon_form_id = Column(Integer, ForeignKey('pokemon_forms.id'),
        nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
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

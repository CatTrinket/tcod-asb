import sqlalchemy as sqla

import asb.db

def can_evolve(pokemon):
    """Return whether or not this Pokémon can evolve at all."""

    return any(can_evolve_species(pokemon, evo)[0]
               for evo in pokemon.species.evolutions)

def can_evolve_species(pokemon, species):
    """Return three things: whether or not this Pokémon can evolve into this
    species, whether or not they'll have to pay, and whether or not the
    appropriate item will have to be consumed.
    """

    # Make sure this species is an option in the first place
    if species.evolves_from_species_id != pokemon.form.species_id:
        return (False, False, False)

    evo = species.evolution_method

    # Shedinja has no evolution method
    if evo is None:
        return (False, False, False)

    # Gender requirements apply to all other methods
    if evo.gender_id is not None and pokemon.gender_id != evo.gender_id:
        return (False, False, False)

    # Go through all the methods
    if evo.experience is not None and pokemon.experience >= evo.experience:
        return (True, False, False)
    elif evo.happiness is not None and pokemon.happiness >= evo.happiness:
        return (True, False, False)
    elif evo.item is not None and has_battled_with(pokemon, evo.item):
        return (True, False, True)
    elif species in pokemon.unlocked_evolutions:
        return (True, False, evo.item_id is not None)
    elif (evo.buyable_price is not None and
          pokemon.trainer.money >= evo.buyable_price):
        return (True, True, False)
    else:
        # No dice
        return (False, False, False)

def check_form_condition(pokemon, form):
    """Check the specified Pokémon form's conditions, and return whether the
    Pokémon meets them.

    This method does not check whether the Pokémon is the same species.  For
    example, when evolving a Darumaka, you'll want to check whether it fulfils
    the conditions for Zen Darmanitan, and that works.

    It also does not check whether this Pokémon can actually switch to this
    form.  For example, a Shellos will show up as fulfilling the conditions for
    both its forms.  This is also intentional, because a pre-db Shellos /can/
    switch, exactly once.
    """

    c = form.condition

    if c is None:
        # No condition!  Woo!
        return True

    if c.gender_id is c.item_id is c.ability_id is None:
        # There is a condition, but its parameters are all blank at the moment,
        # meaning it requires an item that hasn't been added yet
        return False

    if c.gender_id is not None and pokemon.gender_id != c.gender_id:
        # Wrong gender
        return False

    if c.item_id is not None and pokemon.trainer_item.item_id != c.item_id:
        # Wrong held item
        return False

    if c.ability_id is not None:
        # Check the ability that this Pokémon would have if it were this  form
        try:
            pfa = asb.db.DBSession.query(db.PokemonFormAbility).get(
               (form.id, pokemon.ability_slot))
        except sqla.orm.exc.NoResultFound:
            # Welp
            return False

        if pfa.ability_id != c.ability_id:
            # Wrong ability
            return False

    # If we haven't bailed yet, we're good to go
    return True

def has_battled_with(pokemon, item):
    """Check whether the Pokémon has battled with this item, as its current
    species.
    """

    battle = (
        asb.db.DBSession.query(asb.db.BattlePokemon)
        .join(asb.db.BattlePokemon.form)
        .join(asb.db.BattlePokemon.trainer)
        .join(asb.db.BattleTrainer.battle)
        .filter(
             asb.db.BattlePokemon.pokemon_id == pokemon.id,
             asb.db.BattlePokemon.participated,
             asb.db.BattlePokemon.item_id == item.id,
             asb.db.PokemonForm.species_id == pokemon.form.species_id,
             asb.db.Battle.end_date.isnot(None),
             ~asb.db.Battle.needs_approval
        )
    )

    return asb.db.DBSession.query(battle.exists()).scalar()

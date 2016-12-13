import sqlalchemy as sqla

import asb.db

def can_evolve(pokemon):
    """Return whether or not this Pokémon can evolve at all."""

    return any(
        can_evolve_into(pokemon, form)[0]
        for species in pokemon.species.evolutions
        for form in species.forms
    )

def can_potentially_evolve_into(pokemon, form):
    """Determine whether this form is a valid evolution for this Pokémon in the
    first place, before checking the actual requirements.
    """

    # Make sure it's the right species
    if form.species.evolves_from_species_id != pokemon.form.species_id:
        return False

    # If this Pokémon can switch forms, or doesn't have forms (yet), it gets to
    # choose its post-evolution form
    can_pick_forms = (len(pokemon.species.forms) == 1 or
                      pokemon.species.can_switch_forms)

    if can_pick_forms:
        # If it can switch, check the requirements to switch to this form
        return check_form_condition(pokemon, form)
    else:
	# If it can't switch, make sure it's evolving into the corresponding
	# form
        return form.form_order == pokemon.form.form_order

def can_evolve_into(pokemon, form):
    """Return three things: whether or not this Pokémon can evolve into this
    form, whether or not they'll have to pay, and whether or not the
    appropriate item will have to be consumed.
    """

    # Make sure this species and form are valid in the first place
    if not can_potentially_evolve_into(pokemon, form):
        return (False, False, False)

    evo = form.evolution_method

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
    elif form.species in pokemon.unlocked_evolutions:
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

    If the form requires a specific ability, this function checks whether the
    Pokémon *would* have that ability if it were the right species.  (The
    reason for this is that, if this Pokémon is Darumaka, we want to check
    whether it can pick Zen Darmantian when evolving.)

    This function does not check whether the Pokémon can switch forms.  (The
    reason for this is that, for example, if this Pokémon is a pre-db Shellos,
    it *will* be able to switch forms once, so we want it to show up as meeting
    the requirements for both its forms.)
    """

    c = form.condition

    if c is None:
        # No condition!  Woo!
        return True

    if c.item_id is c.ability_id is None:
        # There is a condition, but its parameters are all blank at the moment,
        # meaning it requires an item that hasn't been added yet
        return False

    if c.item_id is not None and pokemon.trainer_item.item_id != c.item_id:
        # Wrong held item
        return False

    if c.ability_id is not None:
        # Check the ability that this Pokémon would have if it were this form
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

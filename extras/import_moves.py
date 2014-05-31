import argparse
import sys

import sqlalchemy as sqla

import asb.db
import pokedex.db

# Parse args
parser = argparse.ArgumentParser(description="Import movepools from veekun's "
    'database.  As of 2014-05-31, this works with current tcod-asb and the '
    '"python3-sort-of" branch of pokedex.')
parser.add_argument('pokedex_url',
    help='The SQLAlchemy URL of the pokedex database.')
parser.add_argument('asb_url',
    help='The SQLAlchemy URL of the ASB database.')

args = parser.parse_args(sys.argv[1:])

# Connect to both databases
pokedex_session = pokedex.db.connect(args.pokedex_url)
asb_engine = sqla.create_engine(args.asb_url)
asb.db.DBSession.configure(bind=asb_engine)

# Build movepools
print('building movepools...', end=' ', flush=True)

movepools = {}
families = (
    asb.DBSession.query(asb.db.PokemonFamily)
    .options(sqla.orm.subqueryload_all('species.forms'))
    .all()
)

for family in families:
    # Add empty movepools for all forms in this family; this has to be done
    # beforehand because one form might affect a later form
    for species in family.species:
        for form in species.forms:
            movepools[form.id] = set()

    for species in family.species:
        # Find species that also get any moves this species gets
        affected_species = [species]
        current_layer = [species]

        while current_layer:
            current_layer = [evo for species in current_layer
                for evo in species.evolutions]
            affected_species.extend(current_layer)

        for form in species.forms:
            # Get this form's moves
            moves = (
                pokedex_session.query(pokedex.db.tables.Move.id)
                .join(pokedex.db.tables.PokemonMove)
                .join(pokedex.db.tables.Pokemon)
                .join(pokedex.db.tables.PokemonForm)
                .filter(pokedex.db.tables.PokemonForm.identifier ==
                    form.identifier)
                .all()
            )

            moves = {move for (move,) in moves}

            # Update the movepools of all forms that get this form's moves.
            # This means all forms of all affected species, unless *this*
            # Pokémon is Wormadam, Rotom, Kyurem, or Meowstic.  (Burmy and
            # Espurr should still affect all forms of their respective evos.)
            affected_movepools = [
                movepools[other_form.id]
                for other_species in affected_species
                for other_form in other_species.forms
                if not (other_form.id != form.id and species.identifier in
                    ['wormadam', 'rotom', 'kyurem', 'meowstic'])
            ]

            for movepool in affected_movepools:
                movepool.update(moves)

asb.db.DBSession.close()
print('done')

# Do all the actual db-modifying in a transaction
with asb_engine.begin() as connection:
    # Delete old movepools
    print('deleting old movepools...', end=' ', flush=True)
    connection.execute(asb.db.PokemonFormMove.__table__.delete())
    print('done')

    # Insert EVERYTHING ALL AT ONCE
    print('inserting new movepools...', end=' ', flush=True)

    connection.execute(asb.db.PokemonFormMove.__table__.insert(), [
        {'pokemon_form_id': form, 'move_id': move}
        for form, moves in movepools.items()
        for move in moves
    ])

    print('done')

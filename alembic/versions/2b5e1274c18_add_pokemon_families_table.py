"""Add pokemon_families table.

Revision ID: 2b5e1274c18
Revises: 58e640283e
Create Date: 2014-03-13 20:56:27.715848

"""

# revision identifiers, used by Alembic.
revision = '2b5e1274c18'
down_revision = '58e640283e'

from alembic import op
import sqlalchemy as sa

fakemon_evolution = {
    10002: 10001,
    10004: 10003,
    10005: 10004,
    10008: 10007,
    10009: 10008,
    10010: 10008,
    10012: 10011,
    10013: 10012,
    10016: 10015,
    10019: 10018,
    10021: 10020,
    10022: 10021,
    10024: 10023,
    10026: 10025,
    10028: 10027,
    10029: 10028,
    10031: 10030,
    10033: 10032,
    10035: 10034,
}

pokemon_species = sa.sql.table('pokemon_species',
    sa.Column('id', sa.Integer),
    sa.Column('evolves_from_species_id', sa.Integer),
    sa.Column('is_fake', sa.Boolean),
    sa.Column('order', sa.Integer),
    sa.Column('pokemon_family_id', sa.Integer)
)

pokemon_families = sa.sql.table('pokemon_families',
    sa.Column('id', sa.Integer())
)

def upgrade():
    # Create this shit
    op.create_table('pokemon_families',
        sa.Column('id', sa.Integer(), primary_key=True)
    )

    op.add_column('pokemon_species', sa.Column('pokemon_family_id', sa.Integer()))

    # Update evolves_from_species_id for Fakemon — I don't have a proper
    # load-from-CSV thing going yet so I guess I have to do this
    for id, evolves_from_species_id in fakemon_evolution.items():
       op.execute(
           pokemon_species.update()
           .where(pokemon_species.c.id == id)
           .values({'evolves_from_species_id': evolves_from_species_id})
       )

    # Populate pokemon_families
    canon_family_rows = (
        sa.select([
            sa.func.generate_series(1, sa.func.count())
        ])
        .select_from(pokemon_species)
        .where(pokemon_species.c.evolves_from_species_id == None)
        .where(pokemon_species.c.is_fake == False)
    )

    fakemon_family_rows = (
        sa.select([
            sa.func.generate_series(1, sa.func.count()) + 10000
        ])
        .select_from(pokemon_species)
        .where(pokemon_species.c.evolves_from_species_id == None)
        .where(pokemon_species.c.is_fake == True)
    )

    for rows in [canon_family_rows, fakemon_family_rows]:
        op.execute(pokemon_families.insert().from_select(['id'], rows))

    # Set pokemon_family_id
    # How many root Pokémon come before this Pokémon or are this Pokémon?
    # This is not the *most* correct way of doing it but it's still correct
    alias = pokemon_species.alias()

    canon_id_subquery = (
        sa.select([sa.func.count()])
        .select_from(alias)
        .where(alias.c.evolves_from_species_id == None)
        .where(alias.c.order <= pokemon_species.c.order)
        .where(alias.c.is_fake == pokemon_species.c.is_fake)
    )

    fakemon_id_subquery = (
        sa.select([sa.func.count() + 10000])
        .select_from(alias)
        .where(alias.c.evolves_from_species_id == None)
        .where(alias.c.order <= pokemon_species.c.order)
        .where(alias.c.is_fake == pokemon_species.c.is_fake)
    )

    op.execute(pokemon_species.update()
        .where(pokemon_species.c.is_fake == False)
        .values(pokemon_family_id=canon_id_subquery))

    op.execute(pokemon_species.update()
        .where(pokemon_species.c.is_fake == True)
        .values(pokemon_family_id=fakemon_id_subquery))

    # Ok thank fuck.  Now just add some constraints.
    op.alter_column('pokemon_species', 'pokemon_family_id', nullable=False)
    op.create_unique_constraint(None, 'pokemon_species', ['id', 'pokemon_family_id'])
    op.create_foreign_key(None, 'pokemon_species', 'pokemon_species',
        ['evolves_from_species_id', 'pokemon_family_id'],
        ['id', 'pokemon_family_id'])

def downgrade():
    op.drop_column('pokemon_species', 'pokemon_family_id')
    op.drop_table('pokemon_families')

    pokemon_species.update().where(pokemon_species.c.is_fake == True).values(
        {'evolves_from_species_id': None})

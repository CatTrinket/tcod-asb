"""Drop pokemon.can_evolve; add pokemon_unlocked_evolutions table.

Revision ID: 3d427da16d9
Revises: 2df80754178
Create Date: 2014-04-02 15:39:02.376340

"""

# revision identifiers, used by Alembic.
revision = '3d427da16d9'
down_revision = '2df80754178'

from alembic import op
import sqlalchemy as sa


# table stubs we need here
pokemon_unlocked_evolutions = sa.sql.table('pokemon_unlocked_evolutions',
    sa.Column('pokemon_id', sa.Integer),
    sa.Column('evolved_species_id', sa.Integer)
)

pokemon = sa.sql.table('pokemon',
    sa.Column('id', sa.Integer),
    sa.Column('pokemon_form_id', sa.Integer),
    sa.Column('can_evolve', sa.Boolean)
)

pokemon_forms = sa.sql.table('pokemon_forms',
    sa.Column('id', sa.Integer),
    sa.Column('species_id', sa.Integer)
)

pokemon_species = sa.sql.table('pokemon_species',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode),
    sa.Column('evolves_from_species_id', sa.Integer)
)

pokemon_species_evolution = sa.sql.table('pokemon_species_evolution',
    sa.Column('evolved_species_id', sa.Integer),
    sa.Column('item_id', sa.Integer)
)


def upgrade():
    # Create table
    op.create_table('pokemon_unlocked_evolutions',
        sa.Column('pokemon_id', sa.Integer(), nullable=False),
        sa.Column('evolved_species_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['evolved_species_id'], ['pokemon_species.id'], ),
        sa.ForeignKeyConstraint(['pokemon_id'], ['pokemon.id'], ),
        sa.PrimaryKeyConstraint('pokemon_id', 'evolved_species_id')
    )

    # Insert evolutions.  Fuck.
    # I'm only going to make this Good Enough to work on the actual data I
    # inherited from the hack.  Specifically, the only evolutions we need to
    # insert are item evolutions, and we don't need to worry about branching
    # ones.  We do need to exclude Gallade, because there's this one Kirlia
    # that can_evolve because it has the exp to become Gardevoir but has never
    # battled holding a Dawn Stone.
    prevo_species = pokemon_species.alias(name='prevo_species')
    evo_species = pokemon_species.alias(name='evo_species')

    evo_getting_query = (
        sa.select([pokemon.c.id, evo_species.c.id])
        .select_from(
            pokemon
            .join(pokemon_forms, pokemon.c.pokemon_form_id ==
                pokemon_forms.c.id)
            .join(prevo_species, pokemon_forms.c.species_id ==
                prevo_species.c.id)
            .join(evo_species, prevo_species.c.id ==
                evo_species.c.evolves_from_species_id)
            .join(pokemon_species_evolution, evo_species.c.id ==
                pokemon_species_evolution.c.evolved_species_id)
        )
        .where(pokemon.c.can_evolve == True)
        .where(pokemon_species_evolution.c.item_id.isnot(None))
        .where(evo_species.c.identifier != 'gallade')
    )
    
    op.execute(pokemon_unlocked_evolutions.insert().from_select(
        ['pokemon_id', 'evolved_species_id'], evo_getting_query))

    op.drop_column('pokemon', 'can_evolve')

def downgrade():
    op.add_column('pokemon', sa.Column('can_evolve', sa.BOOLEAN(), nullable=False,
        default=False))
    op.drop_table('pokemon_unlocked_evolutions')

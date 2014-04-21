"""Release all the Fakemon into the wild.

Revision ID: 55dfbe7be3c
Revises: 463393b5d2a
Create Date: 2014-04-21 14:36:42.888745

"""

# revision identifiers, used by Alembic.
revision = '55dfbe7be3c'
down_revision = '463393b5d2a'

from alembic import op
import sqlalchemy as sa

pokemon = sa.sql.table('pokemon',
    sa.Column('id', sa.Integer),
    sa.Column('pokemon_form_id', sa.Integer),
    sa.Column('trainer_id', sa.Integer),
    sa.Column('experience', sa.Integer),
    sa.Column('happiness', sa.Integer)
)

pokemon_forms = sa.sql.table('pokemon_forms',
    sa.Column('id', sa.Integer),
    sa.Column('species_id', sa.Integer)
)

pokemon_species = sa.sql.table('pokemon_species',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode),
    sa.Column('rarity_id', sa.Integer),
    sa.Column('is_fake', sa.Boolean),
    sa.Column('evolves_from_species_id', sa.Integer),
    sa.Column('pokemon_family_id', sa.Integer)
)

rarities = sa.sql.table('rarities',
    sa.Column('id', sa.Integer),
    sa.Column('price', sa.Integer)
)

trainers = sa.sql.table('trainers',
    sa.Column('id', sa.Integer),
    sa.Column('money', sa.Integer)
)

trainer_items = sa.sql.table('trainer_items',
    sa.Column('id', sa.Integer),
    sa.Column('pokemon_id', sa.Integer),
    sa.Column('item_id', sa.Integer),
    sa.Column('trainer_id', sa.Integer)
)

def do_fakemon_joins(select):
    return (
        select
        .where(pokemon_species.c.is_fake == True)
        .join(pokemon_forms, pokemon.c.pokemon_form_id == pokemon_forms.c.id)
        .join(pokemon_species, pokemon_forms.c.species_id ==
            pokemon_species.c.id)
    )

def upgrade():
    # Get the connection.  We can't really do this in pure SQL.
    connection = op.get_bind()

    # Give Hennic a rarity so we can replace it with money
    connection.execute(
        pokemon_species.update()
        .where(pokemon_species.c.identifier == 'hennic') 
        .values({'rarity_id': 7})
    )

    # Get all the fakemon
    fakemon = connection.execute(
        sa.sql.select([pokemon])
        .where(pokemon_species.c.is_fake == True)
        .select_from(
            pokemon.join(pokemon_forms, pokemon.c.pokemon_form_id ==
                pokemon_forms.c.id)
            .join(pokemon_species, pokemon_forms.c.species_id ==
                pokemon_species.c.id)
        )
    )

    # Set the trainer item sequence
    if connection.dialect.name == 'postgresql':
        connection.execute(sa.sql.expression.func.setval('trainer_items_id_seq',
            sa.sql.expression.func.max(trainer_items.c.id)))

    for a_fakemon in fakemon:
        # Put its item back in the bag
        connection.execute(
            trainer_items.update()
            .where(trainer_items.c.pokemon_id == a_fakemon.id)
            .values({'pokemon_id': None})
        )

        # Give money
        root_species = pokemon_species.alias()

        (money,), = connection.execute(
            sa.sql.select([rarities.c.price])
            .select_from(
                pokemon_forms.join(pokemon_species, pokemon_forms.c.species_id
                    == pokemon_species.c.id)
                .join(root_species, sa.sql.and_(
                    pokemon_species.c.pokemon_family_id ==
                        root_species.c.pokemon_family_id,
                    root_species.c.evolves_from_species_id.is_(None)
                ))
                .join(rarities, root_species.c.rarity_id == rarities.c.id)
            )
            .where(pokemon_forms.c.id == a_fakemon.pokemon_form_id)
        )

        connection.execute(
            trainers.update()
            .where(trainers.c.id == a_fakemon.trainer_id)
            .values({'money': trainers.c.money + money})
        )

        # Give candies
        candies = max(a_fakemon.experience, a_fakemon.happiness)

        for candy in range(candies):
            connection.execute(
                trainer_items.insert()
                .values({'item_id': 1, 'trainer_id': a_fakemon.trainer_id})
            )

        # Release it
        connection.execute(sa.sql.delete(pokemon)
            .where(pokemon.c.id == a_fakemon.id))


def downgrade():
    # There is nothing we can do
    pass

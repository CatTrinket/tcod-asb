"""make pokemon.id mutable

Revision ID: 7a31736914
Revises: 3d55c92f22d
Create Date: 2013-10-09 15:48:07.569646

"""

# revision identifiers, used by Alembic.
revision = '7a31736914'
down_revision = '3d55c92f22d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # I forgot to add this in the first place so I don't have to drop it eheheh
    op.create_foreign_key('trainer_items_pokemon_id_fkey',
        'trainer_items', 'pokemon',
        ['pokemon_id'], ['id'],
        onupdate='cascade')


def downgrade():
    op.drop_constraint('trainer_items_pokemon_id_fkey', 'trainer_items')

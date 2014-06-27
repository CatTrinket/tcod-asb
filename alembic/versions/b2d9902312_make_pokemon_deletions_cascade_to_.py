"""Make pokemon deletions cascade to pokemon_unlocked_evolutions..

Revision ID: b2d9902312
Revises: 3601b66724c
Create Date: 2014-06-27 00:50:46.942846

"""

# revision identifiers, used by Alembic.
revision = 'b2d9902312'
down_revision = '3601b66724c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint('pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions')
    op.create_foreign_key(None, 'pokemon_unlocked_evolutions', 'pokemon',
        ['pokemon_id'], ['id'], ondelete='cascade')


def downgrade():
    op.drop_constraint('pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions')
    op.create_foreign_key(None, 'pokemon_unlocked_evolutions', 'pokemon',
        ['pokemon_id'], ['id'])

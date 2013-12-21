"""Rename pokemon_species.rarity to rarity_id.

Revision ID: 43f39d0d550
Revises: 36e5adfc58
Create Date: 2013-12-16 00:07:16.615340

"""

# revision identifiers, used by Alembic.
revision = '43f39d0d550'
down_revision = '36e5adfc58'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('pokemon_species', 'rarity', new_column_name='rarity_id')

def downgrade():
    op.alter_column('pokemon_species', 'rarity_id', new_column_name='rarity')

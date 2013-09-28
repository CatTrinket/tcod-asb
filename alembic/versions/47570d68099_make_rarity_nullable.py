"""make rarity nullable

Revision ID: 47570d68099
Revises: 1408e69cba7
Create Date: 2013-09-27 17:47:14.899017

"""

# revision identifiers, used by Alembic.
revision = '47570d68099'
down_revision = '1408e69cba7'

from alembic import op

def upgrade():
    op.alter_column('pokemon_species', 'rarity', nullable=True)


def downgrade():
    op.alter_column('pokemon_species', 'rarity', nullable=False)

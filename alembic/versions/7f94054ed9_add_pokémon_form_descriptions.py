"""Add Pokémon form descriptions.

Revision ID: 7f94054ed9
Revises: 2ce99f498f1
Create Date: 2014-07-10 21:22:14.672839

"""

# revision identifiers, used by Alembic.
revision = '7f94054ed9'
down_revision = '2ce99f498f1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pokemon_species', sa.Column('form_explanation',
        sa.Unicode(), nullable=True))


def downgrade():
    op.drop_column('pokemon_species', 'form_explanation')

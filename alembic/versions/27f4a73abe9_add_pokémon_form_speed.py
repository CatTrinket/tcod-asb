"""Add Pokémon form speed.

Revision ID: 27f4a73abe9
Revises: 26cdc8cfb6c
Create Date: 2015-01-30 23:45:41.667659

"""

# revision identifiers, used by Alembic.
revision = '27f4a73abe9'
down_revision = '26cdc8cfb6c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pokemon_forms', sa.Column('speed', sa.Integer(),
        nullable=False, server_default='1'))
    op.alter_column('pokemon_forms', 'speed', server_default=None)

def downgrade():
    op.drop_column('pokemon_forms', 'speed')

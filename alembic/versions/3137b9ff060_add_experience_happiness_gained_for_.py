"""Add experience/happiness gained for battle_pokemon.

Revision ID: 3137b9ff060
Revises: 429795c0ac9
Create Date: 2014-08-29 13:03:10.465972

"""

# revision identifiers, used by Alembic.
revision = '3137b9ff060'
down_revision = '429795c0ac9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('battle_pokemon', sa.Column('happiness_gained',
        sa.Integer(), nullable=True))
    op.add_column('battle_pokemon', sa.Column('experience_gained',
        sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('battle_pokemon', 'happiness_gained')
    op.drop_column('battle_pokemon', 'experience_gained')

"""Carry is_shiny over to battle_pokemon.

Revision ID: 4345928f238
Revises: 2ff96540b89
Create Date: 2015-08-02 23:46:48.132000

"""

# revision identifiers, used by Alembic.
revision = '4345928f238'
down_revision = '2ff96540b89'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('battle_pokemon',
                  sa.Column('is_shiny', sa.Boolean(), nullable=False,
                            server_default='false'))
    op.alter_column('battle_pokemon', 'is_shiny', server_default=None)


def downgrade():
    op.drop_column('battle_pokemon', 'is_shiny')

"""Add Pokémon shininess.

Revision ID: 2ff96540b89
Revises: 2505a3a8221
Create Date: 2015-08-02 21:24:16.772676

"""

# revision identifiers, used by Alembic.
revision = '2ff96540b89'
down_revision = '2505a3a8221'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pokemon', sa.Column('is_shiny', sa.Boolean(),
                                       nullable=False, server_default='false'))
    op.alter_column('pokemon', 'is_shiny', server_default=None)


def downgrade():
    op.drop_column('pokemon', 'is_shiny')

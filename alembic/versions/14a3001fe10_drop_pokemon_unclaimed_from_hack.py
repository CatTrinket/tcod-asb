"""Drop pokemon.unclaimed_from_hack.

Revision ID: 14a3001fe10
Revises: 4ad9caff49c
Create Date: 2014-06-03 11:59:59.383208

"""

# revision identifiers, used by Alembic.
revision = '14a3001fe10'
down_revision = '4ad9caff49c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('pokemon', 'unclaimed_from_hack')


def downgrade():
    op.add_column('pokemon', sa.Column('unclaimed_from_hack', sa.BOOLEAN(),
        nullable=False, server_default='True'))
    op.alter_column('pokemon', 'unclaimed_from_hack', server_default=None)

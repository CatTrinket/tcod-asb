"""Add column battles.needs_approval.

Revision ID: 429795c0ac9
Revises: 4d5e6e65a81
Create Date: 2014-08-27 15:04:52.356688

"""

# revision identifiers, used by Alembic.
revision = '429795c0ac9'
down_revision = '4d5e6e65a81'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('battles', sa.Column('needs_approval', sa.Boolean(),
        nullable=False, server_default='false'))
    op.alter_column('battles', 'needs_approval', server_default=None)


def downgrade():
    op.drop_column('battles', 'needs_approval')

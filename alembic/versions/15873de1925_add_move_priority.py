"""Add move priority.

Revision ID: 15873de1925
Revises: 507ba0d38e9
Create Date: 2014-05-22 21:32:21.530927

"""

# revision identifiers, used by Alembic.
revision = '15873de1925'
down_revision = '507ba0d38e9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('moves', sa.Column('priority', sa.Integer(), nullable=False,
        server_default='0'))
    op.alter_column('moves', 'priority', server_default=None)


def downgrade():
    op.drop_column('moves', 'priority')

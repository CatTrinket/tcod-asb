"""Add column trainer.is_validated.

Revision ID: 36294fb4189
Revises: 542b9e9c3eb
Create Date: 2014-06-14 14:29:55.240852

"""

# revision identifiers, used by Alembic.
revision = '36294fb4189'
down_revision = '542b9e9c3eb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('trainers', sa.Column('is_validated', sa.Boolean(),
        nullable=False, server_default='False'))
    op.alter_column('trainers', 'is_validated', server_default=None)


def downgrade():
    op.drop_column('trainers', 'is_validated')

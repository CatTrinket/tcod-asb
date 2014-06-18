"""Add TCoDf user IDs to trainers.

Revision ID: 432cb17cfe5
Revises: 36294fb4189
Create Date: 2014-06-14 15:04:14.156102

"""

# revision identifiers, used by Alembic.
revision = '432cb17cfe5'
down_revision = '36294fb4189'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('trainers', sa.Column('tcodf_user_id', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('trainers', 'tcodf_user_id')

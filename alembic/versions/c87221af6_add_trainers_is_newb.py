"""add trainers.is_newbie

Revision ID: c87221af6
Revises: 53491594f61
Create Date: 2013-09-27 19:40:08.352072

"""

# revision identifiers, used by Alembic.
revision = 'c87221af6'
down_revision = '53491594f61'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('trainers', sa.Column('is_newbie', sa.Boolean(), nullable=False))


def downgrade():
    op.drop_column('trainers', 'is_newbie')

"""make pokemon.trainer non-nullable

Revision ID: 17bdce9d660
Revises: 118f7dcf328
Create Date: 2013-09-28 10:22:10.863840

"""

# revision identifiers, used by Alembic.
revision = '17bdce9d660'
down_revision = '118f7dcf328'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('pokemon', 'trainer_id', nullable=False)


def downgrade():
    op.alter_column('pokemon', 'trainer_id', nullable=True)

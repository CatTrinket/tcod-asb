"""Add column battle_referees.is_current_ref.

Revision ID: 26cdc8cfb6c
Revises: 3137b9ff060
Create Date: 2014-09-05 14:40:10.393693

"""

# revision identifiers, used by Alembic.
revision = '26cdc8cfb6c'
down_revision = '3137b9ff060'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('battle_referees', sa.Column('is_current_ref', sa.Boolean(),
        nullable=False, server_default='false'))
    op.alter_column('battle_referees', 'is_current_ref', server_default=None)


def downgrade():
    op.drop_column('battle_referees', 'is_current_ref')

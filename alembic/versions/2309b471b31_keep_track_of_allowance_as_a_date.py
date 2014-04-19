"""Keep track of allowance as a date.

Revision ID: 2309b471b31
Revises: 19dc584f14d
Create Date: 2014-04-19 14:29:29.205938

"""

# revision identifiers, used by Alembic.
revision = '2309b471b31'
down_revision = '19dc584f14d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('trainers', sa.Column('last_collected_allowance', sa.Date(),
        nullable=True))
    op.drop_column('trainers', 'can_collect_allowance')


def downgrade():
    op.add_column('trainers', sa.Column('can_collect_allowance', sa.BOOLEAN(),
        nullable=False, server_default=True))
    op.alter_column('trainers', 'can_collect_allowance', server_default=None)
    op.drop_column('trainers', 'last_collected_allowance')

"""Add item prices.

Revision ID: 463393b5d2a
Revises: 2309b471b31
Create Date: 2014-04-19 19:21:25.477083

"""

# revision identifiers, used by Alembic.
revision = '463393b5d2a'
down_revision = '2309b471b31'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('items', sa.Column('price', sa.Integer(), nullable=True))


def downgrade():
    op.drop_column('items', 'price')

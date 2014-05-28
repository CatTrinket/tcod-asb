"""Add bank transaction table.

Revision ID: 31e70373b94
Revises: 15873de1925
Create Date: 2014-05-23 12:46:38.933284

"""

# revision identifiers, used by Alembic.
revision = '31e70373b94'
down_revision = '15873de1925'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('bank_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('tcod_post_id', sa.Integer(), nullable=False),
        sa.Column('is_pending', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('bank_transactions')

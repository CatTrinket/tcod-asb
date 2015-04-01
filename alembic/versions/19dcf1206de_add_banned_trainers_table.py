"""Add banned_trainers table.

Revision ID: 19dcf1206de
Revises: 42a62c35cae
Create Date: 2015-03-31 19:40:45.488052

"""

# revision identifiers, used by Alembic.
revision = '19dcf1206de'
down_revision = '42a62c35cae'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('banned_trainers',
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('banned_by_trainer_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['banned_by_trainer_id'], ['trainers.id']),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id']),
        sa.PrimaryKeyConstraint('trainer_id')
    )


def downgrade():
    op.drop_table('banned_trainers')

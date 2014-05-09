"""Add role tables.

Revision ID: 145892d5dab
Revises: 33cf26f89d0
Create Date: 2014-05-05 13:43:50.581618

"""

# revision identifiers, used by Alembic.
revision = '145892d5dab'
down_revision = '33cf26f89d0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier')
    )
    op.create_table('trainer_roles',
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], onupdate='cascade'),
        sa.PrimaryKeyConstraint('trainer_id', 'role_id')
    )


def downgrade():
    op.drop_table('trainer_roles')
    op.drop_table('roles')

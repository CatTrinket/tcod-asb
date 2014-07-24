"""Add tables for signature stuff.

Revision ID: 4fe95ab7ccf
Revises: 18dafc50e6f
Create Date: 2014-07-23 13:23:41.032908

"""

# revision identifiers, used by Alembic.
revision = '4fe95ab7ccf'
down_revision = '18dafc50e6f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'body_modifications',
        sa.Column('pokemon_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('is_repeatable', sa.Boolean(), nullable=False),
        sa.Column('flavor', sa.Unicode(), nullable=False),
        sa.Column('effect', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['pokemon_id'], ['pokemon.id'],
            onupdate='cascade'),
        sa.PrimaryKeyConstraint('pokemon_id')
    )

    op.create_table(
        'move_modifications',
        sa.Column('pokemon_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('type', sa.Unicode(), nullable=True),
        sa.Column('power', sa.Unicode(), nullable=True),
        sa.Column('energy', sa.Unicode(), nullable=True),
        sa.Column('accuracy', sa.Unicode(), nullable=True),
        sa.Column('target', sa.Unicode(), nullable=True),
        sa.Column('gap', sa.Unicode(), nullable=True),
        sa.Column('duration', sa.Unicode(), nullable=True),
        sa.Column('stat', sa.Unicode(), nullable=True),
        sa.Column('flavor', sa.Unicode(), nullable=True),
        sa.Column('effect', sa.Unicode(), nullable=True),
        sa.ForeignKeyConstraint(['pokemon_id'], ['pokemon.id'],
            onupdate='cascade'),
        sa.PrimaryKeyConstraint('pokemon_id')
    )


def downgrade():
    op.drop_table('move_modifications')
    op.drop_table('body_modifications')

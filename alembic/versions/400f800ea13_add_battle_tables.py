"""Add battle tables.

Revision ID: 400f800ea13
Revises: 4fe95ab7ccf
Create Date: 2014-07-24 15:59:14.372590

"""

# revision identifiers, used by Alembic.
revision = '400f800ea13'
down_revision = '4fe95ab7ccf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('battles',
        sa.Column('id', sa.Integer(), sa.Sequence('battles_id_seq'),
            nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('name')
    )

    op.create_table('battle_teams',
        sa.Column('battle_id', sa.Integer(), nullable=False),
        sa.Column('team_number', sa.Integer(), autoincrement=False,
            nullable=False),
        sa.Column('won', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['battle_id'], ['battles.id'], ),
        sa.PrimaryKeyConstraint('battle_id', 'team_number')
    )

    op.create_table('battle_referees',
        sa.Column('battle_id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('is_emergency_ref', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['battle_id'], ['battles.id'], ),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('battle_id', 'trainer_id')
    )

    op.create_table('battle_trainers',
        sa.Column('id', sa.Integer(), sa.Sequence('battle_trainers_id_seq'),
            nullable=False),
        sa.Column('battle_id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('team_number', sa.Integer(), autoincrement=False,
            nullable=True),
        sa.ForeignKeyConstraint(
            ['battle_id', 'team_number'],
            ['battle_teams.battle_id', 'battle_teams.team_number'],
            name='battle_trainer_team_fkey'
        ),
        sa.ForeignKeyConstraint(['battle_id'], ['battles.id'], ),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('battle_id', 'trainer_id')
    )

    op.create_table('battle_pokemon',
        sa.Column('id', sa.Integer(), sa.Sequence('battle_pokemon_id_seq'),
            nullable=False),
        sa.Column('pokemon_id', sa.Integer(), nullable=True),
        sa.Column('battle_trainer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('pokemon_form_id', sa.Integer(), nullable=False),
        sa.Column('ability_slot', sa.Integer(), nullable=False),
        sa.Column('item_id', sa.Integer(), nullable=True),
        sa.Column('experience', sa.Integer(), nullable=False),
        sa.Column('happiness', sa.Integer(), nullable=False),
        sa.Column('participated', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['battle_trainer_id'], ['battle_trainers.id']),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.ForeignKeyConstraint(['pokemon_form_id'], ['pokemon_forms.id']),
        sa.ForeignKeyConstraint(['pokemon_id'], ['pokemon.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('battle_pokemon')
    op.drop_table('battle_trainers')
    op.drop_table('battle_referees')
    op.drop_table('battle_teams')
    op.drop_table('battles')

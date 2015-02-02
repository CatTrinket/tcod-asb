"""Add trading tables.

Revision ID: 4326326a3c0
Revises: 4ef0dceb2d3
Create Date: 2015-02-01 16:59:08.573627

"""

# revision identifiers, used by Alembic.
revision = '4326326a3c0'
down_revision = '4ef0dceb2d3'

from alembic import op
import sqlalchemy as sa


pokemon = sa.sql.table(
    'pokemon',
    sa.Column('trainer_id', sa.Integer),
    sa.Column('original_trainer_id', sa.Integer)
)

def upgrade():
    op.create_table(
        'trades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('is_gift', sa.Boolean(), nullable=False),
        sa.Column('approved', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'trade_trainers',
        sa.Column('trade_id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=False),
        sa.Column('accepted', sa.Boolean(), nullable=False),
        sa.Column('money', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], ),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('trade_id', 'trainer_id')
    )

    op.add_column('pokemon', sa.Column('original_trainer_id', sa.Integer(),
        sa.ForeignKey('trainers.id'), nullable=True))

    op.execute(
        pokemon.update()
        .values(original_trainer_id=pokemon.c.trainer_id)
    )

    op.add_column('pokemon', sa.Column('trade_id', sa.Integer(),
        sa.ForeignKey('trades.id'), nullable=True))
    op.add_column('trainer_items', sa.Column('trade_id', sa.Integer(),
        sa.ForeignKey('trades.id'), nullable=True))

    op.create_foreign_key(
        'pokemon_trader_fkey', 'pokemon', 'trade_trainers',
        ['trade_id', 'trainer_id'], ['trade_id', 'trainer_id']
    )

    op.create_foreign_key(
        'item_trader_fkey', 'trainer_items', 'trade_trainers',
        ['trade_id', 'trainer_id'], ['trade_id', 'trainer_id']
    )

def downgrade():
    op.drop_constraint('item_trader_fkey', 'trainer_items')
    op.drop_constraint('pokemon_trader_fkey', 'pokemon')

    op.drop_column('trainer_items', 'trade_id')
    op.drop_column('pokemon', 'trade_id')
    op.drop_column('pokemon', 'original_trainer_id')

    op.drop_table('trade_trainers')
    op.drop_table('trades')

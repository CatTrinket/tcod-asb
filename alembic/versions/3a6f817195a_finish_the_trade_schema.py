"""Finish the trade schema.

Revision ID: 3a6f817195a
Revises: 31df6b83b3b
Create Date: 2015-12-20 17:33:43.401776

"""

# revision identifiers, used by Alembic.
revision = '3a6f817195a'
down_revision = '31df6b83b3b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    trade_lot_states = op.create_table(
        'trade_lot_states',
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('identifier')
    )

    op.bulk_insert(trade_lot_states, [
        {'identifier': 'draft'},
        {'identifier': 'proposed'},
        {'identifier': 'accepted'},
        {'identifier': 'rejected'}
    ])

    op.create_table(
        'trade_lots',
        sa.Column('id', sa.Integer, nullable=False, primary_key=True),
        sa.Column('trade_id', sa.Integer, sa.ForeignKey('trades.id'),
                  nullable=False),
        sa.Column('in_exchange_for_id', sa.Integer,
                  sa.ForeignKey('trade_lots.id'), nullable=True),
        sa.Column('sender_id', sa.Integer, sa.ForeignKey('trainers.id'),
                  nullable=True),
        sa.Column('recipient_id', sa.Integer, sa.ForeignKey('trainers.id'),
                  nullable=True),
        sa.Column('state', sa.Unicode,
                  sa.ForeignKey('trade_lot_states.identifier'),
                  nullable=False),
        sa.Column('money', sa.Integer, nullable=True),
        sa.Column('notify_recipient', sa.Boolean, nullable=False),

        sa.UniqueConstraint('id', 'trade_id', 'sender_id', 'recipient_id'),
        sa.ForeignKeyConstraint(
            ['in_exchange_for_id', 'trade_id', 'recipient_id', 'sender_id'],
            ['trade_lots.id', 'trade_lots.trade_id', 'trade_lots.sender_id',
             'trade_lots.recipient_id']
        )
    )

    op.create_table(
        'trade_lot_pokemon',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('trade_lot_id', sa.Integer, sa.ForeignKey('trade_lots.id'),
                  nullable=False),
        sa.Column('pokemon_id', sa.Integer, sa.ForeignKey('pokemon.id'),
                  nullable=True)
    )

    op.create_table(
        'trade_lot_items',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('trade_lot_id', sa.Integer, sa.ForeignKey('trade_lots.id'),
                  nullable=False),
        sa.Column('trainer_item_id', sa.Integer,
                  sa.ForeignKey('trainer_items.id'), nullable=True),
        sa.Column('item_id', sa.Integer, sa.ForeignKey('items.id'),
                  nullable=False)
    )

    op.drop_constraint('pokemon_trader_fkey', 'pokemon')
    op.drop_constraint('pokemon_trade_id_fkey', 'pokemon')
    op.drop_column('pokemon', 'trade_id')

    op.drop_constraint('item_trader_fkey', 'trainer_items')
    op.drop_constraint('trainer_items_trade_id_fkey', 'trainer_items')
    op.drop_column('trainer_items', 'trade_id')

    op.drop_table('trade_trainers')

    op.add_column('trades', sa.Column('completed', sa.Boolean, nullable=False))
    op.add_column('trades', sa.Column('reveal_date', sa.Date(), nullable=True))
    op.drop_column('trades', 'approved')

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trainer_items', sa.Column('trade_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('trainer_items_trade_id_fkey', 'trainer_items', 'trades', ['trade_id'], ['id'])
    op.create_foreign_key('item_trader_fkey', 'trainer_items', 'trade_trainers', ['trade_id', 'trainer_id'], ['trade_id', 'trainer_id'])
    op.add_column('trades', sa.Column('approved', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column('trades', 'reveal_date')
    op.drop_column('trades', 'completion_read')
    op.drop_column('trades', 'completed')
    op.add_column('pokemon', sa.Column('trade_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('pokemon_trade_id_fkey', 'pokemon', 'trades', ['trade_id'], ['id'])
    op.create_foreign_key('pokemon_trader_fkey', 'pokemon', 'trade_trainers', ['trade_id', 'trainer_id'], ['trade_id', 'trainer_id'])
    op.create_table('trade_trainers',
    sa.Column('trade_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('trainer_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('accepted', sa.BOOLEAN(), autoincrement=False, nullable=False),
    sa.Column('money', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['trade_id'], ['trades.id'], name='trade_trainers_trade_id_fkey'),
    sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], name='trade_trainers_trainer_id_fkey'),
    sa.PrimaryKeyConstraint('trade_id', 'trainer_id', name='trade_trainers_pkey')
    )
    op.drop_table('trade_lot_items')
    op.drop_table('trade_lot_pokemon')
    op.drop_table('trade_lots')
    op.drop_table('trade_lot_states')
    ### end Alembic commands ###

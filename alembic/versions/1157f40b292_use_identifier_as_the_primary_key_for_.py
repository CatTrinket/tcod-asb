"""Use identifier as the primary key for bank_transaction_states.

Revision ID: 1157f40b292
Revises: 19b597c2317
Create Date: 2014-07-12 08:52:18.965815

"""

# revision identifiers, used by Alembic.
revision = '1157f40b292'
down_revision = '19b597c2317'

from alembic import op
import sqlalchemy as sa

bank_transactions = sa.sql.table(
    'bank_transactions',
    sa.Column('state_id', sa.Integer),
    sa.Column('state', sa.Unicode)
)

bank_transaction_states = sa.sql.table(
    'bank_transaction_states',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode)
)

states = [(1, 'pending'), (2, 'processed'), (3, 'acknowledged')]

def upgrade():
    # Turn state_id into state
    op.add_column('bank_transactions', sa.Column('state', sa.Unicode,
        nullable=False, server_default='pending'))

    for (state_id, state) in states:
        op.execute(
            bank_transactions.update()
            .where(bank_transactions.c.state_id == state_id)
            .values({'state': state})
        )

    op.alter_column('bank_transactions', 'state', server_default=None)
    op.drop_column('bank_transactions', 'state_id')

    # Drop old keys and ID column
    op.drop_constraint('bank_transaction_states_identifier_key',
        'bank_transaction_states')
    op.drop_constraint('bank_transaction_states_pkey',
        'bank_transaction_states')
    op.drop_column('bank_transaction_states', 'id')

    # Create new keys
    op.create_primary_key('bank_transaction_states_pkey',
        'bank_transaction_states', ['identifier'])
    op.create_foreign_key('bank_transactions_state_fkey',
        'bank_transactions', 'bank_transaction_states',
        ['state'], ['identifier'])

def downgrade():
    # Turn state into state_id
    op.add_column('bank_transactions', sa.Column('state_id', sa.Integer,
        nullable=False, server_default='1'))

    for (state_id, state) in states:
        op.execute(
            bank_transactions.update()
            .where(bank_transactions.c.state == state)
            .values({'state_id': state_id})
        )

    op.alter_column('bank_transactions', 'state_id', server_default=None)
    op.drop_column('bank_transactions', 'state')

    # Recreate ID column
    op.add_column('bank_transaction_states', sa.Column('id', sa.Integer,
        nullable=True))

    for (state_id, state) in states:
        op.execute(
            bank_transaction_states.update()
            .where(bank_transaction_states.c.identifier == state)
            .values({'id': state_id})
        )

    op.alter_column('bank_transaction_states', 'id', nullable=False)

    # Drop new keys and recreate old ones
    op.drop_constraint('bank_transaction_states_pkey',
        'bank_transaction_states')
    op.create_primary_key('bank_transaction_states_pkey',
        'bank_transaction_states', ['id'])
    op.create_unique_constraint('bank_transaction_states_identifier_key',
        'bank_transaction_states', ['identifier'])
    op.create_foreign_key('bank_transactions_state_id_fkey',
        'bank_transactions', 'bank_transaction_states',
        ['state_id'], ['id'])

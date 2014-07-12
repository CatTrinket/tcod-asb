"""Tweak bank transaction state.

Revision ID: 19b597c2317
Revises: 7f94054ed9
Create Date: 2014-07-11 19:33:51.737618

"""

# revision identifiers, used by Alembic.
revision = '19b597c2317'
down_revision = '7f94054ed9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

state_enum = sa.Enum('pending', 'approved', 'denied',
    name='bank_transaction_state')

bank_transactions = sa.sql.table(
    'bank_transactions',
    sa.Column('is_approved', sa.Boolean),
    sa.Column('state', state_enum),
    sa.Column('state_id', sa.Integer)
)

bank_transaction_states = sa.sql.table(
    'bank_transaction_states',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode)
)

def upgrade():
    op.create_table(
        'bank_transaction_states',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier')
    )

    op.bulk_insert(
        bank_transaction_states,
        [
            {'id': 1, 'identifier': 'pending'},
            {'id': 2, 'identifier': 'processed'},
            {'id': 3, 'identifier': 'acknowledged'}
        ]
    )

    op.add_column('bank_transactions', sa.Column('is_approved', sa.Boolean(),
        nullable=False, server_default='False'))

    op.add_column('bank_transactions', sa.Column('state_id', sa.Integer(),
        nullable=False, server_default='1'))

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.state == 'approved')
        .values({'is_approved': True, 'state_id': 2})
    )

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.state == 'denied')
        .values({'is_approved': False, 'state_id': 2})
    )

    op.alter_column('bank_transactions', 'is_approved', server_default=None)
    op.alter_column('bank_transactions', 'state_id', server_default=None)
    op.drop_column('bank_transactions', 'state')


def downgrade():
    op.add_column('bank_transactions', sa.Column('state', state_enum,
        nullable=False, server_default='pending'))

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.is_approved == True)
        .values({'state': 'approved'})
    )

    op.execute(
        bank_transactions.update()
        .where(sa.and_(
            bank_transactions.c.state_id != 1,
            bank_transactions.c.is_approved == False
        ))
        .values({'state': 'denied'})
    )

    op.alter_column('bank_transactions', 'state_id', server_default=None)
    op.drop_column('bank_transactions', 'state_id')
    op.drop_column('bank_transactions', 'is_approved')
    op.drop_table('bank_transaction_states')

"""Change bank transaction states around.

Revision ID: 40812ed2617
Revises: 46b1da464a3
Create Date: 2015-03-11 21:10:32.266127

"""

# revision identifiers, used by Alembic.
revision = '40812ed2617'
down_revision = '46b1da464a3'

from alembic import op
import sqlalchemy as sa

bank_transaction_states = sa.sql.table(
    'bank_transaction_states',
    sa.Column('identifier', sa.Unicode)
)

bank_transactions = sa.sql.table(
    'bank_transactions',
    sa.Column('state', sa.Unicode),
    sa.Column('is_read', sa.Boolean),
    sa.Column('is_approved', sa.Boolean)
)

def upgrade():
    op.add_column('bank_transactions',
                  sa.Column('is_read', sa.Boolean(), nullable=False,
                            server_default='false'))
    op.alter_column('bank_transactions', 'is_read', server_default=None)

    op.bulk_insert(bank_transaction_states, [
        {'identifier': 'approved'},
        {'identifier': 'denied'},
        {'identifier': 'from-mod'}
    ])

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.state == 'acknowledged')
        .values({'is_read': True})
    )

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.state != 'pending')
        .where(bank_transactions.c.is_approved)
        .values({'state': 'approved'})
    )

    op.execute(
        bank_transactions.update()
        .where(bank_transactions.c.state != 'pending')
        .where(~bank_transactions.c.is_approved)
        .values({'state': 'denied'})
    )        

    op.execute(
        bank_transaction_states.delete()
        .where(bank_transaction_states.c.identifier.in_(
            ['processed', 'acknowledged']
        ))
    )

    op.alter_column('bank_transactions', 'tcod_post_id', nullable=True)
    op.drop_column('bank_transactions', 'is_approved')


def downgrade():
    # eh
    assert False

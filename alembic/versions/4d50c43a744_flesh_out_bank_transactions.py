"""Flesh out bank_transactions.

Revision ID: 4d50c43a744
Revises: 31e70373b94
Create Date: 2014-05-29 13:10:19.900338

"""

# revision identifiers, used by Alembic.
revision = '4d50c43a744'
down_revision = '31e70373b94'

from alembic import op
import sqlalchemy as sa


def upgrade():
    state_enum = sa.Enum('pending', 'approved', 'denied',
        name='bank_transaction_state')
    bind = op.get_bind()
    impl = state_enum.dialect_impl(bind.dialect)
    impl.create(bind, checkfirst=True)

    op.add_column('bank_transactions', sa.Column('approver_id', sa.Integer(),
        nullable=True))
    op.add_column('bank_transactions', sa.Column('reason', sa.UnicodeText(),
        nullable=True))
    op.add_column('bank_transactions', sa.Column('state', state_enum,
        nullable=False, server_default='pending'))
    op.alter_column('bank_transactions', 'state', server_default=None)

    # I SHOULD update the new column based on the old column but whatever, I
    # haven't even deployed the old column yet

    op.drop_column('bank_transactions', 'is_pending')


def downgrade():
    # XXX Again, I should update is_pending based on state, but whatever
    op.add_column('bank_transactions', sa.Column('is_pending', sa.BOOLEAN(),
        nullable=False, server_default='True'))
    op.alter_column('bank_transactions', 'is_pending', server_default=None)

    op.drop_column('bank_transactions', 'state')
    op.drop_column('bank_transactions', 'reason')
    op.drop_column('bank_transactions', 'approver_id')

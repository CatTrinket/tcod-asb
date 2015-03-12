"""Add bank transaction dates and notes.

Revision ID: 46b1da464a3
Revises: 42172218251
Create Date: 2015-03-08 01:56:56.060485

"""

# revision identifiers, used by Alembic.
revision = '46b1da464a3'
down_revision = '42172218251'

from alembic import op
import sqlalchemy as sa

bank_transactions = sa.sql.table(
    'bank_transactions',
    sa.Column('id', sa.Integer),
    sa.Column('approver_id', sa.Integer),
    sa.Column('reason', sa.UnicodeText)
)

def upgrade():
    notes_seq = sa.Sequence('bank_transaction_notes_id_seq')
    op.execute(sa.schema.CreateSequence(notes_seq))

    bank_transaction_notes = op.create_table(
        'bank_transaction_notes',
        sa.Column('id', sa.Integer(), notes_seq, nullable=False),
        sa.Column('bank_transaction_id', sa.Integer(), nullable=False),
        sa.Column('trainer_id', sa.Integer(), nullable=True),
        sa.Column('note', sa.Unicode(length=200), nullable=False),
        sa.ForeignKeyConstraint(
            ['bank_transaction_id'], ['bank_transactions.id']
        ),
        sa.ForeignKeyConstraint(['trainer_id'], ['trainers.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.add_column(
        'bank_transactions',
        sa.Column('date', sa.Date(), nullable=True)
    )

    op.create_check_constraint(None, 'bank_transactions', 'amount > 0')

    # Turn reasons-for-denying into notes
    op.execute(
        bank_transaction_notes.insert()
        .from_select(
            ['id', 'bank_transaction_id', 'trainer_id', 'note'],
            sa.select([
                sa.func.next_value(notes_seq),
                bank_transactions.c.id,
                bank_transactions.c.approver_id,
                bank_transactions.c.reason
            ])
            .where(bank_transactions.c.reason.isnot(None))
        )
    )

    op.drop_column('bank_transactions', 'reason')


def downgrade():
    op.add_column('bank_transactions',
                  sa.Column('reason', sa.UnicodeText, nullable=True))
    op.drop_column('bank_transactions', 'date')
    op.drop_table('bank_transaction_notes')

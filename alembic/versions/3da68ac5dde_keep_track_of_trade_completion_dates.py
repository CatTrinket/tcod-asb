"""Keep track of trade completion dates.

Revision ID: 3da68ac5dde
Revises: 3a6f817195a
Create Date: 2015-12-25 15:05:01.412959

"""

# revision identifiers, used by Alembic.
revision = '3da68ac5dde'
down_revision = '3a6f817195a'

import datetime

from alembic import op
import sqlalchemy as sa

trades = sa.sql.table(
    'trades',
    sa.Column('completed', sa.Boolean),
    sa.Column('completed_date', sa.Date)
)

def upgrade():
    op.add_column('trades', sa.Column('completed_date', sa.Date,
                                      nullable=True))

    # get_bind() is basically the only way to use a date here
    op.get_bind().execute(
        trades.update()
        .where(trades.c.completed)
        .values({'completed_date': datetime.date(2015, 12, 25)})
    )

    op.drop_column('trades', 'completed')


def downgrade():
    op.add_column('trades', sa.Column('completed', sa.Boolean, nullable=False,
                                      serverdefault=False))
    op.alter_column('trades', 'completed', serverdefault=None)

    op.get_bind().execute(
        trades.update()
        .where(trades.c.completed_date.isnot(None))
        .values({'completed': True})
    )

    op.drop_column('trades', 'completed_date')

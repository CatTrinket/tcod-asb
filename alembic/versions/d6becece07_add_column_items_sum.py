"""Add column items.summary.

Revision ID: d6becece07
Revises: 7a31736914
Create Date: 2013-11-26 06:08:06.548055

"""

# revision identifiers, used by Alembic.
revision = 'd6becece07'
down_revision = '7a31736914'

from alembic import op
from sqlalchemy import Column, Unicode
from sqlalchemy.sql import table

def upgrade():
    items = table('items',
        Column('summary', Unicode)
    )

    op.add_column('items', Column('summary', Unicode))
    op.execute(items.update().values({'summary': op.inline_literal('')}))
    op.alter_column('items', 'summary', nullable=False)


def downgrade():
    op.drop_column('items', 'summary')

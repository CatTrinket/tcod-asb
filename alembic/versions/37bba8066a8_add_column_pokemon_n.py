"""add column pokemon.name

Revision ID: 37bba8066a8
Revises: None
Create Date: 2013-09-27 15:00:43.438652

"""

# revision identifiers, used by Alembic.
revision = '37bba8066a8'
down_revision = None

from alembic import op
from sqlalchemy import Column, Unicode
from sqlalchemy.sql import table

def upgrade():
    pokemon = table('pokemon',
        Column('name', Unicode)
    )

    op.add_column('pokemon', Column('name', Unicode))
    op.execute(pokemon.update().values({'name': op.inline_literal('')}))
    op.alter_column('pokemon', 'name', nullable=False)


def downgrade():
    op.drop_column('pokemon', 'name')

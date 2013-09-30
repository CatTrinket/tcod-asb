"""add identifiers to a bunch of tables

Revision ID: 5169f3861e1
Revises: 1acb40578ac
Create Date: 2013-09-29 11:03:32.652108

"""

# revision identifiers, used by Alembic.
revision = '5169f3861e1'
down_revision = '1acb40578ac'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import column, select, table

table_names = ['abilities', 'genders', 'items', 'pokemon', 'pokemon_forms',
    'pokemon_species', 'trainers']
tables = {name: table(name, column('id', sa.Integer), column('identifier',
    sa.Unicode)) for name in table_names}

def upgrade():
    # Add all the columns and just use IDs as placeholders
    for name, table in tables.items():
        op.add_column(name, sa.Column('identifier', sa.Unicode()))
        op.execute(table.update().values({'identifier': table.c.id}))
        op.alter_column(name, 'identifier', nullable=False)
        op.create_unique_constraint('{0}_identifier_key'.format(name), name,
            ['identifier'])


def downgrade():
    for name in table_names:
        op.drop_column(name, 'identifier')

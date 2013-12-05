"""Add column pokemon_forms.form_order

Revision ID: 46131a7d726
Revises: 63d30372be
Create Date: 2013-12-05 13:27:14.527232

"""

# revision identifiers, used by Alembic.
revision = '46131a7d726'
down_revision = '63d30372be'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table

def upgrade():
    pokemon_forms = table('pokemon_forms',
        sa.Column('form_order', sa.Integer)
    )

    op.add_column('pokemon_forms', sa.Column('form_order', sa.Integer()))
    op.execute(pokemon_forms.update().values({'form_order': op.inline_literal(1)}))
    op.alter_column('pokemon_forms', 'form_order', nullable=False)


def downgrade():
    op.drop_column('pokemon_forms', 'form_order')

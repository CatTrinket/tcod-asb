"""Stick length limits on trainer and Pokémon names.

Revision ID: 58e640283e
Revises: 2e2e77fd15a
Create Date: 2014-02-07 17:48:47.532572

"""

# revision identifiers, used by Alembic.
revision = '58e640283e'
down_revision = '2e2e77fd15a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('pokemon', 'name', type_=sa.Unicode(30), existing_type=sa.Unicode)
    op.alter_column('trainers', 'name', type_=sa.Unicode(30), existing_type=sa.Unicode)


def downgrade():
    op.alter_column('pokemon', 'name', type_=sa.Unicode, existing_type=sa.Unicode(30))
    op.alter_column('trainers', 'name', type_=sa.Unicode, existing_type=sa.Unicode(30))

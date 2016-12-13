"""Implement Meowstic as a plain old gender evolution

Revision ID: 2979c1ca783
Revises: 57c0a3ac533
Create Date: 2016-12-13 00:10:54.184351

"""

# revision identifiers, used by Alembic.
revision = '2979c1ca783'
down_revision = '57c0a3ac533'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('pokemon_form_conditions', 'gender_id')

def downgrade():
    assert False

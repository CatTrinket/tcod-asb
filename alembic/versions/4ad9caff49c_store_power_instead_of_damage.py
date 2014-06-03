"""Store power instead of damage.

Revision ID: 4ad9caff49c
Revises: 4d50c43a744
Create Date: 2014-06-02 22:28:52.839071

"""

# revision identifiers, used by Alembic.
revision = '4ad9caff49c'
down_revision = '4d50c43a744'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # I am lazy and this works fine
    op.alter_column('moves', 'damage', new_column_name='power')


def downgrade():
    op.alter_column('moves', 'power', new_column_name='damage')

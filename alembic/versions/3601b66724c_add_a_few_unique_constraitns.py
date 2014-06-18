"""Add a few unique constraitns.

Revision ID: 3601b66724c
Revises: 432cb17cfe5
Create Date: 2014-06-18 12:36:17.748584

"""

# revision identifiers, used by Alembic.
revision = '3601b66724c'
down_revision = '432cb17cfe5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_unique_constraint('trainers_tcodf_user_id_key',
        'trainers', ['tcodf_user_id'])
    op.create_unique_constraint('trainers_name_unclaimed_from_hack_key',
        'trainers', ['name', 'unclaimed_from_hack'])

def downgrade():
    op.drop_constraint('trainers_tcodf_user_id_key', 'trainers')
    op.drop_constraint('trainers_name_unclaimed_from_hack_key', 'trainers')

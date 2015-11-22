"""Add notes to effect text tables.

Revision ID: 31df6b83b3b
Revises: 4345928f238
Create Date: 2015-11-10 13:59:44.750904

"""

# revision identifiers, used by Alembic.
revision = '31df6b83b3b'
down_revision = '4345928f238'

from alembic import op
import sqlalchemy as sa


def upgrade():
    for table in ['ability_effects', 'item_effects', 'move_effects']:
        op.add_column(table, sa.Column('notes', sa.Unicode(), nullable=False,
                      server_default=''))
        op.alter_column(table, 'notes', server_default=None)

def downgrade():
    for table in ['ability_effects', 'item_effects', 'move_effects']:
        op.drop_column(table, 'notes')

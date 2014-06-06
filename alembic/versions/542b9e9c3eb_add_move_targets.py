"""Add move targets.

Revision ID: 542b9e9c3eb
Revises: 2ab6ad95083
Create Date: 2014-06-05 21:22:34.137853

"""

# revision identifiers, used by Alembic.
revision = '542b9e9c3eb'
down_revision = '2ab6ad95083'

from alembic import op
import sqlalchemy as sa

move_targets = sa.sql.table('move_targets',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode),
    sa.Column('name', sa.Unicode)
)

def upgrade():
    op.create_table('move_targets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier')
    )

    op.bulk_insert(move_targets, [{'id': 1, 'identifier': 'temp',
        'name': 'temp'}])

    op.add_column('moves', sa.Column('target_id', sa.Integer(), nullable=False,
        server_default='1'))
    op.alter_column('moves', 'target_id', server_default=None)


def downgrade():
    op.add_column('moves', sa.Column('target', sa.VARCHAR(), nullable=False,
        server_default=''))
    op.alter_column('moves', 'target', server_default=None)

    op.drop_column('moves', 'target_id')

    op.drop_table('move_targets')

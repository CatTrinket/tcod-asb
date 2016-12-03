"""Move moves' energy to the editable effect table.

Revision ID: 14f9e1aa963
Revises: 3da68ac5dde
Create Date: 2016-12-03 17:49:28.593500

"""

# revision identifiers, used by Alembic.
revision = '14f9e1aa963'
down_revision = '3da68ac5dde'

from alembic import op
import sqlalchemy as sa

moves = sa.sql.table(
    'moves',
    sa.Column('id', sa.Integer),
    sa.Column('energy', sa.Integer)
)

move_effects = sa.sql.table(
    'move_effects',
    sa.Column('move_id', sa.Integer),
    sa.Column('energy', sa.Integer)
)

def upgrade():
    op.add_column('move_effects', sa.Column('energy', sa.Integer,
                                            nullable=True))

    subquery = sa.select([moves.c.energy],
                         moves.c.id == move_effects.c.move_id)

    op.execute(move_effects.update().values({'energy': subquery}))

    op.drop_column('moves', 'energy')


def downgrade():
    # I'll implement this if I need it
    assert False

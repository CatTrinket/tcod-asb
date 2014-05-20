"""Make the Lax Incense go poof.

Revision ID: 507ba0d38e9
Revises: 145892d5dab
Create Date: 2014-05-20 10:44:33.211710

"""

# revision identifiers, used by Alembic.
revision = '507ba0d38e9'
down_revision = '145892d5dab'

from alembic import op
import sqlalchemy as sa

trainer_items = sa.sql.table('trainer_items',
    sa.Column('item_id', sa.Integer)
)

items = sa.sql.table('items',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode)
)

def upgrade():
    lax_incense = sa.sql.select([items.c.id]).where(
        items.c.identifier == 'lax-incense')
    bright_powder = sa.sql.select([items.c.id]).where(
        items.c.identifier == 'bright-powder')

    op.execute(
        trainer_items.update()
        .where(trainer_items.c.item_id == lax_incense)
        .values({'item_id': bright_powder})
    )

def downgrade():
    pass

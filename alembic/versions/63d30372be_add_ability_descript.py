"""Add ability descriptions.

Revision ID: 63d30372be
Revises: 1998b42d6de
Create Date: 2013-11-27 10:47:18.089668

"""

# revision identifiers, used by Alembic.
revision = '63d30372be'
down_revision = '1998b42d6de'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table

def upgrade():
    abilities = table ('abilities',
        sa.Column('summary', sa.Unicode),
        sa.Column('description', sa.Unicode)
    )

    op.add_column('abilities', sa.Column('description', sa.Unicode(), nullable=True))
    op.add_column('abilities', sa.Column('summary', sa.Unicode(), nullable=True))

    op.execute(abilities.update().values({'summary': op.inline_literal('')}))
    op.execute(abilities.update().values({'description': op.inline_literal('')}))

    op.alter_column('abilities', 'summary', nullable=False)
    op.alter_column('abilities', 'description', nullable=False)

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('abilities', 'summary')
    op.drop_column('abilities', 'description')
    ### end Alembic commands ###

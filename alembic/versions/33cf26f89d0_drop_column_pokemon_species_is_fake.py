"""Drop column pokemon_species.is_fake.

Revision ID: 33cf26f89d0
Revises: 55dfbe7be3c
Create Date: 2014-04-21 18:30:50.420453

"""

# revision identifiers, used by Alembic.
revision = '33cf26f89d0'
down_revision = '55dfbe7be3c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('pokemon_species', 'is_fake')


def downgrade():
    op.add_column('pokemon_species', sa.Column('is_fake', sa.BOOLEAN(),
        nullable=False, server_default=False))
    op.alter_column('pokemon_species', 'is_fake', server_default=None)

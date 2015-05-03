"""Drop pokemon_species_evolution.can_trade_instead.

Revision ID: 2505a3a8221
Revises: 19dcf1206de
Create Date: 2015-05-02 19:17:08.998514

"""

# revision identifiers, used by Alembic.
revision = '2505a3a8221'
down_revision = '19dcf1206de'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # We're not actually going to switch over to the Link Cable here; we'll
    # just let that happen when the db gets reloaded from the CSVs
    op.drop_column('pokemon_species_evolution', 'can_trade_instead')


def downgrade():
    op.add_column(
        'pokemon_species_evolution',
        sa.Column('can_trade_instead', sa.BOOLEAN(), autoincrement=False,
                  nullable=False, server_default=False)
    )
    op.alter_column('pokemon_species_evolution', 'can_trade_instead',
                    server_default=None)

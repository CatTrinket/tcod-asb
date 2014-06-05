"""Set pokemon.form_uncertain.

Revision ID: 2ab6ad95083
Revises: 14a3001fe10
Create Date: 2014-06-04 00:22:49.202752

"""

# revision identifiers, used by Alembic.
revision = '2ab6ad95083'
down_revision = '14a3001fe10'

from alembic import op
import sqlalchemy as sa

pokemon = sa.sql.table('pokemon',
    sa.Column('pokemon_form_id', sa.Integer),
    sa.Column('form_uncertain', sa.Boolean),
    sa.Column('is_in_squad', sa.Boolean)
)

def upgrade():
    op.execute(
        pokemon.update()
        # Unown, Wormadam, Shellos, Gastrodon, Basculin
        .where(pokemon.c.pokemon_form_id.in_([201, 413, 422, 423, 550]))
        .values({'form_uncertain': True, 'is_in_squad': False})
    )


def downgrade():
    pass

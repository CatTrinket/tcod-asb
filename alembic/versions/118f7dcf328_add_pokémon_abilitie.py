"""add Pokémon abilities

Revision ID: 118f7dcf328
Revises: c87221af6
Create Date: 2013-09-27 21:51:02.282502

"""

# revision identifiers, used by Alembic.
revision = '118f7dcf328'
down_revision = 'c87221af6'

from alembic import op
import sqlalchemy as sqla


def upgrade():
    # Add the column with a one-time default, and then ditch the default
    op.add_column('pokemon', sqla.Column('ability_slot', sqla.Integer(),
        nullable=False, server_default='1'))
    op.alter_column('pokemon', 'gender_id', server_default=None)

    # Set up the foreign key
    op.create_foreign_key('pokemon_ability_fkey',
        'pokemon', 'pokemon_form_abilities',
        ['pokemon_form_id', 'ability_slot'], ['pokemon_form_id', 'slot']
    )

def downgrade():
    op.drop_constraint('pokemon_ability_fkey', 'pokemon')
    op.drop_column('pokemon', 'ability_slot')

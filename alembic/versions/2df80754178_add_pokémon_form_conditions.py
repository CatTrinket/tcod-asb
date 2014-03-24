"""Add Pokémon form conditions.

Revision ID: 2df80754178
Revises: 2b5e1274c18
Create Date: 2014-03-24 13:10:04.734170

"""

# revision identifiers, used by Alembic.
revision = '2df80754178'
down_revision = '2b5e1274c18'

from alembic import op
import sqlalchemy as sa

pokemon_species = sa.sql.table('pokemon_species',
    sa.Column('form_carries_into_battle', sa.Boolean)
)

def upgrade():
    op.create_table('pokemon_form_conditions',
        sa.Column('pokemon_form_id', sa.Integer(),
            sa.ForeignKey('pokemon_forms.id'), primary_key=True,
            nullable=False),
        sa.Column('is_optional', sa.Boolean(), nullable=False),
        sa.Column('item_id', sa.Integer(), sa.ForeignKey('items.id'),
            nullable=True),
        sa.Column('gender_id', sa.Integer(), sa.ForeignKey('genders.id'),
            nullable=True),
        sa.Column('ability_id', sa.Integer(), sa.ForeignKey('abilities.id'),
            nullable=True),
    )

    op.add_column('pokemon_species', sa.Column('form_carries_into_battle',
        sa.Boolean(), nullable=True))
    op.execute(pokemon_species.update()
        .values({'form_carries_into_battle': op.inline_literal(False)}))
    op.alter_column('pokemon_species', 'form_carries_into_battle',
        nullable=False)


def downgrade():
    op.drop_column('pokemon_species', 'form_carries_into_battle')
    op.drop_table('pokemon_form_conditions')

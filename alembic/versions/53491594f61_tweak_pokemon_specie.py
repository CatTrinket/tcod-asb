"""tweak pokemon_species_evolution

Revision ID: 53491594f61
Revises: 47570d68099
Create Date: 2013-09-27 18:34:15.565359

"""

# revision identifiers, used by Alembic.
revision = '53491594f61'
down_revision = '47570d68099'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pokemon_species_evolution', sa.Column('buyable_price', sa.Integer(), nullable=True))
    op.drop_column('pokemon_species_evolution', 'is_buyable')
    op.alter_column('pokemon_species_evolution', 'gender', new_column_name='gender_id')


def downgrade():
    op.add_column('pokemon_species_evolution', sa.Column('is_buyable', sa.BOOLEAN(), nullable=False))
    op.drop_column('pokemon_species_evolution', 'buyable_price')
    op.alter_column('pokemon_species_evolution', 'gender_id', new_column_name='gender')

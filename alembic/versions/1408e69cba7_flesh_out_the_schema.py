"""flesh out the schema; still missing body/move mods

Revision ID: 1408e69cba7
Revises: 37bba8066a8
Create Date: 2013-09-27 16:30:36.636058

"""

# revision identifiers, used by Alembic.
revision = '1408e69cba7'
down_revision = '37bba8066a8'

from alembic import op
import sqlalchemy as sqla
from sqlalchemy.sql import table


def upgrade():
    # Create a zillion new tables
    op.create_table('items',
        sqla.Column('id', sqla.Integer(), nullable=False),
        sqla.Column('name', sqla.Unicode(), nullable=False),
        sqla.Column('description', sqla.Unicode(), nullable=False),
        sqla.PrimaryKeyConstraint('id')
    )

    op.create_table('genders',
        sqla.Column('id', sqla.Integer(), nullable=False),
        sqla.Column('name', sqla.Unicode(), nullable=False),
        sqla.PrimaryKeyConstraint('id')
    )

    op.create_table('abilities',
        sqla.Column('id', sqla.Integer(), nullable=False),
        sqla.Column('name', sqla.Unicode(), nullable=False),
        sqla.PrimaryKeyConstraint('id')
    )

    op.create_table('trainer_items',
        sqla.Column('id', sqla.Integer(), nullable=False),
        sqla.Column('trainer_id', sqla.Integer(), nullable=False),
        sqla.Column('item_id', sqla.Integer(), nullable=False),
        sqla.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sqla.ForeignKeyConstraint(['trainer_id'], ['trainers.id'], ),
        sqla.PrimaryKeyConstraint('id')
    )

    op.create_table('pokemon_species_evolution',
        sqla.Column('evolved_species_id', sqla.Integer(), nullable=False),
        sqla.Column('experience', sqla.Integer(), nullable=True),
        sqla.Column('happiness', sqla.Integer(), nullable=True),
        sqla.Column('item_id', sqla.Integer(), nullable=True),
        sqla.Column('gender', sqla.Integer(), nullable=True),
        sqla.Column('is_buyable', sqla.Boolean(), nullable=False),
        sqla.Column('can_trade_instead', sqla.Boolean(), nullable=False),
        sqla.ForeignKeyConstraint(['evolved_species_id'], ['pokemon_species.id'], ),
        sqla.ForeignKeyConstraint(['gender'], ['genders.id'], ),
        sqla.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sqla.PrimaryKeyConstraint('evolved_species_id')
    )

    op.create_table('pokemon_form_abilities',
        sqla.Column('pokemon_form_id', sqla.Integer(), nullable=False),
        sqla.Column('slot', sqla.Integer(), nullable=False),
        sqla.Column('ability_id', sqla.Integer(), nullable=False),
        sqla.Column('is_hidden', sqla.Boolean(), nullable=False),
        sqla.ForeignKeyConstraint(['ability_id'], ['abilities.id'], ),
        sqla.ForeignKeyConstraint(['pokemon_form_id'], ['pokemon_forms.id'], ),
        sqla.PrimaryKeyConstraint('pokemon_form_id', 'slot')
    )

    # Populate the gender table
    genders = table('genders',
        sqla.Column('id', sqla.Integer),
        sqla.Column('name', sqla.Unicode)
    )

    op.bulk_insert(genders, [
        {'name': 'female'},
        {'name': 'male'},
        {'name': 'genderless'}
    ])

    # Create new columns with arbitrary defaults since I only have dummy test data so far
    # ... But don't keep those defaults around
    op.add_column('pokemon', sqla.Column('can_evolve', sqla.Boolean(), nullable=False, server_default='False'))
    op.alter_column('pokemon', 'can_evolve', server_default=None)

    op.add_column('pokemon', sqla.Column('experience', sqla.Integer(), nullable=False, server_default='0'))
    op.alter_column('pokemon', 'experience', server_default=None)

    op.add_column('pokemon', sqla.Column('gender_id', sqla.Integer(), nullable=False, server_default='1'))
    op.alter_column('pokemon', 'gender_id', server_default=None)

    op.add_column('pokemon', sqla.Column('happiness', sqla.Integer(), nullable=False, server_default='0'))
    op.alter_column('pokemon', 'happiness', server_default=None)

    op.add_column('pokemon', sqla.Column('held_item_id', sqla.Integer(), nullable=True))
    op.alter_column('pokemon', 'held_item_id', server_default=None)

    op.add_column('pokemon', sqla.Column('is_in_squad', sqla.Boolean(), nullable=False, server_default='True'))
    op.alter_column('pokemon', 'is_in_squad', server_default=None)

    op.add_column('trainers', sqla.Column('can_collect_allowance', sqla.Boolean(), nullable=False, server_default='True'))
    op.alter_column('trainers', 'can_collect_allowance', server_default=None)

    op.add_column('trainers', sqla.Column('money', sqla.Integer(), nullable=False, server_default='0'))
    op.alter_column('trainers', 'money', server_default=None)

    op.add_column('trainers', sqla.Column('unclaimed_from_hack', sqla.Boolean(), nullable=False, server_default='False'))
    op.alter_column('trainers', 'unclaimed_from_hack', server_default=None)


def downgrade():
    # Drop new stuff
    op.drop_column('trainers', 'unclaimed_from_hack')
    op.drop_column('trainers', 'money')
    op.drop_column('trainers', 'can_collect_allowance')
    op.drop_column('pokemon', 'is_in_squad')
    op.drop_column('pokemon', 'held_item_id')
    op.drop_column('pokemon', 'happiness')
    op.drop_column('pokemon', 'gender_id')
    op.drop_column('pokemon', 'experience')
    op.drop_column('pokemon', 'can_evolve')
    op.drop_table('pokemon_form_abilities')
    op.drop_table('pokemon_species_evolution')
    op.drop_table('trainer_items')
    op.drop_table('abilities')
    op.drop_table('genders')
    op.drop_table('items')

"""Update move modifications table to not be all text.

Revision ID: 55c1351ecd
Revises: 19dcf1206de
Create Date: 2015-04-30 15:38:58.030194

"""

# revision identifiers, used by Alembic.
revision = '55c1351ecd'
down_revision = '19dcf1206de'

from alembic import op
import sqlalchemy as sa


def upgrade():
	# Add needs approval columns
    op.add_column('body_modifications',
    	sa.Column('needs_approval', sa.Boolean, nullable=False, default=True))
    op.add_column('move_modifications',
    	sa.Column('needs_approval', sa.Boolean, nullable=False, default=True))

    # Alter move modifications columns to not be all text
    op.alter_column('move_modifications', 'type',
    	new_column_name='type_id', type_=sa.Integer)
    op.create_foreign_key('move_modifications_type_id_fkey',
    	'move_modifications', 'types',
    	['type_id'], ['id'])

    op.alter_column('move_modifications', 'power', type_=sa.Integer)
    op.alter_column('move_modifications', 'energy', type_=sa.Integer)
    op.alter_column('move_modifications', 'accuracy', type_=sa.Integer)

    op.alter_column('move_modifications', 'target',
    	new_column_name='target_id', type_=sa.Integer)
    op.create_foreign_key('move_modifications_target_id_fkey',
    	'move_modifications', 'move_targets',
    	['target_id'], ['id]'])

    op.alter_column('move_modifications', 'stat',
    	new_column_name='damage_class_id', type_=sa.Integer)
    op.create_foreign_key('move_modifications_damage_class_id_fkey',
    	'move_modifications', 'damage_classes',
    	['damage_class_id'], ['id'])

    # Change flavour column name to description in modification tables
    op.alter_column('body_modifications', 'flavor',
    	new_column_name='description')
    op.alter_column('move_modifications', 'flavor',
    	new_column_name='description')


def downgrade():
	# Drop needs approval columns
	op.drop_column('body_modifications', 'needs_approval')
	op.drop_column('move_modifications', 'needs_approval')

	# Drop new foreign key constraints
	op.drop_constraint('move_modifications_type_id_fkey')
	op.drop_constraint('move_modifications_target_id_fkey')
	op.drop_constraint('move_modifications_damage_class_id_fkey')

	# Revert column names and types
	op.alter_column('move_modifications', 'type_id',
		new_column_name='type', type_=sa.Unicode)
	op.alter_column('move_modifications', 'target_id',
		new_column_name='target', type_=sa.Unicode)
	op.alter_column('move_modifications', 'damage_class_id',
		new_column_name='stat', type_=sa.Unicode)
	op.alter_column('move_modifications', 'power', type_=sa.Unicode)
    op.alter_column('move_modifications', 'energy', type_=sa.Unicode)
    op.alter_column('move_modifications', 'accuracy', type_=sa.Unicode)
    op.alter_column('body_modifications', 'description',
    	new_column_name='flavor')
    op.alter_column('move_modifications', 'description',
    	new_column_name='flavor')

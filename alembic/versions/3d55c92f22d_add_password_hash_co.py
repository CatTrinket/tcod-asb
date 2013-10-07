"""add password hash column; ON UPDATE CASCADE for foreign keys to trainer.id

Revision ID: 3d55c92f22d
Revises: 5169f3861e1
Create Date: 2013-10-03 19:11:32.149621

"""

# revision identifiers, used by Alembic.
revision = '3d55c92f22d'
down_revision = '5169f3861e1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('trainers', sa.Column('password_hash', sa.Unicode(), nullable=True))

    # You can't change constraints, apparently; just drop them and re-add them.

    # n.b. I haven't been naming my constraints so this is just what they've
    # been named by default.  I don't know whether these are SQLA defaults or
    # Postgres defaults.

    op.drop_constraint('pokemon_trainer_id_fkey', 'pokemon')
    op.drop_constraint('trainer_items_trainer_id_fkey', 'trainer_items')

    op.create_foreign_key('pokemon_trainer_id_fkey', 'pokemon', 'trainers',
        ['trainer_id'], ['id'], onupdate='cascade')
    op.create_foreign_key('trainer_items_trainer_id_fkey', 'trainer_items',
        'trainers', ['trainer_id'], ['id'], onupdate='cascade')


def downgrade():
    op.drop_column('trainers', 'password_hash')

    op.drop_constraint('pokemon_trainer_id_fkey', 'pokemon')
    op.drop_constraint('trainer_items_trainer_id_fkey', 'trainer_items')

    # Just let them acquire the default ON UPDATE behaviour again (I assume
    # it's restrict but whatever)
    op.create_foreign_key('pokemon_trainer_id_fkey', 'pokemon', 'trainers',
        ['trainer_id'], ['id'])
    op.create_foreign_key('trainer_items_trainer_id_fkey', 'trainer_items',
        'trainers', ['trainer_id'], ['id'])

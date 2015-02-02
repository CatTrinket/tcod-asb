"""Turn flavour text into player table stuff.

Revision ID: 304735420ea
Revises: 4326326a3c0
Create Date: 2015-02-02 12:06:25.029849

"""

# revision identifiers, used by Alembic.
revision = '304735420ea'
down_revision = '4326326a3c0'

from alembic import op
import sqlalchemy as sa

# Table stubs for moving flavour text back and forth
abilities = sa.sql.table(
    'abilities',
    sa.Column('id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode)
)

ability_effects = sa.sql.table(
    'ability_effects',
    sa.Column('ability_id', sa.Integer),
    sa.Column('edit_time', sa.DateTime),
    sa.Column('edited_by_trainer_id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode),
    sa.Column('is_current', sa.Boolean)
)
    

items = sa.sql.table(
    'items',
    sa.Column('id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode)
)

item_effects = sa.sql.table(
    'item_effects',
    sa.Column('item_id', sa.Integer),
    sa.Column('edit_time', sa.DateTime),
    sa.Column('edited_by_trainer_id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode),
    sa.Column('is_current', sa.Boolean)
)

moves = sa.sql.table(
    'moves',
    sa.Column('id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode)
)

move_effects = sa.sql.table(
    'move_effects',
    sa.Column('move_id', sa.Integer),
    sa.Column('edit_time', sa.DateTime),
    sa.Column('edited_by_trainer_id', sa.Integer),
    sa.Column('summary', sa.Unicode),
    sa.Column('description', sa.Unicode),
    sa.Column('is_current', sa.Boolean)
)

def upgrade():
    op.create_table('ability_effects',
        sa.Column('ability_id', sa.Integer(), nullable=False),
        sa.Column('edit_time', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('edited_by_trainer_id', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Unicode(), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False,
                  server_default=op.inline_literal(True)),
        sa.ForeignKeyConstraint(['ability_id'], ['abilities.id'], ),
        sa.ForeignKeyConstraint(['edited_by_trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('ability_id', 'edit_time')
    )

    op.create_table('item_effects',
        sa.Column('item_id', sa.Integer(), nullable=False),
        sa.Column('edited_by_trainer_id', sa.Integer(), nullable=True),
        sa.Column('edit_time', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('summary', sa.Unicode(), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False,
                  server_default=op.inline_literal(True)),
        sa.ForeignKeyConstraint(['edited_by_trainer_id'], ['trainers.id'], ),
        sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
        sa.PrimaryKeyConstraint('item_id', 'edit_time')
    )

    op.create_table('move_effects',
        sa.Column('move_id', sa.Integer(), nullable=False),
        sa.Column('edit_time', sa.DateTime(), nullable=False,
                  server_default=sa.func.now()),
        sa.Column('edited_by_trainer_id', sa.Integer(), nullable=True),
        sa.Column('summary', sa.Unicode(), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False,
                  server_default=op.inline_literal(True)),
        sa.ForeignKeyConstraint(['edited_by_trainer_id'], ['trainers.id'], ),
        sa.ForeignKeyConstraint(['move_id'], ['moves.id'], ),
        sa.PrimaryKeyConstraint('move_id', 'edit_time')
    )

    op.execute(
        ability_effects.insert()
        .from_select(
            ['ability_id', 'summary', 'description'],
            sa.select([abilities.c.id, abilities.c.summary,
                       abilities.c.description])
        )
    )

    op.execute(
        move_effects.insert()
        .from_select(
            ['move_id', 'summary', 'description'],
            sa.select([moves.c.id, moves.c.summary, moves.c.description])
        )
    )

    op.execute(
        item_effects.insert()
        .from_select(
            ['item_id', 'summary', 'description'],
            sa.select([items.c.id, items.c.summary, items.c.description])
        )
    )

    for table in ['ability_effects', 'item_effects', 'move_effects']:
        for column in ['edit_time', 'is_current']:
            op.alter_column(table, column, server_default=None)

    op.drop_column('abilities', 'summary')
    op.drop_column('abilities', 'description')
    op.drop_column('items', 'summary')
    op.drop_column('items', 'description')
    op.drop_column('moves', 'summary')
    op.drop_column('moves', 'description')


def downgrade():
    # Sorry but auuuugh
    assert False

    # op.add_column('moves', sa.Column('description', sa.Unicode, nullable=False))
    # op.add_column('moves', sa.Column('summary', sa.Unicode, nullable=False))
    # op.add_column('items', sa.Column('description', sa.Unicode, nullable=False))
    # op.add_column('items', sa.Column('summary', sa.Unicode, nullable=False))
    # op.add_column('abilities', sa.Column('description', sa.Unicode, nullable=False))
    # op.add_column('abilities', sa.Column('summary', sa.Unicode, nullable=False))
    # op.drop_table('move_effects')
    # op.drop_table('item_effects')
    # op.drop_table('ability_effects')

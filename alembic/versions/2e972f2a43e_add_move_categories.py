"""Add move categories.

Revision ID: 2e972f2a43e
Revises: 4e11dfe2c5f
Create Date: 2015-02-10 19:22:48.728119

"""

# revision identifiers, used by Alembic.
revision = '2e972f2a43e'
down_revision = '4e11dfe2c5f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('move_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('name')
    )

    op.create_table('move_category_map',
        sa.Column('move_category_id', sa.Integer(), nullable=False),
        sa.Column('move_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['move_category_id'], ['move_categories.id'], ),
        sa.ForeignKeyConstraint(['move_id'], ['moves.id'], ),
        sa.PrimaryKeyConstraint('move_category_id', 'move_id')
    )

    op.drop_column('moves', 'category')


def downgrade():
    op.add_column('moves', sa.Column('category', sa.Unicode, nullable=True))
    op.drop_table('move_category_map')
    op.drop_table('move_categories')

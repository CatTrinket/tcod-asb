"""Add contest stuff.

Revision ID: 2ce99f498f1
Revises: 2df1183d7
Create Date: 2014-07-07 13:38:23.277405

"""

# revision identifiers, used by Alembic.
revision = '2ce99f498f1'
down_revision = '2df1183d7'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('contest_supercategories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier')
    )

    op.create_table('contest_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.Column('name', sa.Unicode(), nullable=False),
        sa.Column('supercategory_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['supercategory_id'], ['contest_supercategories.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier'),
        sa.UniqueConstraint('identifier')
    )

    op.add_column('moves', sa.Column('appeal', sa.Integer(), nullable=True))
    op.add_column('moves', sa.Column('bonus_appeal', sa.Integer(), nullable=True))
    op.add_column('moves', sa.Column('jam', sa.Integer(), nullable=True))
    op.add_column('moves', sa.Column('bonus_jam', sa.Integer(), nullable=True))
    op.add_column('moves', sa.Column('contest_category_id', sa.Integer(),
        sa.ForeignKey('contest_categories.id'), nullable=True))


def downgrade():
    op.drop_column('moves', 'jam')
    op.drop_column('moves', 'contest_category_id')
    op.drop_column('moves', 'bonus_jam')
    op.drop_column('moves', 'bonus_appeal')
    op.drop_column('moves', 'appeal')
    op.drop_table('contest_categories')
    op.drop_table('contest_supercategories')

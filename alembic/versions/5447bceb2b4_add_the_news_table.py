"""Add the news table.

Revision ID: 5447bceb2b4
Revises: 2e6020f3486
Create Date: 2015-02-09 11:33:49.048095

"""

# revision identifiers, used by Alembic.
revision = '5447bceb2b4'
down_revision = '2e6020f3486'

from alembic import op
import sqlalchemy as sa

news_posts_id_seq = sa.Sequence('news_posts_id_seq')

def upgrade():
    op.execute(sa.schema.CreateSequence(news_posts_id_seq))

    op.create_table('news_posts',
        sa.Column('id', sa.Integer(), news_posts_id_seq, nullable=False),
        sa.Column('post_time', sa.DateTime(), nullable=False),
        sa.Column('posted_by_trainer_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('text', sa.Unicode(), nullable=False),
        sa.ForeignKeyConstraint(['posted_by_trainer_id'], ['trainers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('news_posts')
    op.execute(sa.schema.DropSequence(news_posts_id_seq))

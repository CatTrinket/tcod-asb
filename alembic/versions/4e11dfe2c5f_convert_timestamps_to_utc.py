"""Convert timestamps to UTC.

Revision ID: 4e11dfe2c5f
Revises: 5447bceb2b4
Create Date: 2015-02-10 10:55:50.613178

"""

# revision identifiers, used by Alembic.
revision = '4e11dfe2c5f'
down_revision = '5447bceb2b4'

import datetime

from alembic import op
import sqlalchemy as sa

utc_offset = (datetime.datetime.fromtimestamp(0) -
              datetime.datetime.utcfromtimestamp(0))

move_effects = sa.sql.table(
    'move_effects',
    sa.Column('edit_time', sa.DateTime)
)

item_effects = sa.sql.table(
    'item_effects',
    sa.Column('edit_time', sa.DateTime)
)

ability_effects = sa.sql.table(
    'ability_effects',
    sa.Column('edit_time', sa.DateTime)
)

news_posts = sa.sql.table(
    'news_posts',
    sa.Column('post_time', sa.DateTime)
)

def upgrade():
    # Subtract the UTC offset — for negative offsets this will still work as
    # expected (since subtracting -5 hours will add 5 hours)
    for table in [move_effects, item_effects, ability_effects]:
        op.execute(
            table.update()
            .values({'edit_time': table.c.edit_time - utc_offset})
        )

    op.execute(
        news_posts.update()
        .values({'post_time': news_posts.c.post_time - utc_offset})
    )

def downgrade():
    # Add the UTC offset back
    for table in [move_effects, item_effects, ability_effects]:
        op.execute(
            table.update()
            .values({'edit_time': table.c.edit_time + utc_offset})
        )

    op.execute(
        news_posts.update()
        .values({'post_time': news_posts.c.post_time + utc_offset})
    )

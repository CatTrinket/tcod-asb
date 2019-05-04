"""Add profile and markup format columns.

Revision ID: 1786e2e54f2
Revises: 2979c1ca783
Create Date: 2018-04-25 15:50:21.470469

"""

# revision identifiers, used by Alembic.
revision = '1786e2e54f2'
down_revision = '2979c1ca783'

import enum

from alembic import op
import sqlalchemy as sa


class MarkupLanguage(enum.Enum):
    bbcode = 'BBCode'
    markdown = 'Markdown'
    plain_text = 'Plain text'

markup_type = sa.Enum(MarkupLanguage, name='markup_language')


def upgrade():
    markup_type.create(op.get_bind())

    op.add_column('news_posts', sa.Column(
        'format', markup_type, nullable=False,
        server_default=MarkupLanguage.markdown.name))
    op.alter_column('news_posts', 'format', server_default=None)

    op.add_column('trainers', sa.Column(
        'last_markup_format', markup_type, nullable=False,
        server_default=MarkupLanguage.bbcode.name))
    op.alter_column('trainers', 'last_markup_format', server_default=None)

    op.add_column('trainers', sa.Column('profile_format', markup_type))
    op.add_column('trainers', sa.Column('profile', sa.Unicode(65535)))
    op.add_column('pokemon', sa.Column('profile_format', markup_type))
    op.add_column('pokemon', sa.Column('profile', sa.Unicode(65535)))

    # Add length limit
    op.alter_column('news_posts', 'text', type_=sa.Unicode(65535))

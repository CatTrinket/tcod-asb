"""Add identifiers to news posts.

Revision ID: 42172218251
Revises: 2e972f2a43e
Create Date: 2015-02-23 15:51:20.342795

"""

# revision identifiers, used by Alembic.
revision = '42172218251'
down_revision = '2e972f2a43e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

import asb.db as db

Base = declarative_base()

class NewsPost(Base):
    """A trimmed-down version of the current news posts table."""

    __tablename__ = 'news_posts'

    id = sa.Column(sa.Integer, primary_key=True)
    identifier = sa.Column(sa.Unicode, unique=True, nullable=False)
    title = sa.Column(sa.Unicode, nullable=False)

    def set_identifier(self):
        """Set an identifier based on ID and title."""

        self.identifier = db.helpers.identifier(self.title, id=self.id)

def upgrade():
    # Add the identifier column
    op.add_column('news_posts', sa.Column('identifier', sa.Unicode(),
                                          nullable=True))

    # Set all the identifiers
    connection = op.get_bind()
    db.DBSession.configure(bind=connection)
    Base.metadata.bind = connection
    news = db.DBSession.query(NewsPost).all()

    for post in news:
        post.set_identifier()

    db.DBSession.flush()

    # Add constraints
    op.alter_column('news_posts', 'identifier', nullable=False)
    op.create_unique_constraint(None, 'news_posts', ['identifier'])


def downgrade():
    op.drop_column('news_posts', 'identifier')

"""Add type matchup tables.

Revision ID: 2e6020f3486
Revises: 304735420ea
Create Date: 2015-02-08 11:13:02.758357

"""

# revision identifiers, used by Alembic.
revision = '2e6020f3486'
down_revision = '304735420ea'

from alembic import op
import sqlalchemy as sa

types = sa.sql.table(
    'types',
    sa.Column('id', sa.Integer)
)

type_matchups = sa.sql.table(
    'type_matchups',
    sa.Column('attacking_type_id', sa.Integer),
    sa.Column('defending_type_id', sa.Integer),
    sa.Column('result_id', sa.Integer)
)

type_matchup_results = sa.sql.table(
    'type_matchup_results',
    sa.Column('id', sa.Integer),
    sa.Column('identifier', sa.Unicode)
)

def upgrade():
    op.create_table('type_matchup_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('identifier', sa.Unicode(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('identifier')
    )

    op.create_table('type_matchups',
        sa.Column('attacking_type_id', sa.Integer(), nullable=False),
        sa.Column('defending_type_id', sa.Integer(), nullable=False),
        sa.Column('result_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['attacking_type_id'], ['types.id'], ),
        sa.ForeignKeyConstraint(['defending_type_id'], ['types.id'], ),
        sa.ForeignKeyConstraint(['result_id'], ['type_matchup_results.id'], ),
        sa.PrimaryKeyConstraint('attacking_type_id', 'defending_type_id')
    )

    # We should probably give these tables data, just in case future Alembic
    # scripts need it and we can't rely on the CSVs being reloaded in-between.
    # It doesn't have to be the *right* data.
    op.bulk_insert(type_matchup_results, [
        {'id': 1, 'identifier': 'ineffective'},
        {'id': 2, 'identifier': 'not-very-effective'},
        {'id': 3, 'identifier': 'neutral'},
        {'id': 4, 'identifier': 'super-effective'}
    ])

    attacking_type = types
    defending_type = types.alias()

    op.execute(
        type_matchups.insert()
        .from_select(
            ['attacking_type_id', 'defending_type_id', 'result_id'],
            sa.select([attacking_type.c.id, defending_type.c.id, 3])
        )
    )

def downgrade():
    op.drop_table('type_matchups')
    op.drop_table('type_matchup_results')

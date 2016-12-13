"""Allow separate evolution methods by form

Revision ID: 57c0a3ac533
Revises: 14f9e1aa963
Create Date: 2016-12-12 15:35:17.905511

"""

# revision identifiers, used by Alembic.
revision = '57c0a3ac533'
down_revision = '14f9e1aa963'

from alembic import op
import sqlalchemy as sa

pokemon_forms = sa.sql.table(
    'pokemon_forms',
    sa.Column('id', sa.Integer),
    sa.Column('species_id', sa.Integer),
    sa.Column('is_default', sa.Boolean)
)

evolution_methods = sa.sql.table(
    'evolution_methods',
    sa.Column('evolved_species_id', sa.Integer),
    sa.Column('evolved_form_id', sa.Integer)
)

def upgrade():
    # n.b. all this does is move the current methods from the species to the
    # default form; I'm just gonna add ones for alternate forms manually and
    # let the CSV reload take care of that

    op.rename_table('pokemon_species_evolution', 'evolution_methods')

    op.add_column(
        'evolution_methods',
        sa.Column('evolved_form_id', sa.Integer,
                  sa.ForeignKey('pokemon_forms.id'))
    )

    subquery = sa.select(
        [pokemon_forms.c.id],
        sa.and_(
            pokemon_forms.c.species_id ==
                evolution_methods.c.evolved_species_id,
            pokemon_forms.c.is_default
        )
    )

    op.execute(evolution_methods.update()
               .values({'evolved_form_id': subquery}))

    op.drop_column('evolution_methods', 'evolved_species_id')
    op.alter_column('evolution_methods', 'evolved_form_id', nullable=False)
    op.create_primary_key(None, 'evolution_methods', ['evolved_form_id'])

def downgrade():
    assert False

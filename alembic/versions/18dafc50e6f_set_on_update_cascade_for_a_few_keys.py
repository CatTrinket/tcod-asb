"""Set ON UPDATE CASCADE for a few keys.

Revision ID: 18dafc50e6f
Revises: 1157f40b292
Create Date: 2014-07-22 15:11:02.724364

"""

# revision identifiers, used by Alembic.
revision = '18dafc50e6f'
down_revision = '1157f40b292'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # bank_transactions.trainer_id
    op.drop_constraint(
        'bank_transactions_trainer_id_fkey',
        'bank_transactions'
    )

    op.create_foreign_key(
        'bank_transactions_trainer_id_fkey',
        'bank_transactions', 'trainers',
        ['trainer_id'], ['id'],
        onupdate='cascade'
    )

    # bank_transactions.approver_id
    op.drop_constraint(
        'bank_transactions_approver_id_fkey',
        'bank_transactions'
    )

    op.create_foreign_key(
        'bank_transactions_approver_id_fkey',
        'bank_transactions', 'trainers',
        ['approver_id'], ['id'],
        onupdate='cascade'
    )

    # promotion_recipients.trainer_id
    op.drop_constraint(
        'promotion_recipients_trainer_id_fkey',
        'promotion_recipients'
    )

    op.create_foreign_key(
        'promotion_recipients_trainer_id_fkey',
        'promotion_recipients', 'trainers',
        ['trainer_id'], ['id'],
        onupdate='cascade'
    )

    # pokemon_unlocked_evolutions.pokemon_id
    op.drop_constraint(
        'pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions'
    )

    op.create_foreign_key(
        'pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions', 'pokemon',
        ['pokemon_id'], ['id'],
        onupdate='cascade'
    )

def downgrade():
    # bank_transactions.trainer_id
    op.drop_constraint(
        'bank_transactions_trainer_id_fkey',
        'bank_transactions'
    )

    op.create_foreign_key(
        'bank_transactions_trainer_id_fkey',
        'bank_transactions', 'trainers',
        ['trainer_id'], ['id']
    )

    # bank_transactions.approver_id
    op.drop_constraint(
        'bank_transactions_approver_id_fkey',
        'bank_transactions'
    )

    op.create_foreign_key(
        'bank_transactions_approver_id_fkey',
        'bank_transactions', 'trainers',
        ['approver_id'], ['id']
    )

    # promotion_recipients.trainer_id
    op.drop_constraint(
        'promotion_recipients_trainer_id_fkey',
        'promotion_recipients'
    )

    op.create_foreign_key(
        'promotion_recipients_trainer_id_fkey',
        'promotion_recipients', 'trainers',
        ['trainer_id'], ['id']
    )

    # pokemon_unlocked_evolutions.pokemon_id
    op.drop_constraint(
        'pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions'
    )

    op.create_foreign_key(
        'pokemon_unlocked_evolutions_pokemon_id_fkey',
        'pokemon_unlocked_evolutions', 'pokemon',
        ['pokemon_id'], ['id'],
        ondelete='cascade'  # [sic]
    )

import sys

from pyramid.paster import get_appsettings
from sqlalchemy import engine_from_config
import transaction

import asb.models as models

# table, needs_id
# XXX Make this happen automatically
identifier_tables = [
    (models.Pokemon, True),
    (models.Trainer, True),
    (models.PokemonSpecies, False),
    (models.PokemonForm, False),
    (models.Gender, False),
    (models.Ability, False),
    (models.Item, False)
]

def set_identifiers(table, use_id=False):
    """Set the identifier for each row in the given table."""

    rows = models.DBSession.query(table).all()

    print(table.__tablename__)
    print('=' * len(table.__tablename__))

    for row in rows:
        row.identifier = models.identifier(row.name,
            id=row.id if use_id else None)
        print('{0:30} {1}'.format(row.name, row.identifier))

    print()


def main(argv=sys.argv):
    """Figure things out when called from the command line."""

    if len(argv) != 2:
        print('usage: {0} config_uri'.format(argv[0]))
        exit(1)

    settings = get_appsettings(argv[1])
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)

    for table, needs_id in identifier_tables:
        set_identifiers(table, use_id=needs_id)

    transaction.commit()

if __name__ == '__main__':
    main()

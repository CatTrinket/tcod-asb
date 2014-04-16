"""A command-line interface for managing the ASB database.

This file is not intended to be run directly.  It is specified as a separate
entry point in setup.py and should be installed as asbdb.
"""

import argparse
import csv
import os

import alembic.command
import alembic.config
import pkg_resources
import pyramid.paster
import sqlalchemy as sqla

import asb.db

def command_dump(connection, alembic_config):
    """Update the CSVs from the contents of the database.

    alembic_config is unused; it's only there so that all the command methods
    take the same arguments.
    """

    csv_dir = pkg_resources.resource_filename('asb', 'db/data')

    # Dump all the tables, with each table sorted by its primary key
    print('Dumping tables...')
    for table in asb.db.PokedexTable.metadata.tables.values():
        print('  - {0}...'.format(table.name))

        headers = [column.name for column in table.columns]
        primary_key = table.primary_key.columns
        rows = asb.db.DBSession.query(table).order_by(*primary_key).all()

        # You're not supposed to use os.path with resource paths, but this
        # command only makes sense if you're dumping into an actual directory
        csv_path = os.path.join(csv_dir, '{0}.csv'.format(table.name))

        with open(csv_path, 'w', encoding='UTF-8', newline='') as table_csv:
            writer = csv.writer(table_csv, lineterminator='\n')
            writer.writerow(headers)
            writer.writerows(rows)

def command_init(connection, alembic_config):
    """Create the database from scratch and load Pokédex tables."""

    # Create all the tables
    print('Creating tables...')
    asb.db.PokedexTable.metadata.create_all(connection)
    asb.db.PlayerTable.metadata.create_all(connection)

    # Stamp it with alembic
    print('Stamping database with alembic...')
    alembic.command.stamp(alembic_config, 'head')

    # Load all the Pokédex tables
    print('Loading Pokedex tables...')

    for table in asb.db.PokedexTable.metadata.sorted_tables:
        print('  - {0}...'.format(table.name))
        load_table(table, connection)

def command_update(connection, alembic_config):
    """Update the database by running alembic migrations and then reloading all
    the Pokédex tables from the CSVs.
    """

    # Run alembic migrations
    print('Running schema migrations...')
    alembic.command.upgrade(alembic_config, 'head')

    # Get the contents of the player tables so we can put them back after
    print('Stashing player tables...')
    player_table_contents = {}
    player_table_sequences = {}

    for table in asb.db.PlayerTable.metadata.tables.values():
        columns = [column.name for column in table.columns]
        player_table_contents[table.name] = [dict(zip(columns, row)) for row in
            asb.db.DBSession.query(table).all()]

        # Stash sequences, too, if we're using Postgres
        if connection.dialect.name == 'postgresql':
            for column in table.columns:
                if column.default is not None and column.default.is_sequence:
                    player_table_sequences[column.default.name] = (
                        connection.execute(column.default))

    # Close the connection so we can drop tables
    asb.db.DBSession.close()

    # Tear down and rebuild the entire schema
    print('Dropping player tables...')
    asb.db.PlayerTable.metadata.drop_all(connection)
    print('Dropping Pokedex tables...')
    asb.db.PokedexTable.metadata.drop_all(connection)
    print('Recreating Pokedex tables...')
    asb.db.PokedexTable.metadata.create_all(connection)
    print('Recreating player tables...')
    asb.db.PlayerTable.metadata.create_all(connection)

    # Reload all the tables
    print('Reloading Pokedex tables...')
    for table in asb.db.PokedexTable.metadata.sorted_tables:
        print('  - {0}...'.format(table.name))
        load_table(table, connection)

    print('Reloading player tables...')
    for table in asb.db.PlayerTable.metadata.sorted_tables:
        print('  - {0}...'.format(table.name))

        # An empty list is assumed to be a single row with no values so we need
        # to only insert if there's anything to insert
        contents = player_table_contents[table.name]
        if contents:
            connection.execute(table.insert(), contents)

    # Reset sequences (the dict will be empty if we're not on Postgres)
    for sequence_name, value in player_table_sequences.items():
        # - 1 because setval adds one, and we don't want that
        connection.execute(sqla.func.setval(sequence_name, value - 1))

def get_alembic_config(config_path, echo):
    """Create and return an alembic config."""

    config = alembic.config.Config(config_path)

    # Set logging based on the --sql flag
    config.set_main_option('asb_do_logging', str(echo))

    return config

def get_engine(config_path, echo):
    """Create and return an SQLA engine."""

    settings = pyramid.paster.get_appsettings(config_path)
    engine = sqla.engine_from_config(settings, 'sqlalchemy.', echo=echo)
    asb.db.DBSession.configure(bind=engine)
    return engine

def get_parser():
    """Create and return a parser for the command-line arguments."""

    # Global stuff
    parser = argparse.ArgumentParser(description='Manage the ASB database.')
    parser.add_argument('-s', '--sql', action='store_true',
        help='Echo all SQL performed.')
    parser.add_argument('config',
        help='The path to the configuration .ini to use.')
    subparsers = parser.add_subparsers(title='commands')

    # init command
    init_parser = subparsers.add_parser('init',
        help='Create the database from scratch.')
    init_parser.set_defaults(func=command_init)

    # update command
    reload_parser = subparsers.add_parser('update',
        help='Update an existing database.')
    reload_parser.set_defaults(func=command_update)

    # dump command
    dump_parser = subparsers.add_parser('dump',
        help='Update the data CSVs from the contents of the database.')
    dump_parser.set_defaults(func=command_dump)

    return parser

def load_table(table, connection):
    """Load data into an empty table from a CSV."""

    filename = pkg_resources.resource_filename('asb',
        'db/data/{0}.csv'.format(table.name))

    # Read the table's CSV into a list of dicts, because that's what it needs
    # to be for an SQLA Core bulk insert
    with open(filename, encoding='UTF-8', newline='') as table_csv:
        reader = csv.DictReader(table_csv)
        rows = []

        for row in reader:
            # Translate certain values that SQLA doesn't get right on its own
            for column_name, value in row.items():
                column = table.c[column_name]

                if value == '' and column.nullable:
                    row[column_name] = None
                elif isinstance(column.type, sqla.types.Boolean):
                    if value == 'True':
                        row[column_name] = True
                    elif value == 'False':
                        row[column_name] = False

            rows.append(row)

    # pokemon_species has a self-referencing key — evolves_from_species_id — so
    # its rows have to be inserted in the right order.  Instead of actually
    # figuring it out, we can just sort by the order column.
    # XXX Do this right someday
    if table.name == 'pokemon_species':
        rows.sort(key=lambda row: row['order'])

    # Insert everything
    connection.execute(table.insert(), rows)

def main(argv=None):
    """Parse arguments and run the appropriate command."""

    parser = get_parser()
    args = parser.parse_args(argv)
    engine = get_engine(args.config, args.sql)
    alembic_config = get_alembic_config(args.config, args.sql)

    with engine.begin() as connection:
        args.func(connection, alembic_config)

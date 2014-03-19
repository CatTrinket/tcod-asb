Setting up for development
==========================

First off, you'll pretty much *need* to use a virtualenv, since all the package
requirements are given as exact versions.

Also, by default, this thing uses an SQLite db in this directory.  If you're
going to be using something else, change the "sqlalchemy.url" line in
development.ini and alembic.ini.

Anyway:

- python setup.py develop
- initialize_asb_db development.ini
- alembic stamp head
- Load all the data from the CSVs in asb/data/.  There's no actual system for
  this (yet) so you're kind of on your own here, eheheh.
- pserve development.ini


Updating
========

- python setup.py egg_info
- alembic upgrade head
- Reload from CSVs if any of them have changed (sorry)

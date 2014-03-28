Setting up for development
==========================

First off, you'll pretty much *need* to use a virtualenv, since all the package
requirements are given as exact versions.

Also, by default, this thing uses an SQLite db in this directory.  If you're
going to be using something else, change the "sqlalchemy.url" line in
development.ini and alembic.ini.

Anyway:

- python setup.py develop
- asbdb development.ini init
- pserve development.ini


Updating
========

- python setup.py egg_info
- asbdb development.ini update

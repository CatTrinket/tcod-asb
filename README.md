The Cave of Dragonflies ASB
===========================

Setting up for development
--------------------------

Before we begin, make sure you set up your virtualenv with `virtualenv
--python=python3 --setuptools asb-env`.  (And yes, using a virtualenv is more
or less mandatory — `setup.py` specifies exact versions of everything that are
likely to conflict with anything else.)

Also, if you want to use something other than SQLite for the database, make a
copy of `development.ini` and change the `sqlalchemy.url` line accordingly.  If
you're using Postgres, you'll have to `pip install psycopg2`, too.

Anyway, from this directory:

    pip install --editable .
    asbdb development.ini init
    pserve --reload development.ini


Updating
--------

    pip install --upgrade --editable .
    asbdb development.ini update

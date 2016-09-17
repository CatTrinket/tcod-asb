The Cave of Dragonflies ASB
===========================

Setting up for development
--------------------------

First of all, set up a Python 3 virtualenv.  (Using a virtualenv is more or
less mandatory — `setup.py` specifies exact versions of everything that will
probably conflict with anything else.)

Also, if you want to use something other than SQLite for the database, make a
copy of `development.ini` and change the `sqlalchemy.url` line accordingly.

Anyway, from this directory:

    pip install --editable .
    asbdb development.ini init
    pserve --reload development.ini


Updating
--------

    pip install --upgrade --editable .
    asbdb development.ini update


Optional packages
-----------------

Other potentially-useful packages to `pip install` (i.e. everything that's not
in `setup.py` but that I use in production):

- `gunicorn`, for Serious Deployment instead of `pserve`
- `psycopg2`, if you're using Postgres
- `pycrypto`, if you want to use cookie-only sessions

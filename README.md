The Cave of Dragonflies ASB
===========================

Setting up for development
--------------------------

Before we begin, make sure you set up your virtualenv with `virtualenv
--python=python3 --setuptools asb-env`.  (And yes, using a virtualenv is more
or less mandatory — `setup.py` specifies exact versions of everything that are
likely to conflict with anything else.)

Anyway, from this directory:

    pip install --editable .
    asbdb development.ini init
    pserve --reload development.ini


Updating
--------

    pip install --upgrade --editable .
    asbdb development.ini update

"""Temporary thing because I just want to figure out db shit"""

from sys import argv
import sqlalchemy as sqla
import asb.db.tables as tables

# do this part from this directory

if 'create' in argv:
    engine = sqla.create_engine('postgresql://@/asb_test', echo=True)
    tables.TableBase.metadata.create_all(engine)


from alembic.config import Config
from alembic import command

# do this part from the alembic.ini directory.....

if 'alembic' in argv:
    alembic_cfg = Config('alembic.ini')
    command.stamp(alembic_cfg, 'head')

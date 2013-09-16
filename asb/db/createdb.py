"""Temporary thing because I just want to figure out db shit"""

import sqlalchemy as sqla
import tables

engine = sqla.create_engine('postgresql://@/asb_test', echo=True)
tables.TableBase.metadata.create_all(engine)

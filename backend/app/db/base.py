"""The base class every database model inherits from.

SQLAlchemy collects all classes that inherit from Base into Base.metadata.
Alembic reads that metadata to work out which tables to create or change.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Predictable names for indexes and constraints, e.g. "uq_users_email".
# Without this, Postgres invents names, and a later migration that needs to
# drop or rename a constraint can't know what it is called.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

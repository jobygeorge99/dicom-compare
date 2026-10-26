"""The base class every database model inherits from.

SQLAlchemy collects all classes that inherit from Base into Base.metadata.
Alembic (our migration tool, coming next) reads that metadata to work out
which tables to create or change.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

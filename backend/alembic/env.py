"""Alembic runs this file for every command (revision, upgrade, downgrade...).

Its job: tell Alembic (1) which database to connect to and (2) what the
models look like, so `--autogenerate` can compare the two and write the
difference as a migration.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app.core.config import get_settings
from app.db import models  # noqa: F401  (importing registers the tables on Base.metadata)
from app.db.base import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)  # logging setup from alembic.ini

target_metadata = Base.metadata  # "what the database SHOULD look like"
database_url = get_settings().database_url  # same source as the app itself


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: print the SQL instead of running it.

    Useful when a DBA must review changes before they hit production.
    """
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """The normal mode: connect and apply migrations."""
    engine = create_engine(database_url, poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # also detect column TYPE changes, not just new/removed columns
        )
        # All-or-nothing: a failed migration leaves no half-applied change.
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

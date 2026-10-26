"""Database connection setup.

- engine: holds a pool of connections to Postgres. Created once per process.
- SessionLocal: a factory that hands out Sessions. A Session is one
  "unit of work": you load/change objects, then commit or roll back.
- get_db: a FastAPI dependency that gives each request its own Session and
  always closes it afterwards, even if the request crashes.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,  # check a pooled connection is alive before using it
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db  # the route runs here, using `db`
    finally:
        db.close()  # runs after the response, success or error

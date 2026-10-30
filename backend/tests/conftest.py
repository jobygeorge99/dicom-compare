"""Shared test fixtures. pytest loads conftest.py automatically.

A FIXTURE is setup code a test asks for by naming it as a parameter:
    def test_x(client, make_user): ...
pytest builds those objects first and cleans up after.

Database strategy:
- A separate database (dicom_compare_test) on the same Docker Postgres, so
  tests can never touch your dev data. It is created automatically.
- Each test runs inside a transaction that is ROLLED BACK at the end, so
  every test starts with empty tables and tests can't affect each other.
"""

from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.models import Role, User
from app.db.session import get_db
from app.main import app

TEST_PASSWORD = "correct-horse-battery-staple"


@pytest.fixture(scope="session")  # once per test run, not once per test
def db_engine() -> Iterator[Engine]:
    dev_url = make_url(get_settings().database_url)
    test_url = dev_url.set(database=f"{dev_url.database}_test")

    # CREATE DATABASE can't run inside a transaction, hence AUTOCOMMIT.
    server = create_engine(dev_url, isolation_level="AUTOCOMMIT")
    with server.connect() as conn:
        exists = conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": test_url.database},
        )
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    server.dispose()

    engine = create_engine(test_url)
    # Fresh tables from the models on every run.
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(db_engine: Engine) -> Iterator[Session]:
    connection = db_engine.connect()
    outer = connection.begin()
    # "create_savepoint": when app code calls commit(), it only commits a
    # savepoint inside our outer transaction, which we still roll back.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    outer.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    # Point the app's get_db at the test session for the length of one test.
    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(db_session: Session) -> Callable[..., User]:
    """A small factory: make_user(role=Role.ADMIN) creates and returns a user."""

    def _make_user(
        email: str = "analyst@example.com",
        password: str = TEST_PASSWORD,
        role: Role = Role.ANALYST,
        is_active: bool = True,
    ) -> User:
        user = User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
        db_session.add(user)
        db_session.flush()  # send the INSERT so the user gets an id
        return user

    return _make_user

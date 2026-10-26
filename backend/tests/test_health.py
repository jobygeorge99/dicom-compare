"""Our first tests.

TestClient calls the app in-process: no server, no network, very fast.
The readiness test shows a key technique: dependency overrides. We replace
the real database with a fake, so tests don't need Postgres running.
"""

from collections.abc import Iterator
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db.session import get_db
from app.main import app

client = TestClient(app)


def test_liveness_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_503_when_db_is_down() -> None:
    broken_db = MagicMock()
    broken_db.execute.side_effect = OperationalError("SELECT 1", {}, Exception("no db"))

    def fake_get_db() -> Iterator[MagicMock]:
        yield broken_db

    app.dependency_overrides[get_db] = fake_get_db
    try:
        response = client.get("/health/ready")
    finally:
        app.dependency_overrides.clear()  # don't leak the fake into other tests

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}

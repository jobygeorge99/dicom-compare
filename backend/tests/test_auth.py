"""API tests for login and GET /users/me.

These go through the real HTTP layer and a real (test) database, so they
check that every piece fits together. Needs Postgres running (docker compose up -d).
"""

from collections.abc import Callable

from fastapi.testclient import TestClient

from app.db.models import Role, User
from tests.conftest import TEST_PASSWORD

LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/users/me"


def login(client: TestClient, email: str, password: str = TEST_PASSWORD) -> str:
    # OAuth2 login is a FORM post (data=...), not JSON.
    response = client.post(LOGIN_URL, data={"username": email, "password": password})
    assert response.status_code == 200, response.text
    token: str = response.json()["access_token"]
    return token


def test_login_then_read_me(client: TestClient, make_user: Callable[..., User]) -> None:
    make_user(email="ana@example.com", role=Role.ANALYST)

    token = login(client, "ana@example.com")
    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "ana@example.com"
    assert body["role"] == "analyst"
    assert "password_hash" not in body  # the schema must never leak it


def test_login_is_case_insensitive_for_email(
    client: TestClient, make_user: Callable[..., User]
) -> None:
    make_user(email="ana@example.com")

    login(client, "  Ana@Example.COM ")


def test_wrong_password_and_unknown_email_look_the_same(
    client: TestClient, make_user: Callable[..., User]
) -> None:
    make_user(email="ana@example.com")

    wrong_password = client.post(
        LOGIN_URL, data={"username": "ana@example.com", "password": "nope-nope-nope"}
    )
    unknown_email = client.post(
        LOGIN_URL, data={"username": "nobody@example.com", "password": TEST_PASSWORD}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_inactive_user_cannot_log_in(client: TestClient, make_user: Callable[..., User]) -> None:
    make_user(email="gone@example.com", is_active=False)

    response = client.post(
        LOGIN_URL, data={"username": "gone@example.com", "password": TEST_PASSWORD}
    )

    assert response.status_code == 401


def test_me_requires_a_token(client: TestClient) -> None:
    response = client.get(ME_URL)

    assert response.status_code == 401


def test_me_rejects_a_garbage_token(client: TestClient) -> None:
    response = client.get(ME_URL, headers={"Authorization": "Bearer not.a.token"})

    assert response.status_code == 401


def test_deactivated_user_loses_access_with_a_valid_token(
    client: TestClient, make_user: Callable[..., User]
) -> None:
    user = make_user(email="ana@example.com")
    token = login(client, "ana@example.com")

    user.is_active = False  # an admin deactivates them after they logged in

    response = client.get(ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

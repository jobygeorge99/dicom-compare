"""API tests for the admin user endpoints.

The pattern for access control tests: for EVERY protected endpoint, prove
the allowed role succeeds AND every other role is refused. Broken access
control is the top web vulnerability; these tests are how you avoid it.
"""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditAction, AuditLog, Role
from tests.conftest import LoginAs

USERS_URL = "/api/v1/admin/users"
NEW_USER = {
    "email": "Dr.Rao@Hospital.example.com",
    "password": "long-enough-password",
    "role": "analyst",
}


# --- Creating users -------------------------------------------------------------


def test_admin_can_create_a_user_who_can_then_log_in(client: TestClient, login_as: LoginAs) -> None:
    _, admin_headers = login_as(Role.ADMIN)

    response = client.post(USERS_URL, json=NEW_USER, headers=admin_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "dr.rao@hospital.example.com"  # stored lowercase
    assert body["role"] == "analyst"
    assert "password" not in body and "password_hash" not in body

    login = client.post(
        "/api/v1/auth/login",
        data={"username": NEW_USER["email"], "password": NEW_USER["password"]},
    )
    assert login.status_code == 200


def test_role_defaults_to_analyst(client: TestClient, login_as: LoginAs) -> None:
    _, admin_headers = login_as(Role.ADMIN)
    payload = {"email": "new@example.com", "password": "long-enough-password"}

    response = client.post(USERS_URL, json=payload, headers=admin_headers)

    assert response.json()["role"] == "analyst"


def test_analyst_and_viewer_are_forbidden(client: TestClient, login_as: LoginAs) -> None:
    for role in (Role.ANALYST, Role.VIEWER):
        _, headers = login_as(role)

        response = client.post(USERS_URL, json=NEW_USER, headers=headers)

        assert response.status_code == 403, role  # logged in, but not allowed


def test_anonymous_request_is_unauthorized(client: TestClient) -> None:
    response = client.post(USERS_URL, json=NEW_USER)

    assert response.status_code == 401  # not logged in at all


def test_duplicate_email_is_a_conflict(client: TestClient, login_as: LoginAs) -> None:
    _, admin_headers = login_as(Role.ADMIN)
    client.post(USERS_URL, json=NEW_USER, headers=admin_headers)

    again = client.post(USERS_URL, json=NEW_USER, headers=admin_headers)

    assert again.status_code == 409


def test_invalid_input_is_rejected(client: TestClient, login_as: LoginAs) -> None:
    _, admin_headers = login_as(Role.ADMIN)
    bad_inputs = [
        {**NEW_USER, "password": "short"},
        {**NEW_USER, "email": "not-an-email"},
        {**NEW_USER, "role": "superuser"},
    ]

    for payload in bad_inputs:
        response = client.post(USERS_URL, json=payload, headers=admin_headers)
        assert response.status_code == 422, payload  # 422 = failed validation


def test_creating_a_user_is_audited(
    client: TestClient, login_as: LoginAs, db_session: Session
) -> None:
    admin, admin_headers = login_as(Role.ADMIN)

    new_id = client.post(USERS_URL, json=NEW_USER, headers=admin_headers).json()["id"]

    entry = db_session.scalars(
        select(AuditLog).where(AuditLog.action == AuditAction.USER_CREATED)
    ).one()
    assert entry.actor_id == admin.id
    assert entry.target == f"user:{new_id}"


# --- Listing users ----------------------------------------------------------------


def test_admin_can_list_users(client: TestClient, login_as: LoginAs) -> None:
    _, admin_headers = login_as(Role.ADMIN)

    response = client.get(USERS_URL, headers=admin_headers)

    assert response.status_code == 200
    assert [u["email"] for u in response.json()] == ["admin@example.com"]


def test_analyst_cannot_list_users(client: TestClient, login_as: LoginAs) -> None:
    _, headers = login_as(Role.ANALYST)

    assert client.get(USERS_URL, headers=headers).status_code == 403

"""Unit tests for the role -> permission policy. No database, no HTTP.

These pin the policy down: if someone edits ROLE_PERMISSIONS by accident
(say, giving analysts users:create), a test fails in review.
"""

from app.core.permissions import ROLE_PERMISSIONS, Permission, has_permission
from app.db.models import Role


def test_every_role_has_a_policy() -> None:
    # Adding a new Role without deciding its permissions should fail loudly.
    assert set(ROLE_PERMISSIONS) == set(Role)


def test_admin_has_every_permission() -> None:
    assert all(has_permission(Role.ADMIN, p) for p in Permission)


def test_only_admin_can_manage_users() -> None:
    for role in (Role.ANALYST, Role.VIEWER):
        assert not has_permission(role, Permission.USERS_CREATE)
        assert not has_permission(role, Permission.USERS_READ)
        assert not has_permission(role, Permission.AUDIT_READ)


def test_analyst_can_run_comparisons_but_viewer_cannot() -> None:
    assert has_permission(Role.ANALYST, Permission.COMPARISONS_CREATE)
    assert not has_permission(Role.VIEWER, Permission.COMPARISONS_CREATE)

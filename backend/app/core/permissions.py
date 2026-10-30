"""Who may do what: roles map to permissions.

Routes never check roles directly ("is this an admin?"). They ask for a
PERMISSION ("can this user create users?"). To change what a role may do,
edit ROLE_PERMISSIONS below; no route code changes.

Permission names follow the common "resource:action" style.
"""

from enum import StrEnum

from app.db.models import Role


class Permission(StrEnum):
    USERS_CREATE = "users:create"
    USERS_READ = "users:read"
    AUDIT_READ = "audit:read"
    # Used from Phase 2, listed now so the whole policy is visible in one place.
    COMPARISONS_CREATE = "comparisons:create"
    COMPARISONS_READ_OWN = "comparisons:read_own"
    COMPARISONS_READ_SHARED = "comparisons:read_shared"
    COMPARISONS_READ_ALL = "comparisons:read_all"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),  # every permission
    Role.ANALYST: frozenset(
        {
            Permission.COMPARISONS_CREATE,
            Permission.COMPARISONS_READ_OWN,
        }
    ),
    Role.VIEWER: frozenset(
        {
            Permission.COMPARISONS_READ_SHARED,
        }
    ),
}


def has_permission(role: Role, permission: Permission) -> bool:
    # .get(..., empty) means an unknown role gets NOTHING: "deny by default".
    return permission in ROLE_PERMISSIONS.get(role, frozenset())

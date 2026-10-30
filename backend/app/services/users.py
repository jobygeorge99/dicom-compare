"""User management rules, shared by the admin API and the CLI script.

One implementation means one set of rules: an account made from the
terminal and one made through the API are guaranteed to be identical.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import AuditAction, Role, User
from app.services import audit
from app.services.auth import get_user_by_email, normalize_email

MIN_PASSWORD_LENGTH = 12


class EmailAlreadyRegisteredError(Exception):
    """Raised when creating a user whose email is taken.

    The service raises a plain Python error; the ROUTER decides it means
    HTTP 409. Services stay free of HTTP so the CLI can use them too.
    """


def create_user(
    db: Session,
    email: str,
    password: str,
    role: Role,
    created_by: User | None = None,
) -> User:
    """Create, audit and commit a new user. created_by is None for the CLI."""
    if get_user_by_email(db, email) is not None:
        raise EmailAlreadyRegisteredError(email)

    user = User(
        email=normalize_email(email),
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.flush()  # sends the INSERT so user.id exists for the audit entry

    audit.record(
        db,
        AuditAction.USER_CREATED,
        actor_id=created_by.id if created_by else None,
        target=f"user:{user.id}",
    )
    db.commit()  # user + audit entry saved together, or not at all
    return user


def list_users(db: Session) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)))

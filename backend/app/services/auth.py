"""Login logic.

The SERVICE layer holds business rules and knows nothing about HTTP: no
requests, no status codes. That keeps it easy to test and lets other
callers (a CLI script, the phase 4 agent) reuse it.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, password_needs_rehash, verify_password
from app.db.models import User

# Used when the email doesn't exist, so that case takes as long as a wrong
# password. Otherwise an attacker could time responses to learn which
# emails have accounts ("user enumeration").
_DUMMY_HASH = hash_password("dummy-password-used-only-for-timing")


def normalize_email(email: str) -> str:
    """Emails are case-insensitive in practice: store and compare lowercase."""
    return email.strip().lower()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == normalize_email(email)))


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """Return the user if the email and password are right and the account is active."""
    user = get_user_by_email(db, email)

    if user is None:
        verify_password(password, _DUMMY_HASH)  # burn the same time, then fail
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    # Hashing settings get stronger over time; upgrade old hashes quietly.
    if password_needs_rehash(user.password_hash):
        user.password_hash = hash_password(password)
        db.commit()

    return user

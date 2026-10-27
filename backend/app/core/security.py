"""Password hashing and JWT access tokens.

Kept in one small module with no web or database code, so it is easy to
read, easy to test, and the only place that touches secrets.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import get_settings

# --------------------------------------------------------------------------
# Passwords
# --------------------------------------------------------------------------

# Argon2id with the library's recommended settings. It is deliberately SLOW
# and memory-hungry, which makes guessing billions of passwords impractical.
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return a hash like '$argon2id$v=19$m=65536,t=3,p=4$<salt>$<hash>'."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """True if the password matches. Never raises for a wrong password."""
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def password_needs_rehash(password_hash: str) -> bool:
    """True if the hash used older/weaker settings. Re-hash at next login."""
    return _hasher.check_needs_rehash(password_hash)


# --------------------------------------------------------------------------
# JWT access tokens
# --------------------------------------------------------------------------


def create_access_token(
    subject: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed token saying "this user, with this role, until this time".

    subject: the user's id as a string (the standard JWT "sub" claim).
    """
    settings = get_settings()
    now = datetime.now(UTC)
    lifetime = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": subject,  # who
        "role": role,  # what they may do
        "iat": now,  # issued at
        "exp": now + lifetime,  # expires at; PyJWT rejects the token after this
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify the signature and expiry, then return the payload.

    Raises jwt.InvalidTokenError (or a subclass such as ExpiredSignatureError)
    if the token is forged, tampered with, malformed or expired.
    """
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],  # a fixed list: never trust the token's own "alg"
        options={"require": ["exp", "sub", "role"]},
    )

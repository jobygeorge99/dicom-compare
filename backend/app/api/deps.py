"""Reusable FastAPI dependencies.

A route asks for what it needs in its parameters (a DB session, the current
user) and FastAPI builds it. Auth rules live here once, not copied into
every route.
"""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.permissions import Permission, has_permission
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

# Reads the "Authorization: Bearer <token>" header. tokenUrl tells the
# /docs page where to send the username/password to get a token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DbSession,
) -> User:
    """Turn the token on the request back into a User, or reject with 401."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},  # required by the HTTP spec for 401
    )

    try:
        payload = decode_access_token(token)
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as exc:
        raise unauthorized from exc

    # Always re-load the user: if an admin deactivated them after the token
    # was issued, they lose access now, not when the token expires.
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(permission: Permission) -> Callable[[User], User]:
    """Build a dependency that lets the request through only with `permission`.

    Usage in a route:
        admin: Annotated[User, Depends(require_permission(Permission.USERS_CREATE))]

    It is a "factory": a function that returns a function. Each route passes
    the permission it needs and gets its own checker back.
    """

    def checker(current_user: CurrentUser) -> User:
        # Logged in (else get_current_user already raised 401), but allowed?
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to do this",
            )
        return current_user

    return checker

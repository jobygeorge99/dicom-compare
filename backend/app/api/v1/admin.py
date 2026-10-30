"""Admin-only endpoints under /api/v1/admin."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import DbSession, require_permission
from app.core.permissions import Permission
from app.db.models import User
from app.schemas.user import UserCreate, UserRead
from app.services.users import EmailAlreadyRegisteredError, create_user, list_users

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(
    body: UserCreate,
    db: DbSession,
    admin: Annotated[User, Depends(require_permission(Permission.USERS_CREATE))],
) -> User:
    try:
        return create_user(
            db,
            email=body.email,
            password=body.password,
            role=body.role,
            created_by=admin,
        )
    except EmailAlreadyRegisteredError as exc:
        # 409 Conflict: the request is valid, but clashes with existing data.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        ) from exc


@router.get("/users", response_model=list[UserRead])
def list_users_endpoint(
    db: DbSession,
    _: Annotated[User, Depends(require_permission(Permission.USERS_READ))],
) -> list[User]:
    # `_` = "I need this check to run, but don't use the value".
    return list_users(db)

"""POST /api/v1/auth/login"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.core.security import create_access_token
from app.db.models import AuditAction
from app.schemas.auth import Token
from app.services import audit
from app.services.auth import authenticate_user, normalize_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    # The OAuth2 standard calls the field "username"; ours holds the email.
    user = authenticate_user(db, email=form.username, password=form.password)
    if user is None:
        # Repeated failures for one email = someone guessing passwords.
        # We log the attempted email (never the password), cut to fit the column.
        audit.record(db, AuditAction.LOGIN_FAILED, target=normalize_email(form.username)[:255])
        db.commit()
        # Same message for "no such user", "wrong password" and "inactive",
        # so the response never reveals which emails have accounts.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    audit.record(db, AuditAction.LOGIN_SUCCEEDED, actor_id=user.id, target=f"user:{user.id}")
    db.commit()

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)

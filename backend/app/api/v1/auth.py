"""POST /api/v1/auth/login"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession
from app.core.security import create_access_token
from app.schemas.auth import Token
from app.services.auth import authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> Token:
    # The OAuth2 standard calls the field "username"; ours holds the email.
    user = authenticate_user(db, email=form.username, password=form.password)
    if user is None:
        # Same message for "no such user", "wrong password" and "inactive",
        # so the response never reveals which emails have accounts.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)

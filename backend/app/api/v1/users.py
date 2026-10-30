"""GET /api/v1/users/me"""

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.db.models import User
from app.schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> User:
    # Asking for CurrentUser is all it takes to make a route require login.
    # response_model=UserRead filters the User down to the safe fields.
    return current_user

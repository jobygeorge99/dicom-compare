"""Schemas for users.

Why not just return the SQLAlchemy User object? Because it holds
password_hash. A schema is an explicit allow-list: only the fields listed
here can ever leave the API. Forgetting a field is safe; leaking one is not.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models import Role
from app.services.users import MIN_PASSWORD_LENGTH


class UserRead(BaseModel):
    # from_attributes lets Pydantic read fields straight off a User object
    # (user.email, user.role...) instead of needing a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: Role
    is_active: bool
    created_at: datetime


class UserCreate(BaseModel):
    """What an admin sends to POST /api/v1/admin/users.

    Pydantic checks all of this BEFORE our code runs; bad input gets an
    automatic 422 response listing exactly which field is wrong.
    """

    email: EmailStr  # must look like a real email address
    # max_length: Argon2 is slow on purpose, so a 1 MB "password" could tie up the server.
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=128)
    role: Role = Role.ANALYST  # least privilege by default

"""Schemas for users.

Why not just return the SQLAlchemy User object? Because it holds
password_hash. A schema is an explicit allow-list: only the fields listed
here can ever leave the API. Forgetting a field is safe; leaking one is not.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import Role


class UserRead(BaseModel):
    # from_attributes lets Pydantic read fields straight off a User object
    # (user.email, user.role...) instead of needing a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: Role
    is_active: bool
    created_at: datetime

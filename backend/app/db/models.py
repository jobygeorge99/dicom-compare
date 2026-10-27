"""Database models: each class here becomes a table.

Phase 1 has one table, `users`. Comparisons and the audit log come later.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Role(StrEnum):
    """The three roles from the architecture brief.

    StrEnum members are also real strings: Role.ADMIN == "admin" is True,
    so they drop straight into JSON responses and JWT tokens.
    """

    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Never the password itself: a one-way Argon2 hash (added in the next step).
    password_hash: Mapped[str] = mapped_column(String(255))

    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            native_enum=False,  # store as VARCHAR, not a Postgres ENUM type
            length=20,
            values_callable=lambda roles: [r.value for r in roles],  # store "admin", not "ADMIN"
        ),
        default=Role.ANALYST,
    )

    # Deactivate instead of delete, so the audit log never points at a missing user.
    is_active: Mapped[bool] = mapped_column(default=True)

    # Filled in by Postgres at insert time, stored with its time zone.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        # What you see when you print(user) while debugging. Never include password_hash.
        return f"User(id={self.id}, email={self.email!r}, role={self.role})"

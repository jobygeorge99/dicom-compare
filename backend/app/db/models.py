"""Database models: each class here becomes a table.

Phase 1: `users` and `audit_log`. Comparisons come in Phase 2.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
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


class AuditAction(StrEnum):
    """Every kind of event we record. A fixed list keeps the log searchable."""

    LOGIN_SUCCEEDED = "login_succeeded"
    LOGIN_FAILED = "login_failed"
    USER_CREATED = "user_created"


class AuditLog(Base):
    """An append-only record of who did what, and when.

    Rows are only ever inserted, never updated or deleted. That is what makes
    the log trustworthy when someone asks "who created this account?".
    """

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Who did it. Nullable: a failed login may not belong to any real user.
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)

    action: Mapped[AuditAction] = mapped_column(
        Enum(
            AuditAction,
            native_enum=False,
            length=50,
            values_callable=lambda actions: [a.value for a in actions],
        ),
        index=True,
    )

    # What it was done to, in a short readable form, e.g. "user:7".
    target: Mapped[str | None] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,  # audit queries are almost always "between these dates"
    )

"""Write entries to the audit log.

`record` only ADDS the entry to the session; the caller commits. So the
audit entry and the change it describes are saved in ONE transaction:
either both are stored or neither is. A log that says "user created" for a
user that was never saved would be worse than no log.
"""

from sqlalchemy.orm import Session

from app.db.models import AuditAction, AuditLog


def record(
    db: Session,
    action: AuditAction,
    actor_id: int | None = None,
    target: str | None = None,
) -> None:
    db.add(AuditLog(action=action, actor_id=actor_id, target=target))

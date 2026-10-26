"""Health endpoints, used by Azure (and Docker, Kubernetes...) to check the app.

Two kinds, a standard enterprise pattern:
- /health        "liveness":  is the process up? Never touches the DB, so a
                  DB outage doesn't make the platform restart a healthy app.
- /health/ready  "readiness": can it serve real traffic? Checks the DB.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    # `Depends(get_db)` is dependency injection: FastAPI calls get_db() for us
    # and passes the Session in. Tests can swap it for a fake.
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ready"}

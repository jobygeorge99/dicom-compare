"""Application entry point.

Run locally (from the backend folder):  uvicorn app.main:app --reload
`app.main:app` means: import module app/main.py, use the variable `app`.
"""

from fastapi import FastAPI

from app.api import health
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Routers group related endpoints. Each feature gets its own router file,
# and main.py just plugs them in. Auth and users come next, under /api/v1.
app.include_router(health.router)

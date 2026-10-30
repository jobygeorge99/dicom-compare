"""Collects every v1 router under the /api/v1 prefix.

Versioning the URL means a future /api/v2 can change things without
breaking the frontend (or anyone else) still calling v1.
"""

from fastapi import APIRouter

from app.api.v1 import admin, auth, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(admin.router)

"""Schemas for login.

A schema describes the SHAPE of data crossing the API boundary. FastAPI uses
it to validate input, convert output to JSON, and draw the /docs page.
"""

from typing import Literal

from pydantic import BaseModel


class Token(BaseModel):
    """What POST /api/v1/auth/login returns.

    The field names are fixed by the OAuth2 standard, so tools like the
    /docs "Authorize" button know how to read them.
    """

    access_token: str
    token_type: Literal["bearer"] = "bearer"

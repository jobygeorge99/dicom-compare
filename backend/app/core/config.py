"""App settings, read from environment variables (and the repo-root .env file).

Why a Settings class instead of os.getenv() everywhere?
- One place lists every setting the app needs.
- Pydantic validates types at startup: a bad value fails fast, not mid-request.
- On Azure, the same fields are filled from App Service settings / Key Vault,
  with zero code changes. That is the "12-factor app" config principle.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[3] is the repo root, where .env lives.
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        extra="ignore",  # .env also holds POSTGRES_* for docker; ignore those here
    )

    app_name: str = "DICOM Compare API"
    app_env: str = "local"  # local | staging | production
    database_url: str = "postgresql+psycopg://dicom:change-me-locally@localhost:5432/dicom_compare"


@lru_cache  # build Settings once, then reuse the same object everywhere
def get_settings() -> Settings:
    return Settings()

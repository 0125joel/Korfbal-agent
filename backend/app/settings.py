"""Application-level environment settings."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[1]
_DOTENV_PATH = _BACKEND_DIR / ".env"

# Load .env early so other modules that rely on os.environ also benefit.
if _DOTENV_PATH.exists():
    load_dotenv(_DOTENV_PATH)


class AppSettings(BaseSettings):
    """Settings read from environment variables or .env files."""

    api_key: Optional[str] = Field(default=None, alias="API_KEY")
    cors_origins: List[str] = Field(default_factory=list, alias="CORS_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=_DOTENV_PATH,
        env_prefix="",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            if not value.strip():
                return []
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        if isinstance(value, list):
            return value
        raise TypeError("Invalid cors origins value")


app_settings = AppSettings()

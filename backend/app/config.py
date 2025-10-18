"""Applicatieconfiguratie en paden."""
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Globale instellingen voor de FastAPI-applicatie."""

    model_path: Path = Field(
        default=Path(__file__).resolve().parents[2] / "models" / "yolo_korfbal.pt",
        description="Pad naar het YOLO-modelbestand.",
    )
    confidence_threshold: float = Field(
        default=0.4,
        ge=0.0,
        le=1.0,
        description="Minimum confidence voor detecties.",
    )
    goal_iou_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="IOU-drempel om bal en korf te koppelen.",
    )
    retention_seconds: int = Field(
        default=900,
        description="Hoe lang shots in het geheugen blijven (rolling window).",
    )
    api_prefix: str = Field(default="/api")
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    log_level: str = Field(default="INFO")
    next_public_base_url: Optional[str] = Field(
        default=None, description="Optioneel basisadres voor frontend-API-calls."
    )

    model_config = SettingsConfigDict(
        env_prefix="KORFBAL_",
        case_sensitive=False,
    )


def get_settings() -> Settings:
    """Returneert een singleton Settings-instance."""
    return Settings()


settings = get_settings()

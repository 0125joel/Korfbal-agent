"""Pydantic-schema's voor API payloads."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class PlayerShot(BaseModel):
    player_id: str = Field(..., description="Unieke speleridentifier")
    player_name: Optional[str] = Field(None, description="Leesbare spelersnaam")
    x: float = Field(..., ge=0.0, le=1.0, description="Genormaliseerde x-positie op het veld")
    y: float = Field(..., ge=0.0, le=1.0, description="Genormaliseerde y-positie op het veld")
    scored: bool = Field(..., description="Of de poging een doelpunt werd")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = Field(..., ge=0.0, le=1.0, description="Vertrouwen in de voorspelling")


class HeatmapPoint(BaseModel):
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    value: float = Field(..., ge=0.0)


class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]
    grid_size: int


class PlayerStats(BaseModel):
    player_id: str
    player_name: Optional[str]
    attempts: int
    goals: int
    accuracy: float


class StatsResponse(BaseModel):
    shots: List[PlayerShot]
    players: List[PlayerStats]


class FrameMetadata(BaseModel):
    match_id: str
    frame_timestamp: datetime
    player_id: Optional[str]
    player_name: Optional[str]


class FramePayload(BaseModel):
    image_base64: str = Field(..., description="Frame in base64 (JPEG/PNG)")
    metadata: FrameMetadata


class ModelInfo(BaseModel):
    name: str
    version: str
    classes: List[str]
    confidence_threshold: float


class EventType(str, Enum):
    SHOT = "shot"
    GOAL = "goal"
    MISS = "miss"
    REBOUND = "rebound"


class Event(BaseModel):
    event_type: EventType
    x: float = Field(..., ge=0.0, le=1.0)
    y: float = Field(..., ge=0.0, le=1.0)
    ts_ms: int = Field(..., ge=0)
    player_id: Optional[str] = Field(default=None)
    payload: Optional[dict[str, Any]] = None


class EventBatchRequest(BaseModel):
    events: List[Event]


class EventBatchResponse(BaseModel):
    added: int


class EventResetResponse(BaseModel):
    removed: int


class EventListResponse(BaseModel):
    events: List[Event]
    total: int
    limit: int
    offset: int

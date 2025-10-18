"""FastAPI applicatie voor korfbal video-analyse."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import (
    Body,
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .schemas import (
    EventBatchRequest,
    EventBatchResponse,
    EventListResponse,
    EventResetResponse,
    FramePayload,
    HeatmapResponse,
    ModelInfo,
    PlayerShot,
    StatsResponse,
)
from .services.analyzer import ShotAnalyzer, create_analyzer
from .services.events import EventStore, event_store
from .services.state import ShotStore, store
from .settings import app_settings

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), "INFO"))
LOGGER = logging.getLogger(__name__)

SERVICE_NAME = "korfbal-live-analytics"
SERVICE_VERSION = "1.0.0"

cors_origins = app_settings.cors_origins or settings.cors_origins or ["*"]

app = FastAPI(
    title="Korfbal Live Analytics",
    version=SERVICE_VERSION,
    openapi_url=f"{settings.api_prefix}/openapi.json",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
LOGGER.info("CORS origins ingesteld op: %s", ", ".join(cors_origins))

FRONTEND_DIR = Path(__file__).resolve().parents[3] / "frontend" / "out"
if FRONTEND_DIR.exists():
    LOGGER.info("Mount frontend static bestanden vanuit %s", FRONTEND_DIR)
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:  # type: ignore[misc]
        return {"message": "Korfbal analytics API", "docs": f"{settings.api_prefix}/docs"}


async def get_store() -> ShotStore:
    return store


async def get_analyzer(store: ShotStore = Depends(get_store)) -> ShotAnalyzer:
    if not hasattr(app.state, "analyzer"):
        app.state.analyzer = create_analyzer(store)
    return app.state.analyzer


async def get_event_store() -> EventStore:
    return event_store


async def enforce_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    required_key = app_settings.api_key
    if required_key and x_api_key != required_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


@app.get("/healthz", include_in_schema=False)
async def healthz() -> dict[str, object]:
    return {"ok": True, "service": SERVICE_NAME, "version": SERVICE_VERSION}


@app.get(f"{settings.api_prefix}/model", response_model=ModelInfo)
async def model_info(analyzer: ShotAnalyzer = Depends(get_analyzer)) -> ModelInfo:
    names = list(getattr(analyzer._model, "names", {}).values()) if analyzer._model else []
    version = getattr(analyzer._model, "ckpt_path", "unknown") if analyzer._model else "unavailable"
    return ModelInfo(
        name="YOLO Korfbal",
        version=str(version),
        classes=names,
        confidence_threshold=settings.confidence_threshold,
    )


@app.post(f"{settings.api_prefix}/frames/analyze", response_model=Optional[PlayerShot])
async def analyze_frame(
    payload: FramePayload = Body(...),
    analyzer: ShotAnalyzer = Depends(get_analyzer),
) -> Optional[PlayerShot]:
    shot = analyzer.analyze(payload)
    if shot is None:
        return None
    return shot


@app.get(f"{settings.api_prefix}/stats", response_model=StatsResponse)
async def stats(store: ShotStore = Depends(get_store)) -> StatsResponse:
    return store.to_stats()


@app.get(f"{settings.api_prefix}/heatmap", response_model=HeatmapResponse)
async def heatmap(grid_size: int = 10, store: ShotStore = Depends(get_store)) -> HeatmapResponse:
    return store.to_heatmap(grid_size=grid_size)


@app.websocket(f"{settings.api_prefix}/ws/frames")
async def websocket_frames(
    websocket: WebSocket,
    analyzer: ShotAnalyzer = Depends(get_analyzer),
) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            frame = FramePayload.model_validate(payload)
            shot = analyzer.analyze(frame)
            await websocket.send_json({"shot": shot.model_dump() if shot else None})
    except WebSocketDisconnect:
        LOGGER.info("WebSocket afgesloten")
    except Exception as exc:  # pragma: no cover - runtime logging
        LOGGER.exception("WebSocket fout: %s", exc)
        await websocket.send_json({"error": str(exc)})
        await websocket.close()


@app.post(
    f"{settings.api_prefix}/events/batch",
    response_model=EventBatchResponse,
    dependencies=[Depends(enforce_api_key)],
)
async def ingest_events(
    payload: EventBatchRequest, store: EventStore = Depends(get_event_store)
) -> EventBatchResponse:
    added = store.add_many(payload.events)
    return EventBatchResponse(added=added)


@app.post(
    f"{settings.api_prefix}/events/reset",
    response_model=EventResetResponse,
    dependencies=[Depends(enforce_api_key)],
)
async def reset_events(store: EventStore = Depends(get_event_store)) -> EventResetResponse:
    removed = store.reset()
    return EventResetResponse(removed=removed)


@app.get(f"{settings.api_prefix}/events/all", response_model=EventListResponse)
async def list_events(
    limit: int = 100,
    offset: int = 0,
    store: EventStore = Depends(get_event_store),
) -> EventListResponse:
    limit = max(1, min(limit, 500))
    offset = max(offset, 0)
    events = store.list_events(limit=limit, offset=offset)
    return EventListResponse(events=events, total=store.total, limit=limit, offset=offset)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    LOGGER.debug("Validatiefout op %s: %s", request.url, exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    LOGGER.exception("Onverwachte fout op %s: %s", request.url, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

"""FastAPI applicatie voor korfbal video-analyse."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import Body, Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .schemas import FramePayload, HeatmapResponse, ModelInfo, PlayerShot, StatsResponse
from .services.analyzer import ShotAnalyzer, create_analyzer
from .services.state import ShotStore, store

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), "INFO"))
LOGGER = logging.getLogger(__name__)

app = FastAPI(title="Korfbal Live Analytics", openapi_url=f"{settings.api_prefix}/openapi.json")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get(f"{settings.api_prefix}/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
            frame = FramePayload.parse_obj(payload)
            shot = analyzer.analyze(frame)
            await websocket.send_json({"shot": shot.dict() if shot else None})
    except WebSocketDisconnect:
        LOGGER.info("WebSocket afgesloten")
    except Exception as exc:  # pragma: no cover - runtime logging
        LOGGER.exception("WebSocket fout: %s", exc)
        await websocket.send_json({"error": str(exc)})
        await websocket.close()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):  # type: ignore[override]
    LOGGER.exception("Onverwachte fout: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

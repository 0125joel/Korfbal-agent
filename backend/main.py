from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlitedict import SqliteDict

DB_PATH = "events.sqlite"

app = FastAPI(title="Korfbal Analytics API", version="0.1.0")

# CORS: frontend mag overal vandaan tijdens dev; in prod zet je dit strakker
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class Event(BaseModel):
    ts_ms: int                  # tijdstempel in ms vanaf start video
    event_type: str             # "shot"|"goal"|"rebound"|"assist"
    player_id: Optional[str]    # later rugnummer; nu bv. "tracker-12"
    x: float                    # 0..1 genormaliseerd X (veldbreedte)
    y: float                    # 0..1 genormaliseerd Y (veldlengte)
    distance_m: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

def _read_all() -> list:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        return db.get("events", [])

def _write_all(data: list) -> None:
    with SqliteDict(DB_PATH, autocommit=True) as db:
        db["events"] = data

@app.get("/")
def root():
    return {"ok": True, "service": "korfbal-analytics-api"}

@app.post("/events/batch")
def upload_events(events: List[Event]):
    data = _read_all()
    data.extend([e.model_dump() for e in events])
    _write_all(data)
    return {"ok": True, "added": len(events), "total": len(data)}

@app.post("/events/reset")
def reset():
    _write_all([])
    return {"ok": True, "total": 0}

@app.get("/events/all")
def all_events():
    return {"events": _read_all()}

@app.get("/stats")
def stats():
    per_player = {}
    for e in _read_all():
        pid = e.get("player_id") or "unknown"
        per_player.setdefault(pid, {"shots":0,"goals":0,"rebounds":0,"assists":0})
        et = e["event_type"]
        if et == "shot":    per_player[pid]["shots"]   += 1
        if et == "goal":    per_player[pid]["goals"]   += 1
        if et == "rebound": per_player[pid]["rebounds"]+= 1
        if et == "assist":  per_player[pid]["assists"] += 1
    return {"players": per_player}

@app.get("/heatmap")
def heatmap():
    points = []
    for e in _read_all():
        if e["event_type"] in ("shot","goal"):
            points.append({
                "x": e["x"], "y": e["y"],
                "goal": e["event_type"]=="goal",
                "dist": e.get("distance_m")
            })
    return {"points": points}

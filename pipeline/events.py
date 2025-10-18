"""Simple heuristic event extraction."""
from __future__ import annotations

from typing import List

import pandas as pd

from agent.tools import seconds_to_ts


def classify_events(tracks: pd.DataFrame) -> pd.DataFrame:
    """Translate tracking rows into event candidates.

    The placeholder converts the mock tracking rows into "shot" events with
    alternating outcomes so that the UI has a couple of different event types to
    display.
    """

    if tracks.empty:
        return pd.DataFrame(columns=["t", "ts", "event", "team", "player", "x", "y"])

    rows: List[dict] = []
    outcomes = ["shot", "goal", "rebound"]
    for idx, (_, row) in enumerate(tracks.iterrows()):
        event_type = outcomes[idx % len(outcomes)]
        rows.append(
            {
                "t": seconds_to_ts(row["ts"]),
                "ts": row["ts"],
                "event": event_type,
                "team": "Thuis" if idx % 2 == 0 else "Uit",
                "player": (idx % 8) + 1,
                "defended": bool(idx % 2),
                "half": 1 if row["ts"] < 600 else 2,
                "x": row.get("x", 0.5),
                "y": row.get("y", 0.5),
                "confidence": row.get("confidence", 0.8),
            }
        )
    return pd.DataFrame(rows)

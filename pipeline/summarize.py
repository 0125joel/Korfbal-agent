"""Generate human readable summaries and statistics for event tables."""
from __future__ import annotations

from typing import Dict

import pandas as pd


def summarize(events: pd.DataFrame) -> Dict:
    if events.empty:
        return {"headline": "Nog geen events beschikbaar", "metrics": {}}

    totals = {
        "events": int(len(events)),
        "goals": int((events.get("event") == "goal").sum()),
        "shots": int((events.get("event") == "shot").sum()),
        "rebounds": int((events.get("event") == "rebound").sum()),
    }

    goal_events = events[events.get("event") == "goal"] if "event" in events else pd.DataFrame()
    top_scorer = None
    if not goal_events.empty and "player" in goal_events:
        top_scorer = (
            goal_events.groupby("player").size().sort_values(ascending=False).index.astype(str).tolist()
        )
        top_scorer = top_scorer[0] if top_scorer else None

    headline = f"{totals['goals']} doelpunten uit {totals['shots']} schoten (demo)."
    summary = {"headline": headline, "metrics": totals}
    if top_scorer:
        summary["top_scorer"] = top_scorer
    return summary

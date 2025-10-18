"""Generate human readable summaries and statistics for event tables."""
from __future__ import annotations

from typing import Dict, Mapping

import pandas as pd


def _metrics(df: pd.DataFrame) -> Dict[str, int]:
    return {
        "events": int(len(df)),
        "goals": int((df.get("event") == "goal").sum()),
        "shots": int((df.get("event") == "shot").sum()),
        "rebounds": int((df.get("event") == "rebound").sum()),
    }


def _headline_for_status(status: str, totals: Mapping[str, int], halves: Mapping[int, Mapping[str, int]]) -> str:
    shots = totals.get("shots", 0)
    goals = totals.get("goals", 0)

    if status == "halftime" and 1 in halves:
        half = halves[1]
        return f"Rust: {half.get('goals', 0)} doelpunten uit {half.get('shots', 0)} schoten."
    if status == "fulltime" and {1, 2}.issubset(halves.keys()):
        first = halves[1]
        second = halves[2]
        return (
            "Eindtijd: {total_goals} doelpunten (1e helft {first_goals}, 2e helft {second_goals})."
        ).format(
            total_goals=goals,
            first_goals=first.get("goals", 0),
            second_goals=second.get("goals", 0),
        )

    return f"Live: {goals} doelpunten uit {shots} schoten."


def summarize(events: pd.DataFrame) -> Dict:
    if events.empty:
        return {"headline": "Nog geen events beschikbaar", "metrics": {}, "status": "idle"}

    totals = _metrics(events)

    halves: Dict[int, Dict[str, int]] = {}
    if "half" in events.columns:
        for half_id, frame in events.groupby("half"):
            try:
                half_key = int(half_id)
            except (TypeError, ValueError):
                continue
            halves[half_key] = _metrics(frame)

    status = "in_progress"
    if 1 in halves and 2 not in halves:
        status = "halftime"
    elif {1, 2}.issubset(halves.keys()):
        status = "fulltime"

    goal_events = events[events.get("event") == "goal"] if "event" in events else pd.DataFrame()
    top_scorer = None
    if not goal_events.empty and "player" in goal_events:
        ranking = (
            goal_events.groupby("player").size().sort_values(ascending=False).index.astype(str).tolist()
        )
        top_scorer = ranking[0] if ranking else None

    headline = _headline_for_status(status, totals, halves)
    summary = {"headline": headline, "metrics": totals, "status": status}
    if halves:
        summary["halves"] = halves
    if top_scorer:
        summary["top_scorer"] = top_scorer
    return summary

"""Utility helpers for working with event data and lightweight visualisations.

The helpers here intentionally remain lightweight so that they can be reused by
Streamlit, the agent layer and offline pipelines alike.  Real models and
analytics can slot in later – the goal for now is to provide a clear contract
for where new capabilities should be implemented.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

import json

import pandas as pd
import plotly.graph_objects as go

OUTPUT_DIR = Path("outputs")
EVENTS_PATH = OUTPUT_DIR / "events.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "summary.json"


def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_events(limit: Optional[int] = None) -> pd.DataFrame:
    """Load stored events into a :class:`~pandas.DataFrame`.

    Parameters
    ----------
    limit:
        Optional maximum amount of rows to return. ``None`` keeps everything.
    """

    if not EVENTS_PATH.exists():
        return pd.DataFrame()

    records: List[Dict[str, Any]] = []
    with EVENTS_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    df = pd.DataFrame(records)
    if limit is not None and not df.empty:
        return df.tail(limit)
    return df


def save_events(df: pd.DataFrame) -> None:
    """Persist the provided event table to ``events.jsonl``."""

    _ensure_output_dir()
    with EVENTS_PATH.open("w", encoding="utf-8") as handle:
        for _, row in df.iterrows():
            handle.write(json.dumps(row.to_dict(), ensure_ascii=False) + "\n")


def load_summary(default: Optional[Mapping[str, Any]] = None) -> Mapping[str, Any]:
    """Load the stored summary structure, falling back to ``default``."""

    if not SUMMARY_PATH.exists():
        return default or {}

    with SUMMARY_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_summary(summary: Mapping[str, Any]) -> None:
    """Persist a summary payload for later retrieval."""

    _ensure_output_dir()
    with SUMMARY_PATH.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)


def seconds_to_ts(seconds: float) -> str:
    """Format seconds into ``HH:MM:SS.mmm``."""

    total_ms = int(round(seconds * 1000))
    ms = total_ms % 1000
    total_seconds = total_ms // 1000
    minutes, sec = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{sec:02d}.{ms:03d}"


def search_events(df: pd.DataFrame, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Very small helper that filters events by ``query``.

    A real system could hook into semantic search.  For the starter template we
    perform a case-insensitive substring match across a couple of textual
    columns.
    """

    if df.empty:
        return []

    query = (query or "").strip().lower()
    if not query:
        return df.tail(limit).to_dict(orient="records")

    mask = pd.Series(False, index=df.index)
    for column in ["event", "team", "player", "note"]:
        if column in df.columns:
            values = df[column].astype(str).str.lower().str.contains(query, na=False)
            mask = mask | values

    results = df[mask]
    if results.empty:
        return []

    return results.tail(limit).to_dict(orient="records")


def plot_shotmap(df: pd.DataFrame, title: str = "Shotmap") -> go.Figure:
    """Generate a basic half-court scatter plot for (x, y) coordinates."""

    fig = go.Figure()
    if not df.empty and {"x", "y"}.issubset(df.columns):
        fig.add_trace(
            go.Scatter(
                x=df["x"],
                y=df["y"],
                mode="markers",
                marker=dict(size=10, color=df.get("defended", False), colorscale="Viridis"),
                text=df.get("event"),
                name="events",
            )
        )

    fig.update_layout(
        title=title,
        xaxis=dict(title="Court width", range=[0, 1]),
        yaxis=dict(title="Court length", range=[0, 1]),
        height=400,
    )
    return fig

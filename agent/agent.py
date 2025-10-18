"""Minimal agent layer tying together the various helper utilities."""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd

from .indexer import EventIndexer
from .tools import load_events, load_summary

_INDEXER = EventIndexer()


def _prepare_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    return df.to_dict(orient="records")


def answer(query: str) -> Dict[str, Any]:
    """Return a structured response for the Streamlit UI."""

    events = load_events()
    if events.empty:
        return {"text": "Nog geen events geladen. Run analyse.", "items": []}

    records = _prepare_records(events)
    _INDEXER.build(records)
    ranked = _INDEXER.query(query, top_k=10)
    items = [row for _, row in ranked] or records[-10:]

    summary = load_summary({})
    summary_line = summary.get("headline") if isinstance(summary, dict) else None
    if summary_line:
        text = summary_line
    else:
        text = f"{len(items)} resultaten gevonden (demo)."

    return {"text": text, "items": items, "summary": summary}

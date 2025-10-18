"""Lightweight FAISS-style index wrapper used by the demo agent.

The implementation tries to import :mod:`faiss`.  If it is unavailable we fall
back to a simple Python based ranking that still exposes the same API so that
higher layers of the application do not have to care about the underlying
back-end.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    faiss = None  # type: ignore


Vector = np.ndarray


def _tokenise(text: str) -> List[str]:
    return [tok for tok in text.lower().replace("/", " ").split() if tok]


def _to_vector(tokens: Iterable[str], dim: int = 256) -> Vector:
    vec = np.zeros(dim, dtype="float32")
    for token in tokens:
        index = hash(token) % dim
        vec[index] += 1.0
    if vec.sum() > 0:
        vec /= np.linalg.norm(vec)
    return vec


@dataclass
class EventIndexer:
    """Very small helper around FAISS (or a Python fallback)."""

    dimension: int = 256
    texts: List[str] = field(default_factory=list)
    records: List[Dict] = field(default_factory=list)
    _index: "faiss.Index" | None = field(default=None, init=False, repr=False)

    def build(self, events: Sequence[Dict]) -> None:
        self.texts = []
        self.records = []
        vectors: List[Vector] = []

        for row in events:
            text_parts = [
                str(row.get(key, ""))
                for key in ("event", "team", "player", "note")
                if row.get(key)
            ]
            text = " ".join(text_parts).strip().lower()
            self.texts.append(text)
            self.records.append(row)
            vectors.append(_to_vector(_tokenise(text), self.dimension))

        if faiss is not None and vectors:
            stacked = np.stack(vectors)
            self._index = faiss.IndexFlatIP(self.dimension)
            self._index.add(stacked)
        else:
            self._index = None

    def query(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict]]:
        if not self.records:
            return []

        query = (query or "").strip().lower()
        if not query:
            return [(1.0, record) for record in self.records[-top_k:]]

        if self._index is not None and faiss is not None:
            vector = _to_vector(_tokenise(query), self.dimension)
            distances, indices = self._index.search(vector[np.newaxis, :], top_k)
            results: List[Tuple[float, Dict]] = []
            for score, idx in zip(distances[0], indices[0]):
                if idx < 0:
                    continue
                results.append((float(score), self.records[int(idx)]))
            return results

        scores: List[Tuple[float, Dict]] = []
        for record, text in zip(self.records, self.texts):
            if query in text:
                scores.append((1.0, record))
            else:
                overlap = len(set(_tokenise(query)) & set(_tokenise(text)))
                if overlap:
                    scores.append((overlap / len(_tokenise(query)), record))
        scores.sort(key=lambda item: item[0], reverse=True)
        return scores[:top_k]

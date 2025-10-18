"""In-memory opslag voor generieke events."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from itertools import islice
from typing import Deque, Iterable, List

from ..schemas import Event


@dataclass
class EventStore:
    """Buffer die events bewaart met eenvoudige paginatie."""

    max_events: int = 10_000
    _events: Deque[Event] = field(default_factory=deque)

    def add_many(self, events: Iterable[Event]) -> int:
        count = 0
        for event in events:
            self._events.append(event)
            count += 1
            if len(self._events) > self.max_events:
                self._events.popleft()
        return count

    def reset(self) -> int:
        removed = len(self._events)
        self._events.clear()
        return removed

    def list_events(self, limit: int, offset: int) -> List[Event]:
        if offset < 0:
            offset = 0
        if limit <= 0:
            return []
        iterator = islice(self._events, offset, offset + limit)
        return list(iterator)

    @property
    def total(self) -> int:
        return len(self._events)


event_store = EventStore()

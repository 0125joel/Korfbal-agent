"""In-memory opslag van shots en aggregaties."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Deque, List

from ..config import settings
from ..schemas import HeatmapPoint, HeatmapResponse, PlayerShot, PlayerStats, StatsResponse


@dataclass
class ShotStore:
    """Bewaar een sliding window aan shots."""

    retention: timedelta = field(
        default_factory=lambda: timedelta(seconds=settings.retention_seconds)
    )
    _shots: Deque[PlayerShot] = field(default_factory=deque)

    def add_shot(self, shot: PlayerShot) -> None:
        self._shots.append(shot)
        self._prune()

    def _prune(self) -> None:
        threshold = datetime.utcnow() - self.retention
        while self._shots and self._shots[0].timestamp < threshold:
            self._shots.popleft()

    def recent_shots(self) -> List[PlayerShot]:
        self._prune()
        return list(self._shots)

    def to_stats(self) -> StatsResponse:
        shots = self.recent_shots()
        player_map: dict[str, list[PlayerShot]] = {}
        for shot in shots:
            player_map.setdefault(shot.player_id, []).append(shot)
        players: list[PlayerStats] = []
        for player_id, attempts in player_map.items():
            goals = sum(1 for shot in attempts if shot.scored)
            players.append(
                PlayerStats(
                    player_id=player_id,
                    player_name=attempts[0].player_name,
                    attempts=len(attempts),
                    goals=goals,
                    accuracy=goals / len(attempts) if attempts else 0.0,
                )
            )
        players.sort(key=lambda p: p.goals, reverse=True)
        return StatsResponse(shots=shots, players=players)

    def to_heatmap(self, grid_size: int = 10) -> HeatmapResponse:
        shots = self.recent_shots()
        if not shots:
            return HeatmapResponse(points=[], grid_size=grid_size)
        grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
        for shot in shots:
            gx = min(grid_size - 1, int(shot.x * grid_size))
            gy = min(grid_size - 1, int(shot.y * grid_size))
            weight = 1.0 if shot.scored else 0.5
            grid[gy][gx] += weight
        points: list[HeatmapPoint] = []
        for y, row in enumerate(grid):
            for x, value in enumerate(row):
                if value <= 0:
                    continue
                points.append(
                    HeatmapPoint(
                        x=(x + 0.5) / grid_size,
                        y=(y + 0.5) / grid_size,
                        value=value,
                    )
                )
        return HeatmapResponse(points=points, grid_size=grid_size)


store = ShotStore()

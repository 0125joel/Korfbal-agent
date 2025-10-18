"""Detection + tracking placeholder pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class DetectionConfig:
    model_name: str = "yolov8n.pt"
    conf_threshold: float = 0.25
    tracking_method: str = "bytetrack"


def detect_and_track(video_path: Path, config: DetectionConfig | None = None) -> pd.DataFrame:
    """Return a mock detection dataframe.

    A real implementation would invoke Ultralytics YOLOv8 for detection and feed
    detections into ByteTrack.  The placeholder simply constructs a couple of
    made-up rows so that downstream steps have something to work with.
    """

    config = config or DetectionConfig()
    data: List[dict] = []
    timestamps = [0.0, 5.2, 11.4]
    for idx, ts in enumerate(timestamps, start=1):
        data.append(
            {
                "frame": idx * 25,
                "ts": ts,
                "track_id": idx,
                "x": 0.4 + idx * 0.05,
                "y": 0.2 + idx * 0.1,
                "confidence": config.conf_threshold + 0.1,
            }
        )
    return pd.DataFrame(data)

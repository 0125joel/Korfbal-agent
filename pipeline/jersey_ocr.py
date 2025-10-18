"""Placeholder for jersey number OCR."""
from __future__ import annotations

from typing import Optional

import numpy as np


class JerseyOCR:
    """Thin wrapper mimicking an EasyOCR based recogniser."""

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or "easyocr_korfbal"

    def recognise(self, image: np.ndarray) -> str:
        """Return a fake jersey number so downstream steps have data."""

        # A deterministic pseudo result keeps demos predictable.
        checksum = int(image.sum()) if image.size else 0
        return str((checksum % 99) + 1)

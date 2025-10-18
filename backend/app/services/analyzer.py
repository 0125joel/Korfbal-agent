"""Service voor het analyseren van frames met behulp van een YOLO-model."""
from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO

from ..config import settings
from ..schemas import FramePayload, PlayerShot
from .state import ShotStore

LOGGER = logging.getLogger(__name__)


@dataclass
class Detection:
    """Vereenvoudigde representatie van een YOLO-detectie."""

    class_name: str
    confidence: float
    bbox: np.ndarray  # [x1, y1, x2, y2]

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return (float((x1 + x2) / 2.0), float((y1 + y2) / 2.0))

    @property
    def area(self) -> float:
        x1, y1, x2, y2 = self.bbox
        return max(0.0, float(x2 - x1)) * max(0.0, float(y2 - y1))


class ShotAnalyzer:
    """Analyseert frames en produceert shot-events."""

    def __init__(self, store: ShotStore) -> None:
        self._store = store
        try:
            self._model = YOLO(str(settings.model_path))
        except FileNotFoundError as exc:  # pragma: no cover - alleen tijdens setup
            LOGGER.warning("Kon model niet laden: %s", exc)
            self._model = None
        self._class_names = self._model.names if self._model else {}
        LOGGER.info("ShotAnalyzer initialised met classes: %s", self._class_names)

    def analyze(self, payload: FramePayload) -> Optional[PlayerShot]:
        """Voer inference uit en voeg eventueel een shot toe aan de store."""
        if not self._model:
            LOGGER.error("Model niet geladen, sla frame over")
            return None

        frame = self._decode_frame(payload.image_base64)
        if frame is None:
            LOGGER.error("Frame kon niet worden gedecodeerd")
            return None

        height, width, _ = frame.shape
        LOGGER.debug("Ontvangen frame met resolutie %sx%s", width, height)

        results = self._model.predict(
            frame,
            conf=settings.confidence_threshold,
            verbose=False,
        )
        detections = self._parse_detections(results[0])
        basket = self._select_largest(detections, target_classes={"basket", "hoop"})
        ball = self._select_highest_confidence(detections, target_classes={"ball", "korfbal"})

        if not basket or not ball:
            LOGGER.debug("Geen basket (%s) of bal (%s) gedetecteerd", bool(basket), bool(ball))
            return None

        scored = self._is_goal(basket, ball)
        normalized_x, normalized_y = self._normalize(ball.center, width, height)

        shot = PlayerShot(
            player_id=payload.metadata.player_id or "unknown",
            player_name=payload.metadata.player_name,
            x=normalized_x,
            y=normalized_y,
            scored=scored,
            timestamp=payload.metadata.frame_timestamp,
            confidence=ball.confidence,
        )
        self._store.add_shot(shot)
        LOGGER.info(
            "Shot geregistreerd voor speler %s (goal=%s, confidence=%.2f)",
            shot.player_id,
            shot.scored,
            shot.confidence,
        )
        return shot

    @staticmethod
    def _decode_frame(encoded: str) -> Optional[np.ndarray]:
        try:
            binary = base64.b64decode(encoded)
            with Image.open(io.BytesIO(binary)) as img:
                img = img.convert("RGB")
                array = np.array(img)
            # YOLO verwacht BGR
            return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
        except Exception as exc:  # pragma: no cover - logging bij onverwachte data
            LOGGER.exception("Kon base64-frame niet decoderen: %s", exc)
            return None

    def _parse_detections(self, result) -> list[Detection]:
        detections: list[Detection] = []
        if result is None:
            return detections
        names = self._class_names or result.names
        for bbox, confidence, cls_idx in zip(
            result.boxes.xyxy.cpu().numpy(),
            result.boxes.conf.cpu().numpy(),
            result.boxes.cls.cpu().numpy(),
        ):
            class_name = names.get(int(cls_idx), str(int(cls_idx)))
            detections.append(
                Detection(
                    class_name=class_name.lower(),
                    confidence=float(confidence),
                    bbox=bbox,
                )
            )
        return detections

    @staticmethod
    def _select_largest(
        detections: list[Detection], target_classes: set[str]
    ) -> Optional[Detection]:
        target = [d for d in detections if d.class_name in target_classes]
        if not target:
            return None
        return max(target, key=lambda d: d.area)

    @staticmethod
    def _select_highest_confidence(
        detections: list[Detection], target_classes: set[str]
    ) -> Optional[Detection]:
        target = [d for d in detections if d.class_name in target_classes]
        if not target:
            return None
        return max(target, key=lambda d: d.confidence)

    @staticmethod
    def _normalize(center: tuple[float, float], width: int, height: int) -> tuple[float, float]:
        cx, cy = center
        return cx / max(width, 1), cy / max(height, 1)

    def _is_goal(self, basket: Detection, ball: Detection) -> bool:
        iou = self._iou(basket.bbox, ball.bbox)
        LOGGER.debug("IOU basket/ball = %.3f", iou)
        if iou >= settings.goal_iou_threshold:
            return True
        # fallback: bal onder basket met hoge confidence
        bx1, by1, bx2, by2 = basket.bbox
        cx, cy = ball.center
        within_horizontal = bx1 <= cx <= bx2
        below_rim = cy >= by1 and cy <= by2 + (by2 - by1) * 0.25
        return within_horizontal and below_rim and ball.confidence >= settings.confidence_threshold

    @staticmethod
    def _iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
        xA = max(box_a[0], box_b[0])
        yA = max(box_a[1], box_b[1])
        xB = min(box_a[2], box_b[2])
        yB = min(box_a[3], box_b[3])

        inter_area = max(0.0, xB - xA) * max(0.0, yB - yA)
        if inter_area <= 0:
            return 0.0
        box_a_area = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
        box_b_area = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
        union = box_a_area + box_b_area - inter_area
        return float(inter_area / union) if union > 0 else 0.0


def create_analyzer(store: ShotStore) -> ShotAnalyzer:
    return ShotAnalyzer(store)

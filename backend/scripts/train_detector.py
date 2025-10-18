"""Train een YOLO-model voor korfbaldoel detectie."""
from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train YOLO voor korfbal")
    parser.add_argument("--data", required=True, help="Pad naar dataset YAML")
    parser.add_argument("--model", default="yolov8n.pt", help="Basismodel")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--project", default="runs/train-korfbal")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        project=args.project,
        name="korfbal",
    )
    best = Path(args.project) / "korfbal" / "weights" / "best.pt"
    print(f"Training gereed. Beste model: {best}")


if __name__ == "__main__":
    main()

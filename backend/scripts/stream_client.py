"""Voorbeeldscript om frames via WebSocket te versturen."""
from __future__ import annotations

import argparse
import asyncio
import base64
from datetime import datetime
from pathlib import Path

import cv2
import websockets


def encode_image(path: Path) -> str:
    frame = cv2.imread(str(path))
    if frame is None:
        raise FileNotFoundError(f"Kon afbeelding niet lezen: {path}")
    _, buffer = cv2.imencode(".jpg", frame)
    return base64.b64encode(buffer).decode("utf-8")


async def stream(websocket_url: str, image_path: Path) -> None:
    payload = {
        "image_base64": encode_image(image_path),
        "metadata": {
            "match_id": "demo",
            "frame_timestamp": datetime.utcnow().isoformat() + "Z",
            "player_id": "demo",
            "player_name": "Demo Speler",
        },
    }
    async with websockets.connect(websocket_url) as ws:
        await ws.send(json.dumps(payload))
        response = await ws.recv()
        print(response)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stuur testframe via websocket")
    parser.add_argument("--url", default="ws://localhost:7860/api/ws/frames")
    parser.add_argument("--image", type=Path, required=True)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    await stream(args.url, args.image)


if __name__ == "__main__":
    import json

    asyncio.run(main())

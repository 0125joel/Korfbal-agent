"""Placeholder utilities for ingesting live korfball streams."""
from __future__ import annotations

from pathlib import Path
from typing import Optional


def build_streamlink_command(youtube_url: str, output: Path) -> str:
    """Return the command that Streamlink should execute.

    The function does not run the process – it simply returns the command string
    so that downstream orchestrators can decide how and when to execute it.
    """

    quality = "720p,best"
    output.parent.mkdir(parents=True, exist_ok=True)
    return f"streamlink --default-stream {quality} {youtube_url} best -o {output}"


def ingest_youtube(youtube_url: str, output_dir: Path, filename: Optional[str] = None) -> Path:
    """Return the path where the downloaded stream will live.

    Actual downloading is outside the scope of this starter; returning the path
    keeps the rest of the pipeline easy to test.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / (filename or "korfbal_live.mp4")
    command = build_streamlink_command(youtube_url, target)
    # In a real implementation you might call subprocess.run(command, ...)
    # For now we simply return the path so tests can verify expectations.
    return target

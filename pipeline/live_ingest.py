"""Utilities to ingest live korfball streams during phase 0.2.

The goal for this iteration of the project is to provide an orchestration layer
capable of pulling a YouTube Live HLS feed to disk using Streamlink.  The code
below intentionally keeps the responsibilities lightweight: discover the stream,
launch Streamlink in a background process and expose simple status reporting so
that the UI (or other orchestrators) can inform the user about progress.

In a production-ready implementation the ingested stream would be processed by
the detection/tracking pipeline.  For now the emphasis is on proving that live
ingest is possible and providing hooks for later stages.
"""
from __future__ import annotations

import shlex
import shutil
import subprocess
import threading
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Deque, Iterable, List, Optional

try:  # yt-dlp is optional during development but recommended for validation.
    from yt_dlp import YoutubeDL
except ModuleNotFoundError:  # pragma: no cover - handled gracefully at runtime.
    YoutubeDL = None  # type: ignore[assignment]


class LiveIngestError(RuntimeError):
    """Raised when live ingest prerequisites are missing or fail."""


def _require_streamlink() -> None:
    if shutil.which("streamlink") is None:
        raise LiveIngestError(
            "Streamlink is niet gevonden. Installeer het pakket (pip install streamlink) "
            "of voeg het toe aan de PATH voordat live ingest kan starten."
        )


def build_streamlink_command(youtube_url: str, output: Path, quality: str = "720p,best") -> List[str]:
    """Return a tokenised Streamlink command for easier :mod:`subprocess` usage."""

    output.parent.mkdir(parents=True, exist_ok=True)
    return shlex.split(
        f"streamlink --default-stream {shlex.quote(quality)} {shlex.quote(youtube_url)} best -o {shlex.quote(str(output))}"
    )


def probe_youtube_stream(youtube_url: str) -> Optional[dict]:
    """Return basic metadata about the YouTube stream using :mod:`yt_dlp`.

    The helper is best-effort.  If :mod:`yt_dlp` is not installed the function
    returns ``None`` so that callers can decide how to inform the user.
    """

    if YoutubeDL is None:
        return None

    options = {"quiet": True, "skip_download": True, "noplaylist": True}
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
    return {
        "title": info.get("title"),
        "is_live": info.get("is_live"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
    }


@dataclass
class LiveIngestor:
    """Manage the lifecycle of a Streamlink ingest process."""

    youtube_url: str
    output_dir: Path
    filename: Optional[str] = None
    duration: Optional[int] = None  # seconds
    poll_interval: float = 1.0
    quality: str = "720p,best"
    _process: Optional[subprocess.Popen] = field(init=False, default=None, repr=False)
    _log_buffer: Deque[str] = field(init=False, default_factory=lambda: deque(maxlen=200), repr=False)
    _log_thread: Optional[threading.Thread] = field(init=False, default=None, repr=False)

    def start(self) -> Path:
        """Launch Streamlink and start capturing stderr for log feedback."""

        _require_streamlink()
        command = build_streamlink_command(self.youtube_url, self.output_path, quality=self.quality)
        self._process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        if self._process.stderr is not None:
            self._log_thread = threading.Thread(target=self._capture_streamlink_logs, daemon=True)
            self._log_thread.start()

        if self.duration:
            timer = threading.Timer(self.duration, self.stop)
            timer.daemon = True
            timer.start()

        return self.output_path

    def stop(self) -> None:
        """Terminate the Streamlink process if it is running."""

        if self._process is None:
            return

        if self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def read_logs(self, limit: int = 20) -> List[str]:
        """Return the latest Streamlink log lines for UI presentation."""

        lines = list(self._log_buffer)
        if limit:
            return lines[-limit:]
        return lines

    @property
    def output_path(self) -> Path:
        return self.output_dir / (self.filename or "korfbal_live.mp4")

    def _capture_streamlink_logs(self) -> None:
        assert self._process is not None and self._process.stderr is not None
        for line in iter(self._process.stderr.readline, ""):
            if not line:
                break
            cleaned = line.strip()
            if cleaned:
                self._log_buffer.append(cleaned)
        self._process = None


def ingest_youtube(youtube_url: str, output_dir: Path, filename: Optional[str] = None, duration: Optional[int] = None) -> Path:
    """Convenience wrapper to ingest a stream without manually creating a class instance."""

    ingestor = LiveIngestor(youtube_url=youtube_url, output_dir=output_dir, filename=filename, duration=duration)
    return ingestor.start()


def tail_logs(ingestor: LiveIngestor, lines: int = 20) -> str:
    """Return a newline separated string of the most recent log lines."""

    return "\n".join(ingestor.read_logs(lines))


def run_cli(args: Optional[Iterable[str]] = None) -> int:
    """Small CLI mainly useful for manual testing and documentation snippets."""

    import argparse

    parser = argparse.ArgumentParser(description="Start a Streamlink ingest for a YouTube live stream.")
    parser.add_argument("url", help="YouTube (live) URL")
    parser.add_argument("--output", type=Path, default=Path("data/live"), help="Directory to store the capture in.")
    parser.add_argument("--filename", help="Optional filename for the captured stream.")
    parser.add_argument("--duration", type=int, help="Optional maximum duration in seconds.")
    parsed = parser.parse_args(args=args)

    ingestor = LiveIngestor(
        youtube_url=parsed.url,
        output_dir=parsed.output,
        filename=parsed.filename,
        duration=parsed.duration,
    )

    try:
        path = ingestor.start()
    except LiveIngestError as exc:  # pragma: no cover - CLI feedback only.
        parser.error(str(exc))
        return 1

    print(f"Streamlink gestart, output: {path}")
    try:
        while ingestor.is_running():
            pass
    finally:
        ingestor.stop()
    print("Ingest afgerond")
    return 0


if __name__ == "__main__":  # pragma: no cover - manual CLI usage.
    raise SystemExit(run_cli())

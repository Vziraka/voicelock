"""Microphone capture — 16 kHz mono PCM with injectable streams for tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16_000
CHANNELS = 1
MAX_SECONDS = 30.0
DTYPE = np.float32


class CaptureStatus(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    ERROR = "error"


@dataclass
class CaptureEngine:
    """Click-toggle capture with level frames and a soft 30s auto-stop.

    `open_input` and `clock` are injectable so Gate tests never touch a real mic.
    """

    sample_rate: int = SAMPLE_RATE
    max_seconds: float = MAX_SECONDS
    open_input: Callable[..., Any] = sd.InputStream
    clock: Callable[[], float] = field(default_factory=lambda: __import__("time").monotonic)
    status: CaptureStatus = CaptureStatus.IDLE
    error_message: str | None = None
    _chunks: list[np.ndarray] = field(default_factory=list)
    _levels: list[float] = field(default_factory=list)
    _started_at: float | None = None
    _stream: Any = None

    @property
    def is_recording(self) -> bool:
        return self.status == CaptureStatus.RECORDING

    @property
    def levels(self) -> list[float]:
        return list(self._levels)

    def pcm_buffer(self) -> np.ndarray:
        """Return captured mono PCM (empty array if nothing recorded)."""
        if not self._chunks:
            return np.zeros(0, dtype=DTYPE)
        return np.concatenate(self._chunks).astype(DTYPE, copy=False)

    def start(self) -> None:
        """Start recording. On mic failure, set ERROR (no crash, no silent success)."""
        if self.status == CaptureStatus.RECORDING:
            return
        self._chunks.clear()
        self._levels.clear()
        self.error_message = None
        try:
            stream = self.open_input(
                samplerate=self.sample_rate,
                channels=CHANNELS,
                dtype=DTYPE,
                callback=self._on_audio,
            )
            stream.start()
        except Exception as exc:  # noqa: BLE001 — surface any open failure as mic error
            self.status = CaptureStatus.ERROR
            self.error_message = _mic_error_message(exc)
            self._stream = None
            return
        self._stream = stream
        self._started_at = self.clock()
        self.status = CaptureStatus.RECORDING

    def stop(self) -> np.ndarray:
        """Stop recording and return the PCM buffer."""
        if self.status != CaptureStatus.RECORDING:
            return self.pcm_buffer()
        self._close_stream()
        self.status = CaptureStatus.IDLE
        self._started_at = None
        return self.pcm_buffer()

    def toggle(self) -> np.ndarray | None:
        """Click-toggle: start if idle, stop if recording. Returns buffer on stop."""
        if self.status == CaptureStatus.RECORDING:
            return self.stop()
        self.start()
        return None

    def pump(self, frames: np.ndarray | None = None) -> None:
        """Advance capture: optional fake frames + soft-cap check.

        Tests call this with injected frames. Live use can call it periodically
        (or rely on the stream callback) to enforce the 30s auto-stop.
        """
        if self.status != CaptureStatus.RECORDING:
            return
        if frames is not None:
            self._ingest(np.asarray(frames, dtype=DTYPE).reshape(-1))
        if self._started_at is not None and (self.clock() - self._started_at) >= self.max_seconds:
            self.stop()

    def _on_audio(self, indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
        del frames, time_info, status
        if self.status != CaptureStatus.RECORDING:
            return
        mono = np.asarray(indata[:, 0], dtype=DTYPE).copy()
        self._ingest(mono)
        if self._started_at is not None and (self.clock() - self._started_at) >= self.max_seconds:
            # Tearing the stream down here would deadlock: Pa_StopStream blocks
            # until this callback returns. Raise sounddevice's supported
            # in-callback stop and let pump()/stop() converge the engine state.
            raise sd.CallbackStop

    def _ingest(self, mono: np.ndarray) -> None:
        if mono.size == 0:
            return
        self._chunks.append(mono)
        # RMS level in [0, 1] for the visualizer bars.
        rms = float(np.sqrt(np.mean(np.square(mono))))
        self._levels.append(min(1.0, rms))

    def _close_stream(self) -> None:
        stream = self._stream
        self._stream = None
        if stream is None:
            return
        try:
            stream.stop()
        except Exception:  # noqa: BLE001
            pass
        try:
            stream.close()
        except Exception:  # noqa: BLE001
            pass


def _mic_error_message(exc: BaseException) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    lowered = text.lower()
    if "permission" in lowered or "denied" in lowered:
        return "Microphone permission denied"
    return "No microphone available"

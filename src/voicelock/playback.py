"""Playback of captured PCM buffers — injectable output for Gate tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import sounddevice as sd

from voicelock.capture import DTYPE, SAMPLE_RATE


@dataclass
class PlaybackEngine:
    """Play a mono PCM buffer; support stop so the Booth is not stuck listening.

    `play` / `wait` / `stop_output` are injectable so Gate tests never need real speakers.
    """

    sample_rate: int = SAMPLE_RATE
    play: Callable[..., None] = sd.play
    wait: Callable[[], None] = sd.wait
    stop_output: Callable[[], None] = sd.stop
    last_frames: np.ndarray | None = field(default=None, init=False)
    completed: bool = field(default=False, init=False)
    is_playing: bool = field(default=False, init=False)
    interrupted: bool = field(default=False, init=False)

    def play_buffer(self, pcm: np.ndarray, *, block: bool = True) -> None:
        """Play `pcm` (mono float PCM). If `block`, wait until finished or stopped."""
        frames = np.asarray(pcm, dtype=DTYPE).reshape(-1)
        if frames.size == 0:
            raise ValueError("Cannot play an empty PCM buffer")
        self.stop()
        self.completed = False
        self.interrupted = False
        self.last_frames = frames
        self.is_playing = True
        self.play(frames, self.sample_rate)
        if block:
            self.wait()
            self.is_playing = False
            self.completed = not self.interrupted

    def stop(self) -> None:
        """Stop playback early (or clear a finished stream)."""
        was_playing = self.is_playing
        if was_playing:
            try:
                self.stop_output()
            except Exception:  # noqa: BLE001
                pass
            self.is_playing = False
            self.interrupted = True
            self.completed = False

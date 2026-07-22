"""Playback of captured PCM buffers — injectable output for Gate tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import sounddevice as sd

from voicelock.capture import DTYPE, SAMPLE_RATE


@dataclass
class PlaybackEngine:
    """Play a mono PCM buffer to completion.

    `play` is injectable so Gate tests never need real speakers.
    """

    sample_rate: int = SAMPLE_RATE
    play: Callable[..., None] = sd.play
    wait: Callable[[], None] = sd.wait
    last_frames: np.ndarray | None = field(default=None, init=False)
    completed: bool = field(default=False, init=False)

    def play_buffer(self, pcm: np.ndarray) -> None:
        """Play `pcm` (mono float PCM) and wait until it finishes."""
        frames = np.asarray(pcm, dtype=DTYPE).reshape(-1)
        if frames.size == 0:
            raise ValueError("Cannot play an empty PCM buffer")
        self.completed = False
        self.last_frames = frames
        self.play(frames, self.sample_rate)
        self.wait()
        self.completed = True

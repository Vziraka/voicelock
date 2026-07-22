"""Playback engine tests — injectable fake output only (no real speakers)."""

from __future__ import annotations

import numpy as np

from voicelock.capture import SAMPLE_RATE
from voicelock.playback import PlaybackEngine


def test_playback_completes_without_error() -> None:
    played: list[tuple[np.ndarray, int]] = []
    waits: list[bool] = []

    def fake_play(data: np.ndarray, samplerate: int) -> None:
        played.append((np.asarray(data).copy(), samplerate))

    def fake_wait() -> None:
        waits.append(True)

    engine = PlaybackEngine(play=fake_play, wait=fake_wait)
    pcm = (0.25 * np.sin(2 * np.pi * 440.0 * np.arange(800) / SAMPLE_RATE)).astype(
        np.float32
    )

    engine.play_buffer(pcm)

    assert engine.completed is True
    assert len(played) == 1
    assert played[0][1] == SAMPLE_RATE
    assert played[0][0].size == pcm.size
    assert waits == [True]

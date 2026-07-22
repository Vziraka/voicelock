"""Playback engine tests — injectable fake output only (no real speakers)."""

from __future__ import annotations

import numpy as np

from voicelock.capture import SAMPLE_RATE
from voicelock.playback import PlaybackEngine


def _tone(samples: int = 800) -> np.ndarray:
    return (0.25 * np.sin(2 * np.pi * 440.0 * np.arange(samples) / SAMPLE_RATE)).astype(
        np.float32
    )


def test_playback_completes_without_error() -> None:
    played: list[tuple[np.ndarray, int]] = []
    waits: list[bool] = []

    def fake_play(data: np.ndarray, samplerate: int) -> None:
        played.append((np.asarray(data).copy(), samplerate))

    def fake_wait() -> None:
        waits.append(True)

    engine = PlaybackEngine(play=fake_play, wait=fake_wait, stop_output=lambda: None)
    pcm = _tone()

    engine.play_buffer(pcm)

    assert engine.completed is True
    assert engine.is_playing is False
    assert len(played) == 1
    assert played[0][1] == SAMPLE_RATE
    assert played[0][0].size == pcm.size
    assert waits == [True]


def test_playback_can_stop_early() -> None:
    stops: list[bool] = []

    def fake_play(data: np.ndarray, samplerate: int) -> None:
        del data, samplerate

    def fake_stop() -> None:
        stops.append(True)

    engine = PlaybackEngine(play=fake_play, wait=lambda: None, stop_output=fake_stop)
    engine.play_buffer(_tone(), block=False)

    assert engine.is_playing is True
    engine.stop()
    assert engine.is_playing is False
    assert engine.interrupted is True
    assert engine.completed is False
    assert stops == [True]

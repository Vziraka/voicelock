"""Capture engine tests — injectable fake streams only (no real mic)."""

from __future__ import annotations

import numpy as np

from voicelock.capture import CaptureEngine, CaptureStatus, SAMPLE_RATE


class FakeStream:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def _tone(samples: int, amplitude: float = 0.4) -> np.ndarray:
    t = np.arange(samples, dtype=np.float32) / SAMPLE_RATE
    return (amplitude * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)


def test_start_stop_yields_nonempty_pcm() -> None:
    clock = FakeClock()
    engine = CaptureEngine(open_input=lambda **kw: FakeStream(**kw), clock=clock)

    engine.start()
    assert engine.status == CaptureStatus.RECORDING
    engine.pump(_tone(800))
    buf = engine.stop()

    assert engine.status == CaptureStatus.IDLE
    assert buf.size > 0
    assert buf.dtype == np.float32


def test_level_frames_emit_during_capture() -> None:
    engine = CaptureEngine(open_input=lambda **kw: FakeStream(**kw), clock=FakeClock())
    engine.start()
    engine.pump(_tone(400, amplitude=0.5))
    engine.pump(_tone(400, amplitude=0.2))

    assert len(engine.levels) >= 2
    assert all(0.0 <= level <= 1.0 for level in engine.levels)
    engine.stop()


def test_mic_unavailable_surfaces_error_state() -> None:
    def boom(**kwargs):
        raise OSError("PortAudio error: Device unavailable")

    engine = CaptureEngine(open_input=boom, clock=FakeClock())
    engine.start()

    assert engine.status == CaptureStatus.ERROR
    assert engine.error_message is not None
    assert "microphone" in engine.error_message.lower()
    assert engine.pcm_buffer().size == 0


def test_auto_stops_at_30s_soft_cap() -> None:
    clock = FakeClock()
    engine = CaptureEngine(
        open_input=lambda **kw: FakeStream(**kw),
        clock=clock,
        max_seconds=30.0,
    )
    engine.start()
    engine.pump(_tone(160))
    clock.advance(30.0)
    engine.pump(_tone(160))

    assert engine.status == CaptureStatus.IDLE
    assert engine.pcm_buffer().size > 0


def test_toggle_start_then_stop() -> None:
    engine = CaptureEngine(open_input=lambda **kw: FakeStream(**kw), clock=FakeClock())
    assert engine.toggle() is None
    assert engine.is_recording
    engine.pump(_tone(200))
    buf = engine.toggle()
    assert buf is not None and buf.size > 0
    assert not engine.is_recording

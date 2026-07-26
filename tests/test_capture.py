"""Capture engine tests — injectable fake streams only (no real mic)."""

from __future__ import annotations

import numpy as np
import pytest
import sounddevice as sd

from voicelock.capture import CaptureEngine, CaptureStatus, CHANNELS, SAMPLE_RATE


class ReentrantTeardown(BaseException):
    """Raised when a stream is torn down from inside its own callback.

    A `BaseException` subclass on purpose: `capture.py`'s `_close_stream` wraps
    `stream.stop()` and `stream.close()` in `except Exception: pass`, so an
    ordinary exception would be swallowed and the defect would hide.
    """


class FakeStream:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.callback = kwargs.get("callback")
        self.started = False
        self.stopped = False
        self.closed = False
        self.delivering = True
        self.callback_stopped = False
        self._in_callback = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self._forbid_reentrant_teardown("stop")
        self.stopped = True

    def close(self) -> None:
        self._forbid_reentrant_teardown("close")
        self.closed = True

    def deliver(self, mono: np.ndarray) -> None:
        """Hand frames to the callback the way PortAudio does.

        `indata` arrives 2-D as `(frames, channels)`. Delivery halts for good
        once the callback raises `sd.CallbackStop`, mirroring PortAudio's
        contract.
        """
        if not self.delivering:
            return
        indata = np.asarray(mono, dtype=np.float32).reshape(-1, CHANNELS)
        self._in_callback = True
        try:
            self.callback(indata, indata.shape[0], None, None)
        except sd.CallbackStop:
            self.callback_stopped = True
            self.delivering = False
        finally:
            self._in_callback = False

    def _forbid_reentrant_teardown(self, action: str) -> None:
        if self._in_callback:
            raise ReentrantTeardown(f"stream.{action}() called from inside the callback")


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


def test_callback_path_carries_audio_without_pump() -> None:
    """Frames delivered through the real `_on_audio` reach the buffer and levels."""
    streams: list[FakeStream] = []

    def open_input(**kwargs) -> FakeStream:
        stream = FakeStream(**kwargs)
        streams.append(stream)
        return stream

    engine = CaptureEngine(open_input=open_input, clock=FakeClock())
    engine.start()
    stream = streams[0]

    # No pump() anywhere in this test — the callback is the only path exercised.
    stream.deliver(_tone(400, amplitude=0.5))
    stream.deliver(_tone(400, amplitude=0.2))

    assert engine.pcm_buffer().size == 800
    assert len(engine.levels) == 2
    assert all(0.0 <= level <= 1.0 for level in engine.levels)


def test_teardown_from_inside_the_callback_trips_the_wire() -> None:
    """The tripwire escapes a blanket `except Exception` — capture.py has one."""
    holder: dict[str, FakeStream] = {}

    def tearing_callback(indata, frames, time_info, status) -> None:
        holder["stream"].stop()

    stream = FakeStream(callback=tearing_callback)
    holder["stream"] = stream

    with pytest.raises(ReentrantTeardown):
        try:
            stream.deliver(_tone(64))
        except Exception:  # mirrors capture.py's `_close_stream` blanket handler
            pass

    assert not stream.stopped


def test_delivery_halts_once_the_callback_raises_callback_stop() -> None:
    """PortAudio's contract: after CallbackStop, no further frames arrive."""
    frame_counts: list[int] = []

    def stopping_callback(indata, frames, time_info, status) -> None:
        frame_counts.append(frames)
        raise sd.CallbackStop

    stream = FakeStream(callback=stopping_callback)
    stream.deliver(_tone(64))
    stream.deliver(_tone(64))

    assert frame_counts == [64]
    assert stream.callback_stopped
    assert not stream.delivering

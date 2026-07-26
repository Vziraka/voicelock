"""Face engine tests — injectable fake camera and landmarker only (no real webcam).

The fake camera delivers frames through the **real `read()` the engine calls**,
and those frames flow through the engine's real frame-handling path into the real
composited output. `cv2.VideoCapture` has no callback, so `read()` is the
equivalent of the callback the F4.5 lesson requires a device double to deliver
through; a test that fabricated landmarks and skipped that path would be the same
hole in a different shape.
"""

from __future__ import annotations

import base64
import re
import time
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pytest

from voicelock.facedetect import (
    CAPTURE_HEIGHT,
    CAPTURE_WIDTH,
    DRAWN_POINTS,
    FACE_OVAL_POINTS,
    FRAME_INTERVAL,
    LIP_POINTS,
    PREVIEW_PX,
    TARGET_FPS,
    FaceEngine,
    FaceStatus,
    FrameResult,
    _centre_crop_square,
    _draw_overlay,
    pacing_delay,
)

LANDMARK_COUNT = 478
FIXTURE = Path(__file__).parent / "fixtures" / "face" / "portrait.jpg"
REFERENCE = Path(__file__).parent / "fixtures" / "face" / "portrait_expected_face_landmarks.pbtxt"

# Comfortably above the 0.005645 max deviation measured between the vendored
# bundle and MediaPipe's published reference, and still tight enough that a real
# preprocessing regression would break it.
REFERENCE_TOLERANCE = 0.02


@dataclass
class Pt:
    """Stands in for MediaPipe's NormalizedLandmark (x/y is all we consume)."""

    x: float
    y: float


class FakeResult:
    def __init__(self, landmarks: list[Pt] | None) -> None:
        self.face_landmarks = [landmarks] if landmarks else []


class FakeLandmarker:
    """Returns known landmarks and records the timestamps it was handed."""

    def __init__(self, landmarks: list[Pt] | None) -> None:
        self._landmarks = landmarks
        self.timestamps: list[int] = []

    def detect_for_video(self, image, timestamp_ms: int) -> FakeResult:
        del image
        self.timestamps.append(timestamp_ms)
        return FakeResult(self._landmarks)


class CameraUsedAfterRelease(BaseException):
    """Raised when `read()` happens after `release()`.

    A `BaseException` subclass on purpose, exactly as F4.5's `ReentrantTeardown`:
    an ordinary `Exception` would be swallowed by any blanket `except Exception`
    on a teardown path, and the leak would hide. It also records a flag, because
    an exception raised inside a daemon worker thread dies with that thread and
    would otherwise never reach the assertion.
    """


class FakeCamera:
    """Hands frames back through the real `read()` the engine calls."""

    def __init__(
        self,
        frames: list[np.ndarray] | None = None,
        *,
        opened: bool = True,
        read_ok: bool = True,
        repeat: bool = False,
    ) -> None:
        self._frames = list(frames or [])
        self._opened = opened
        self._read_ok = read_ok
        self._repeat = repeat
        self.released = False
        self.release_count = 0
        self.used_after_release = False
        self.props: dict[int, float] = {}
        self.read_count = 0

    def isOpened(self) -> bool:  # noqa: N802 — mirrors the cv2.VideoCapture API
        return self._opened

    def set(self, prop: int, value: float) -> bool:
        self.props[prop] = value
        return True

    def read(self) -> tuple[bool, np.ndarray | None]:
        if self.released:
            self.used_after_release = True
            raise CameraUsedAfterRelease("read() called after release()")
        self.read_count += 1
        if not self._read_ok or not self._frames:
            return False, None
        if self._repeat:
            return True, self._frames[(self.read_count - 1) % len(self._frames)]
        return True, self._frames.pop(0)

    def release(self) -> None:
        self.released = True
        self.release_count += 1


def _blank(value: int = 30) -> np.ndarray:
    return np.full((CAPTURE_HEIGHT, CAPTURE_WIDTH, 3), value, dtype=np.uint8)


def _landmarks(base: tuple[float, float] = (0.5, 0.5), overrides=None) -> list[Pt]:
    points = [Pt(base[0], base[1]) for _ in range(LANDMARK_COUNT)]
    for index, (x, y) in (overrides or {}).items():
        points[index] = Pt(x, y)
    return points


def _face_at(cx: float, cy: float, half_w: float = 0.07, half_h: float = 0.15) -> list[Pt]:
    """A landmark set whose face oval spans a known normalized box."""
    overrides = {}
    for n, index in enumerate(FACE_OVAL_POINTS):
        overrides[index] = (
            cx - half_w if n % 2 else cx + half_w,
            cy - half_h if n < len(FACE_OVAL_POINTS) // 2 else cy + half_h,
        )
    return _landmarks(base=(cx, cy), overrides=overrides)


def _engine(landmarks: list[Pt] | None, frames: list[np.ndarray] | None = None):
    cameras: list[FakeCamera] = []

    def open_camera(index):
        del index
        camera = FakeCamera(frames)
        cameras.append(camera)
        return camera

    engine = FaceEngine(open_camera=open_camera, landmarker=FakeLandmarker(landmarks))
    return engine, cameras


def _decode(data_uri: str) -> np.ndarray:
    assert data_uri.startswith("data:image/jpeg;base64,")
    raw = base64.b64decode(data_uri.split(",", 1)[1])
    return cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)


def _overlay_centroid(image: np.ndarray, background: int) -> tuple[float, float]:
    """Centre of the pixels the overlay changed."""
    delta = np.abs(image.astype(np.int16) - background).sum(axis=2)
    ys, xs = np.nonzero(delta > 40)
    assert xs.size > 0, "no overlay pixels were drawn"
    return float(xs.mean()), float(ys.mean())


# (1) frames flow through the real read path


def test_frames_from_read_reach_the_engine_and_come_out_composited() -> None:
    frames = [_blank(), _blank(), _blank()]
    engine, cameras = _engine(_face_at(0.5, 0.5), frames)

    camera = engine.acquire_camera()
    assert camera is not None
    assert engine.status != FaceStatus.ERROR

    ok, frame = camera.read()  # the real read path, not a fabricated frame
    assert ok
    result = engine.process_frame(frame)

    image = _decode(result.data_uri)
    assert image.shape == (PREVIEW_PX, PREVIEW_PX, 3)
    assert cameras[0].props[cv2.CAP_PROP_FRAME_WIDTH] == CAPTURE_WIDTH
    assert cameras[0].props[cv2.CAP_PROP_FRAME_HEIGHT] == CAPTURE_HEIGHT


def test_video_mode_timestamps_increase_monotonically() -> None:
    """`detect_for_video` requires it; the engine owns the counter."""
    engine, _ = _engine(_face_at(0.5, 0.5))
    for _ in range(4):
        engine.process_frame(_blank())

    stamps = engine.landmarker.timestamps
    assert stamps == sorted(stamps)
    assert len(set(stamps)) == len(stamps)


# (2) the overlay is drawn from real landmark output, and the crop maps it


def test_overlay_lands_where_the_crop_and_the_mirror_put_it() -> None:
    """A face on the LEFT of the frame must appear on the RIGHT of the preview.

    This is where a normalized-vs-pixel scaling bug, a crop-offset bug, or a
    missing mirror would show.
    """
    background = 30
    engine, _ = _engine(_face_at(0.25, 0.5))
    result = engine.process_frame(_blank(background))

    cx, cy = _overlay_centroid(_decode(result.data_uri), background)

    # 0.25 * 640 = 160 px in the full frame; the centre crop drops 80 px from
    # each side, so 80 px into the 480 px square; scaled to 172 px that is 28.7;
    # mirrored it is 171 - 28.7 = 142.3.
    scale = PREVIEW_PX / CAPTURE_HEIGHT
    expected_x = (PREVIEW_PX - 1) - (0.25 * CAPTURE_WIDTH - 80) * scale
    expected_y = 0.5 * CAPTURE_HEIGHT * scale

    assert cx == pytest.approx(expected_x, abs=8)
    assert cy == pytest.approx(expected_y, abs=8)
    assert cx > PREVIEW_PX / 2, "a face left of centre must render right of centre"


# (3) the lip contour is drawn, and the engine returns all 478


def test_lip_contour_is_among_the_drawn_points() -> None:
    assert LIP_POINTS, "no lip landmarks were resolved from MediaPipe's constants"
    assert set(LIP_POINTS).issubset(set(DRAWN_POINTS))


def test_engine_returns_all_478_landmarks_though_only_a_subset_is_drawn() -> None:
    engine, _ = _engine(_face_at(0.5, 0.5))
    result = engine.process_frame(_blank())

    assert len(result.landmarks) == LANDMARK_COUNT
    assert len(DRAWN_POINTS) < LANDMARK_COUNT


# (3b) the preview is mirrored, and ONLY the pixels are


def test_preview_is_the_mirror_of_the_unflipped_composite() -> None:
    """Catches someone 'fixing' the mirror by flipping coordinates instead."""
    frame = _blank()
    # An asymmetric frame makes the flip unambiguous.
    frame[:, : CAPTURE_WIDTH // 2] = 200
    landmarks = _face_at(0.35, 0.5)

    engine, _ = _engine(landmarks)
    got = _decode(engine.process_frame(frame).data_uri)

    # Build the expected UNFLIPPED composite with the module's own helpers, so
    # only the flip is under test rather than the whole pipeline re-implemented.
    canvas = frame.copy()
    _draw_overlay(canvas, landmarks)
    square = _centre_crop_square(canvas)
    unflipped = cv2.resize(square, (PREVIEW_PX, PREVIEW_PX), interpolation=cv2.INTER_AREA)

    diff = np.abs(got.astype(np.int16) - cv2.flip(unflipped, 1).astype(np.int16))
    assert diff.mean() < 6, "composite is not the horizontal mirror of the unflipped frame"


def test_returned_landmarks_are_unflipped() -> None:
    landmarks = _face_at(0.25, 0.5)
    engine, _ = _engine(landmarks)
    result = engine.process_frame(_blank())

    assert result.landmarks[0].x == pytest.approx(landmarks[0].x)
    assert result.landmarks[0].x < 0.5, "landmark data must stay in unmirrored coords"


# (4) no face in frame is a normal state


def test_no_face_in_frame_still_produces_a_frame_and_no_error() -> None:
    engine, _ = _engine(None)
    result = engine.process_frame(_blank())

    assert result.landmarks == []
    assert engine.status != FaceStatus.ERROR
    assert engine.error_message is None

    image = _decode(result.data_uri)
    assert image.shape == (PREVIEW_PX, PREVIEW_PX, 3)
    # Nothing was drawn: the preview is still the flat background.
    assert image.std() < 3


# (7) camera-open failure surfaces as ERROR


def test_camera_that_never_opens_surfaces_error() -> None:
    camera = FakeCamera(opened=False)
    engine = FaceEngine(open_camera=lambda index: camera, landmarker=FakeLandmarker(None))

    assert engine.acquire_camera() is None
    assert engine.status == FaceStatus.ERROR
    assert "camera" in engine.error_message.lower()
    assert camera.released


def test_camera_that_opens_but_yields_no_frames_surfaces_error() -> None:
    """A falsy `read()` must not be treated as 'no frame yet' — that spins forever."""
    camera = FakeCamera(read_ok=False)
    engine = FaceEngine(open_camera=lambda index: camera, landmarker=FakeLandmarker(None))

    assert engine.acquire_camera() is None
    assert engine.status == FaceStatus.ERROR
    assert engine.error_message
    assert camera.released
    assert camera.read_count == 1, "the engine must not retry a dead camera in a loop"


def test_camera_open_raising_surfaces_error() -> None:
    def boom(index):
        raise OSError("failed to open capture device")

    engine = FaceEngine(open_camera=boom, landmarker=FakeLandmarker(None))

    assert engine.acquire_camera() is None
    assert engine.status == FaceStatus.ERROR
    assert engine.error_message == "No camera available"


def test_permission_failure_gets_its_own_message() -> None:
    def denied(index):
        raise OSError("Camera access permission denied by the OS")

    engine = FaceEngine(open_camera=denied, landmarker=FakeLandmarker(None))
    engine.acquire_camera()

    assert engine.error_message == "Camera permission denied"


# The real model — no injected landmarker


def _reference_landmarks() -> list[tuple[float, float]]:
    text = REFERENCE.read_text(encoding="utf-8")
    pairs = re.findall(r"landmark \{\s*x: ([-\d.eE+]+)\s*y: ([-\d.eE+]+)", text)
    return [(float(x), float(y)) for x, y in pairs]


@pytest.mark.skipif(
    not FIXTURE.is_file(),
    reason=(
        "tests/fixtures/face/portrait.jpg is licence-restricted and deliberately "
        "not committed — fetch it per tests/fixtures/face/README.md"
    ),
)
def test_vendored_model_detects_a_real_face_matching_the_vendor_reference() -> None:
    """Separates 'the bundle is on disk' from 'the bundle works'."""
    engine = FaceEngine()  # no injected landmarker — the real vendored bundle
    result = engine.process_frame(cv2.imread(str(FIXTURE)))

    assert len(result.landmarks) == LANDMARK_COUNT

    expected = _reference_landmarks()
    assert len(expected) == LANDMARK_COUNT
    got = np.array([(lm.x, lm.y) for lm in result.landmarks])
    assert np.abs(got - np.array(expected)).max() < REFERENCE_TOLERANCE


def test_vendored_model_finds_no_face_in_a_plain_colour_image() -> None:
    engine = FaceEngine()  # the real bundle again
    result = engine.process_frame(_blank(128))

    assert result.landmarks == []
    assert engine.status != FaceStatus.ERROR


# ---------------------------------------------------------------------------
# Camera lifecycle
# ---------------------------------------------------------------------------


def _wait_for(predicate, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return False


def _running_engine(repeat_frames: int = 3):
    """An engine wired to a fake camera that keeps yielding frames."""
    cameras: list[FakeCamera] = []

    def open_camera(index):
        del index
        camera = FakeCamera([_blank() for _ in range(repeat_frames)], repeat=True)
        cameras.append(camera)
        return camera

    engine = FaceEngine(
        open_camera=open_camera, landmarker=FakeLandmarker(_face_at(0.5, 0.5))
    )
    return engine, cameras


# (5) Stop releases the camera


def test_stop_joins_the_worker_before_releasing_the_camera() -> None:
    """A read after release is a bug; the fake trips on it, loudly and from a thread."""
    engine, cameras = _running_engine()
    received: list[FrameResult] = []

    engine.start(received.append)
    assert engine.status == FaceStatus.RUNNING
    assert _wait_for(lambda: len(received) >= 2), "the worker never delivered frames"

    engine.stop()

    camera = cameras[0]
    assert camera.released
    assert camera.release_count == 1, "release() must happen exactly once"
    assert not camera.used_after_release, "the camera was read after release()"
    assert engine.status == FaceStatus.IDLE
    assert engine._thread is None
    assert all(r.data_uri.startswith("data:image/jpeg;base64,") for r in received)


def test_read_after_release_trips_a_wire_a_blanket_handler_cannot_swallow() -> None:
    """Proves the tripwire is armed — and that `except Exception` misses it."""
    camera = FakeCamera([_blank()])
    camera.release()

    with pytest.raises(CameraUsedAfterRelease):
        try:
            camera.read()
        except Exception:  # a blanket handler on a teardown path would eat a plain Exception
            pytest.fail("the tripwire was swallowed by `except Exception`")

    assert camera.used_after_release


def test_stop_is_idempotent_and_safe_after_a_failed_start() -> None:
    """A window-close handler needs both — it cannot know what state it is in."""
    engine = FaceEngine(
        open_camera=lambda index: FakeCamera(opened=False),
        landmarker=FakeLandmarker(None),
    )
    engine.start(lambda result: None)
    assert engine.status == FaceStatus.ERROR

    engine.stop()
    engine.stop()

    assert engine.status == FaceStatus.ERROR, "stop() must not erase a camera error"
    assert engine._thread is None


def test_camera_failure_starts_no_worker_thread() -> None:
    engine = FaceEngine(
        open_camera=lambda index: FakeCamera(read_ok=True, opened=False),
        landmarker=FakeLandmarker(None),
    )
    engine.start(lambda result: None)

    assert engine.status == FaceStatus.ERROR
    assert engine._thread is None


# (6) a second start after stop works


def test_second_start_after_stop_opens_a_fresh_camera_and_frames_flow_again() -> None:
    engine, cameras = _running_engine()

    first: list[FrameResult] = []
    engine.start(first.append)
    assert _wait_for(lambda: len(first) >= 1)
    engine.stop()

    second: list[FrameResult] = []
    engine.start(second.append)
    assert _wait_for(lambda: len(second) >= 1), "a second Record must bring frames back"
    engine.stop()

    assert len(cameras) == 2, "the second start must open a fresh camera"
    assert all(camera.released for camera in cameras)
    assert not any(camera.used_after_release for camera in cameras)
    assert engine.status == FaceStatus.IDLE


def test_start_after_a_failed_start_clears_the_stale_error() -> None:
    """A successful open is the only thing that should decide the status."""
    cameras: list[FakeCamera] = []

    def open_camera(index):
        del index
        camera = FakeCamera(
            [_blank() for _ in range(3)], repeat=True, opened=bool(cameras)
        )
        cameras.append(camera)
        return camera

    engine = FaceEngine(
        open_camera=open_camera, landmarker=FakeLandmarker(_face_at(0.5, 0.5))
    )

    engine.start(lambda result: None)  # first open fails
    assert engine.status == FaceStatus.ERROR
    assert engine.error_message

    received: list[FrameResult] = []
    engine.start(received.append)  # second open succeeds
    assert engine.status == FaceStatus.RUNNING
    assert engine.error_message is None
    assert _wait_for(lambda: len(received) >= 1)
    engine.stop()


# Drop frames, never queue them


def test_frames_are_dropped_not_queued_when_one_overruns_its_budget() -> None:
    """An overrun yields zero delay — the loop reads the newest frame instead
    of buffering the ones it missed. A queueing pipeline drifts."""
    assert pacing_delay(0.0) == pytest.approx(FRAME_INTERVAL)
    assert pacing_delay(FRAME_INTERVAL / 2) == pytest.approx(FRAME_INTERVAL / 2)
    assert pacing_delay(FRAME_INTERVAL) == 0.0
    assert pacing_delay(FRAME_INTERVAL * 4) == 0.0, "an overrun must never be repaid"


def test_frame_rate_is_a_named_constant() -> None:
    """The spec's fallback ladder must be a one-line edit."""
    assert TARGET_FPS == 30
    assert FRAME_INTERVAL == pytest.approx(1.0 / TARGET_FPS)


def _paced_clock(elapsed_per_frame: float):
    """A clock reporting a fixed elapsed time for every loop iteration.

    `_loop` calls it twice per frame — once before `read()`, once after
    `process_frame` — so odd calls open a frame and even calls close it.
    """
    state = {"now": 0.0, "calls": 0}

    def clock() -> float:
        state["calls"] += 1
        if state["calls"] % 2 == 1:
            return state["now"]
        state["now"] += elapsed_per_frame
        return state["now"]

    return clock


def test_an_overrun_frame_is_not_repaid_with_a_wait() -> None:
    """Drop, don't queue: an over-budget frame must cost ZERO extra delay.

    Discriminating on purpose. A loop that waited a flat `FRAME_INTERVAL`
    regardless of elapsed time would need >= 5 * 33 ms here and fail; only a
    loop that actually consults `pacing_delay` finishes fast.
    """
    engine, cameras = _running_engine()
    engine.clock = _paced_clock(FRAME_INTERVAL * 3)  # every frame overruns

    received: list[FrameResult] = []
    began = time.monotonic()
    engine.start(received.append)
    assert _wait_for(lambda: len(received) >= 5)
    engine.stop()
    wall = time.monotonic() - began

    assert wall < 5 * FRAME_INTERVAL * 0.6, (
        f"overrun frames were repaid with waits: {wall:.3f}s for 5 frames"
    )
    # One processed frame per read — nothing queued up behind the overrun.
    assert cameras[0].read_count >= len(received)
    assert not cameras[0].used_after_release


def test_an_under_budget_frame_is_paced_to_the_target_rate() -> None:
    """The other half: pacing must actually happen when there is budget left.

    Without this, an implementation that never waits at all would satisfy the
    overrun test above and silently run the camera flat out.
    """
    engine, _ = _running_engine()
    engine.clock = _paced_clock(0.0)  # every frame comes in instantly

    received: list[FrameResult] = []
    began = time.monotonic()
    engine.start(received.append)
    assert _wait_for(lambda: len(received) >= 4)
    engine.stop()
    wall = time.monotonic() - began

    assert wall >= 2 * FRAME_INTERVAL, (
        f"the worker did not pace itself: 4 frames in {wall:.3f}s"
    )


def test_a_camera_that_stops_delivering_mid_loop_surfaces_an_error() -> None:
    """A finite fake runs dry, which is the falsy-read branch inside `_loop`."""
    cameras: list[FakeCamera] = []

    def open_camera(index):
        del index
        # Two frames: one consumed by acquire_camera's probe, one by the loop.
        camera = FakeCamera([_blank(), _blank()])
        cameras.append(camera)
        return camera

    engine = FaceEngine(
        open_camera=open_camera, landmarker=FakeLandmarker(_face_at(0.5, 0.5))
    )
    received: list[FrameResult] = []
    engine.start(received.append)

    assert _wait_for(lambda: engine.status == FaceStatus.ERROR), (
        "a camera that stops delivering must not leave a dead loop behind RUNNING"
    )
    assert engine.error_message == "Camera stopped delivering frames"
    assert len(received) == 1

    engine.stop()
    assert cameras[0].released
    assert engine.status == FaceStatus.ERROR, "stop() must not erase the error"


def test_restarting_after_a_mid_loop_camera_failure_releases_the_dead_camera() -> None:
    """The leak the falsy-read branch would otherwise cause."""
    cameras: list[FakeCamera] = []

    def open_camera(index):
        del index
        if cameras:
            camera = FakeCamera([_blank() for _ in range(3)], repeat=True)
        else:
            camera = FakeCamera([_blank(), _blank()])
        cameras.append(camera)
        return camera

    engine = FaceEngine(
        open_camera=open_camera, landmarker=FakeLandmarker(_face_at(0.5, 0.5))
    )
    engine.start(lambda result: None)
    assert _wait_for(lambda: engine.status == FaceStatus.ERROR)

    received: list[FrameResult] = []
    engine.start(received.append)  # restart WITHOUT an explicit stop() first

    assert engine.status == FaceStatus.RUNNING
    assert _wait_for(lambda: len(received) >= 1)
    engine.stop()

    assert len(cameras) == 2
    assert cameras[0].released, "the dead camera was orphaned instead of released"
    assert all(not camera.used_after_release for camera in cameras)

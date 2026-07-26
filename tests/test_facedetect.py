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
    LIP_POINTS,
    PREVIEW_PX,
    FaceEngine,
    FaceStatus,
    _centre_crop_square,
    _draw_overlay,
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


class FakeCamera:
    """Hands frames back through the real `read()` the engine calls."""

    def __init__(
        self,
        frames: list[np.ndarray] | None = None,
        *,
        opened: bool = True,
        read_ok: bool = True,
    ) -> None:
        self._frames = list(frames or [])
        self._opened = opened
        self._read_ok = read_ok
        self.released = False
        self.props: dict[int, float] = {}
        self.read_count = 0

    def isOpened(self) -> bool:  # noqa: N802 — mirrors the cv2.VideoCapture API
        return self._opened

    def set(self, prop: int, value: float) -> bool:
        self.props[prop] = value
        return True

    def read(self) -> tuple[bool, np.ndarray | None]:
        self.read_count += 1
        if not self._read_ok or not self._frames:
            return False, None
        return True, self._frames.pop(0)

    def release(self) -> None:
        self.released = True


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

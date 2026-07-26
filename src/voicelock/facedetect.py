"""Webcam face detection — landmarks composited onto the Booth's round preview.

Shaped after `capture.py`: `open_camera` and `landmarker` are injectable so Gate
tests never touch a real webcam, and failures surface as an ERROR status with a
human-readable message rather than an exception.

This module owns both halves: the per-frame transform, and the camera lifecycle
that drives it on its own daemon thread.
"""

from __future__ import annotations

import base64
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import (
    FaceLandmarker,
    FaceLandmarkerOptions,
    RunningMode,
)
from mediapipe.tasks.python.vision.face_landmarker import FaceLandmarksConnections

CAMERA_INDEX = 0
CAPTURE_WIDTH = 640
CAPTURE_HEIGHT = 480
PREVIEW_PX = 172
JPEG_QUALITY = 80

# One named constant, so the spec's fallback ladder (30 -> 20 -> 15, on measured
# evidence) is a one-line edit rather than a hunt for scattered literals.
TARGET_FPS = 30
FRAME_INTERVAL = 1.0 / TARGET_FPS

# How long stop() waits for the worker to finish its current frame. Generous
# relative to the frame budget so a slow frame is joined rather than abandoned.
JOIN_TIMEOUT = 5.0

MODEL_PATH = (
    Path(__file__).resolve().parent / "models" / "face_landmarker" / "face_landmarker.task"
)

# Overlay styling is OpenCV's, not the Booth's CSS — matching the Booth's visual
# language is F9 polish, deliberately out of scope here.
OVERLAY_COLOR = (120, 255, 120)  # BGR
POINT_COLOR = (255, 210, 90)  # BGR
# Sized for the downscale, not for the capture frame: the overlay is drawn on the
# 640x480 frame and then shrunk ~2.8x to fit the 172 px disk, so a 1 px stroke
# would average away to nothing by the time it reaches the page.
ELLIPSE_THICKNESS = 5
POINT_RADIUS = 3


def _group_points(*groups: Any) -> tuple[int, ...]:
    """Flatten MediaPipe connection groups into a sorted tuple of point indices."""
    return tuple(sorted({i for g in groups for c in g for i in (c.start, c.end)}))


_CONNECTIONS = FaceLandmarksConnections

# Index groups come from MediaPipe's own published constants rather than
# hand-copied numbers, so the drawn subset cannot silently drift from the model's
# topology.
FACE_OVAL_POINTS = _group_points(_CONNECTIONS.FACE_LANDMARKS_FACE_OVAL)
LIP_POINTS = _group_points(_CONNECTIONS.FACE_LANDMARKS_LIPS)
DRAWN_POINTS = _group_points(
    _CONNECTIONS.FACE_LANDMARKS_LIPS,
    _CONNECTIONS.FACE_LANDMARKS_LEFT_EYE,
    _CONNECTIONS.FACE_LANDMARKS_RIGHT_EYE,
)


class FaceStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"


@dataclass
class FrameResult:
    """One composited preview frame plus the landmarks behind it.

    `data_uri` is the 172 px square the page renders: overlay drawn, centre-
    cropped, then mirrored. `landmarks` is the FULL 478-point set in unflipped,
    full-frame normalized coordinates — the display subset must not narrow the
    data contract, because later face features consume these points.
    """

    data_uri: str
    landmarks: list[Any]


@dataclass
class FaceEngine:
    """Per-frame face detection and preview compositing.

    `open_camera` and `landmarker` are injectable; the default landmarker is
    loaded lazily from the vendored bundle so importing this module costs
    nothing.
    """

    open_camera: Callable[..., Any] = cv2.VideoCapture
    landmarker: Any | None = None
    clock: Callable[[], float] = time.monotonic
    status: FaceStatus = FaceStatus.IDLE
    error_message: str | None = None
    _timestamp_ms: int = field(default=0, init=False)
    _camera: Any = field(default=None, init=False)
    _thread: threading.Thread | None = field(default=None, init=False)
    _stop_event: threading.Event = field(default_factory=threading.Event, init=False)

    @property
    def is_running(self) -> bool:
        return self.status == FaceStatus.RUNNING

    def acquire_camera(self) -> Any | None:
        """Open the camera, or set ERROR and return None.

        `cv2.VideoCapture` does not raise on a missing device — it returns an
        object whose `isOpened()` is False, and/or whose `read()` returns
        `(False, None)`. Both are checked here: treating a falsy `read()` as
        merely "no frame yet" would spin forever.
        """
        self.error_message = None
        try:
            camera = self.open_camera(CAMERA_INDEX)
        except Exception as exc:  # noqa: BLE001 — surface any open failure as camera error
            return self._fail(_camera_error_message(exc))
        if not camera.isOpened():
            camera.release()
            return self._fail("No camera available")
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT)
        ok, frame = camera.read()
        if not ok or frame is None:
            camera.release()
            return self._fail("Camera gave no frames")
        return camera

    def start(self, on_frame: Callable[[FrameResult], None]) -> None:
        """Open the camera and drive it from a daemon thread.

        Its own thread, not `app.py`'s 50 ms pump: that loop serves audio levels
        and must not be made to wait on a JPEG encode. On camera failure the
        status is left ERROR and no thread starts — the caller decides what that
        means for the rest of the take.
        """
        if self.is_running:
            return
        camera = self.acquire_camera()
        if camera is None:
            return
        self._camera = camera
        self._stop_event.clear()
        # Clears any ERROR left by an earlier failed start — a successful open
        # is the only thing that should decide the current status.
        self.status = FaceStatus.RUNNING
        self._thread = threading.Thread(
            target=self._loop, args=(on_frame,), name="voicelock-face", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the loop, join the worker, and only THEN release the camera.

        The ordering is the whole point: a frame read after `release()` is a bug,
        and releasing while the worker is still mid-read is how a webcam stays
        lit after the app thinks it let go. Safe to call twice, and safe to call
        after a failed start — a window-close handler needs both.
        """
        self._stop_event.set()
        thread, self._thread = self._thread, None
        if thread is not None:
            thread.join(timeout=JOIN_TIMEOUT)
        camera, self._camera = self._camera, None
        if camera is not None:
            camera.release()
        if self.is_running:
            self.status = FaceStatus.IDLE

    def _loop(self, on_frame: Callable[[FrameResult], None]) -> None:
        camera = self._camera
        while not self._stop_event.is_set():
            started = self.clock()
            ok, frame = camera.read()
            if not ok or frame is None:
                break
            on_frame(self.process_frame(frame))
            # Wait on the stop event rather than sleeping, so Stop is felt
            # immediately instead of after the rest of the frame budget.
            self._stop_event.wait(pacing_delay(self.clock() - started))

    def process_frame(self, frame: np.ndarray) -> FrameResult:
        """One frame in, one composited data URI plus all 478 landmarks out.

        Order matters and is fixed: detect on the FULL frame (so a face at the
        edge of the field of view is still found, it is simply not shown), draw,
        centre-crop to a square, downscale, and only then mirror. The flip is
        last so the overlay is already painted into the pixels and flips with
        them — no landmark coordinate is ever flipped. Any text drawn by a later
        feature must be drawn after the flip, or it renders backwards.
        """
        landmarks = self._detect(frame)
        canvas = frame.copy()
        if landmarks:
            _draw_overlay(canvas, landmarks)
        square = _centre_crop_square(canvas)
        preview = cv2.resize(
            square, (PREVIEW_PX, PREVIEW_PX), interpolation=cv2.INTER_AREA
        )
        mirrored = cv2.flip(preview, 1)
        # cv2.imencode raises cv2.error on a genuinely bad image rather than
        # returning False for a valid 3-channel uint8 frame, so the flag carries
        # no branch worth testing.
        _, buf = cv2.imencode(
            ".jpg", mirrored, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        )
        encoded = base64.b64encode(buf.tobytes()).decode("ascii")
        return FrameResult(data_uri=f"data:image/jpeg;base64,{encoded}", landmarks=landmarks)

    def _detect(self, frame: np.ndarray) -> list[Any]:
        landmarker = self._ensure_landmarker()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        # VIDEO mode is synchronous and deterministic (LIVE_STREAM would make
        # frame ordering nondeterministic and turn Gate tests flaky). It requires
        # monotonically increasing timestamps; the engine owns that counter.
        self._timestamp_ms += 1
        result = landmarker.detect_for_video(image, self._timestamp_ms)
        if not result.face_landmarks:
            return []
        return list(result.face_landmarks[0])

    def _ensure_landmarker(self) -> Any:
        if self.landmarker is None:
            self.landmarker = load_landmarker()
        return self.landmarker

    def _fail(self, message: str) -> None:
        self.status = FaceStatus.ERROR
        self.error_message = message
        return None


def pacing_delay(elapsed: float) -> float:
    """How long to wait before reading the next frame.

    Drop, never queue. A frame that overran its budget yields **zero** delay —
    the loop goes straight back to `read()` for the newest frame instead of
    buffering the ones it missed. A queueing pipeline does not merely run slow,
    it drifts: the preview falls further behind reality every frame, which reads
    as a freeze rather than as a low frame rate.
    """
    return max(0.0, FRAME_INTERVAL - elapsed)


def load_landmarker() -> FaceLandmarker:
    """Load the vendored bundle from a local path — no network, on any path."""
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=RunningMode.VIDEO,
    )
    return FaceLandmarker.create_from_options(options)


def _centre_crop_square(frame: np.ndarray) -> np.ndarray:
    """Crop to the largest centred square. The page masks it to a circle."""
    height, width = frame.shape[:2]
    side = min(height, width)
    x0 = (width - side) // 2
    y0 = (height - side) // 2
    return frame[y0 : y0 + side, x0 : x0 + side]


def _draw_overlay(canvas: np.ndarray, landmarks: list[Any]) -> None:
    """Draw the face ellipse and the landmark subset onto the full frame.

    An ellipse rather than the conventional rectangle because the preview is
    masked to a circle: a rectangle's corners clip when a face nears the edge.
    """
    height, width = canvas.shape[:2]
    points = [
        (int(round(lm.x * width)), int(round(lm.y * height))) for lm in landmarks
    ]
    oval = [points[i] for i in FACE_OVAL_POINTS]
    xs = [p[0] for p in oval]
    ys = [p[1] for p in oval]
    centre = ((min(xs) + max(xs)) // 2, (min(ys) + max(ys)) // 2)
    axes = (max(1, (max(xs) - min(xs)) // 2), max(1, (max(ys) - min(ys)) // 2))
    cv2.ellipse(canvas, centre, axes, 0, 0, 360, OVERLAY_COLOR, ELLIPSE_THICKNESS)
    for index in DRAWN_POINTS:
        cv2.circle(canvas, points[index], POINT_RADIUS, POINT_COLOR, -1)


def _camera_error_message(exc: BaseException) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    lowered = text.lower()
    if "permission" in lowered or "denied" in lowered:
        return "Camera permission denied"
    return "No camera available"

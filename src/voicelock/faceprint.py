"""Faceprint — face identity from a detected face via the vendored SFace model (F6).

Diagnostic only: compute a face embedding and a live match distance against a
stored reference face, colored accept / borderline / reject. No lock and no
key derivation — that is F7. Python owns all faceprint computation; the JS UI
only renders the result.

Unlike ``voiceprint.py``'s ``load_wav``, which refuses non-16kHz-mono audio
because ``capture.py`` pins the microphone to one format, camera frames
legitimately vary in resolution — there is no equivalent pin upstream of this
module. So this module CONVERTS rather than refuses: whatever frame size
arrives, it is resized/aligned/cropped as needed, never rejected with a
``ValueError`` on shape alone. Copying ``voiceprint.py``'s refuse-on-mismatch
pattern here would reject valid camera input.

The SFace ONNX weights are vendored under ``models/sface/`` and loaded fully
offline (a local file path, no runtime network). Detection and the five-point
alignment crop are computed with a SECOND, ``IMAGE``-mode ``FaceLandmarker``
instance loaded from the SAME vendored ``models/face_landmarker/`` bundle
``facedetect.py`` uses in ``VIDEO`` mode — a different instance because
``IMAGE`` mode is synchronous, stateless per call, and carries no tracker
state between unrelated frames, which is what a standalone frame/file needs
(``facedetect.py``'s ``VIDEO``-mode instance is for a genuine, continuous
camera stream and is not reused here).
"""

from __future__ import annotations

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

REFERENCE_TAKES = 3

# OpenCV's own published SFace operating point (cosine >= 0.363, L2 <= 1.128)
# is one operating point expressed in two metrics, not two independent bars:
# for unit-norm vectors, L2^2 == 2 * (1 - cosine), so L2 <= 1.128 and
# cosine >= 0.363 describe the same boundary. Q5 forbids deriving a second,
# repo-measured cutoff from just two comparisons, so both band edges are
# pinned to that one number rather than inventing a distinct REJECT value —
# the meter's borderline band has zero width in practice. compare() returns
# raw L2 distance (cv2's FR_NORM_L2), not cosine.
ACCEPT_CUTOFF = 1.128
REJECT_CUTOFF = 1.128

BAND_ACCEPT = "accept"
BAND_BORDERLINE = "borderline"
BAND_REJECT = "reject"

_MODEL_DIR = Path(__file__).resolve().parent / "models"
_SFACE_MODEL_PATH = _MODEL_DIR / "sface" / "face_recognition_sface_2021dec.onnx"
_LANDMARKER_MODEL_PATH = _MODEL_DIR / "face_landmarker" / "face_landmarker.task"

# Five-point YuNet-shaped row built from MediaPipe's 478 landmarks, per
# memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md: eye centres
# are the midpoint of each eye's outer+inner corner, nose tip and mouth
# corners are single indices. Order matters — confirmed empirically there,
# not assumed from naming — and must not be reordered.
_LEFT_EYE_CORNERS = (33, 133)
_RIGHT_EYE_CORNERS = (263, 362)
_NOSE_TIP = 4
_MOUTH_CORNERS = (61, 291)

# The recognizer's own aligned-crop size (SFace's training-time input).
_ALIGNED_SIZE = 112

# Lazily loaded, module-cached — loading either model is slow (~seconds).
_landmarker = None
_recognizer = None


class FaceprintError(Exception):
    """Base error for faceprint failures."""


class NoFaceError(FaceprintError):
    """No face was detected in the frame — Booth copy: 'no face detected'."""


class NoReferenceError(FaceprintError):
    """No reference faceprint on disk yet — Booth copy: set a reference first."""


def default_reference_path() -> Path:
    """Where the averaged reference faceprint lives (sibling of the vault)."""
    return Path.home() / ".voicelock" / "faceprint.ref"


def embed_frame(frame: np.ndarray) -> np.ndarray:
    """Return the SFace embedding for the largest detected face in ``frame``.

    ``frame`` is a BGR image array (as ``cv2.imread`` or a camera frame
    produces) at ANY resolution — this function resizes/aligns as needed and
    never raises on an unexpected frame size (see the module docstring for
    why, unlike ``voiceprint``, this converts rather than refuses).

    Raises ``NoFaceError`` if no face is detected. If more than one face is
    detected, the largest by landmark bounding-box area is used (Q6) — a
    camera frame catching a bystander should not silently swap identities.
    """
    landmarks = _detect_largest_face(frame)
    if landmarks is None:
        raise NoFaceError("no face detected")
    aligned = _align(frame, landmarks)
    recognizer = _ensure_recognizer()
    feature = recognizer.feature(aligned)
    return np.asarray(feature, dtype=np.float32).reshape(-1)


def embed_file(path: str | Path) -> np.ndarray:
    """Load an image file and return its face embedding (see ``embed_frame``)."""
    frame = cv2.imread(str(path))
    if frame is None:
        raise FaceprintError(f"{path}: could not be read as an image")
    return embed_frame(frame)


def set_reference(
    frames: list[np.ndarray], path: Path | None = None
) -> np.ndarray:
    """Average ``REFERENCE_TAKES`` per-frame embeddings into one reference.

    Each frame is embedded; the mean is persisted (plaintext, not in the
    vault). A frame with no face raises ``NoFaceError`` before anything is
    saved, so it is never averaged in.

    Honest asymmetry (Q4): three frames captured seconds apart are far more
    correlated than F3's three separately spoken sentences are — a blink or a
    momentary expression is the main thing this guards against, not the
    broader natural variation voice's three-take average buys.
    """
    if len(frames) != REFERENCE_TAKES:
        raise FaceprintError(
            f"need exactly {REFERENCE_TAKES} frames, got {len(frames)}"
        )
    embeddings = [embed_frame(frame) for frame in frames]  # raises on a faceless frame
    reference = np.mean(embeddings, axis=0).astype(np.float32)
    _save_reference(reference, path)
    return reference


def load_reference(path: Path | None = None) -> np.ndarray:
    """Load the stored reference faceprint, or raise ``NoReferenceError``."""
    ref_path = path if path is not None else default_reference_path()
    if not ref_path.is_file():
        raise NoReferenceError("no reference faceprint yet — set one first")
    with open(ref_path, "rb") as handle:
        vec = np.load(handle)
    return np.asarray(vec, dtype=np.float32)


def compare(a: np.ndarray, b: np.ndarray) -> float:
    """Return the raw L2 distance between two SFace embeddings.

    Lower is closer. ``ACCEPT_CUTOFF``/``REJECT_CUTOFF`` are the same value
    (decision recorded in ``plan.md`` 2026-07-27) — the meter has zero
    borderline width in practice.
    """
    recognizer = _ensure_recognizer()
    a = np.asarray(a, dtype=np.float32).reshape(1, -1)
    b = np.asarray(b, dtype=np.float32).reshape(1, -1)
    return float(recognizer.match(a, b, cv2.FaceRecognizerSF_FR_NORM_L2))


def band_for(distance: float) -> str:
    """Map an L2 distance to the accept / borderline / reject band."""
    if distance <= ACCEPT_CUTOFF:
        return BAND_ACCEPT
    if distance >= REJECT_CUTOFF:
        return BAND_REJECT
    return BAND_BORDERLINE


def _detect_largest_face(frame: np.ndarray) -> list[Any] | None:
    """Detect faces in ``frame`` and return the largest one's 478 landmarks.

    ``None`` when no face is found. Several faces are resolved by bounding-
    box area (Q6) rather than by taking whichever MediaPipe lists first —
    a bystander in frame must not silently become "the" face.
    """
    landmarker = _ensure_landmarker()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(image)  # IMAGE mode: synchronous, no timestamp
    if not result.face_landmarks:
        return None
    if len(result.face_landmarks) == 1:
        return list(result.face_landmarks[0])
    height, width = frame.shape[:2]
    return max(
        (list(face) for face in result.face_landmarks),
        key=lambda face: _bbox_area(face, width, height),
    )


def _bbox_area(landmarks: list[Any], width: int, height: int) -> float:
    xs = [lm.x * width for lm in landmarks]
    ys = [lm.y * height for lm in landmarks]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


def _align(frame: np.ndarray, landmarks: list[Any]) -> np.ndarray:
    """Build a YuNet-shaped 5-point row from MediaPipe landmarks and crop.

    Per memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md: eye
    centres are the midpoint of each eye's outer+inner corner (indices
    33/133 and 263/362), nose tip is index 4, mouth corners are 61 and 291.
    Confidence is hardcoded to 1.0 — SFace's ``alignCrop`` does not use it.
    Landmark coordinates are normalized 0..1; ``alignCrop`` expects pixels.
    """
    height, width = frame.shape[:2]

    def point(index: int) -> tuple[float, float]:
        lm = landmarks[index]
        return lm.x * width, lm.y * height

    def midpoint(i: int, j: int) -> tuple[float, float]:
        (x1, y1), (x2, y2) = point(i), point(j)
        return (x1 + x2) / 2, (y1 + y2) / 2

    left_eye = midpoint(*_LEFT_EYE_CORNERS)
    right_eye = midpoint(*_RIGHT_EYE_CORNERS)
    nose = point(_NOSE_TIP)
    mouth_left = point(_MOUTH_CORNERS[0])
    mouth_right = point(_MOUTH_CORNERS[1])

    xs = [lm.x * width for lm in landmarks]
    ys = [lm.y * height for lm in landmarks]
    face_box = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))

    row = np.array(
        [[*face_box, *left_eye, *right_eye, *nose, *mouth_left, *mouth_right, 1.0]],
        dtype=np.float32,
    )
    recognizer = _ensure_recognizer()
    return recognizer.alignCrop(frame, row)


def _ensure_landmarker() -> FaceLandmarker:
    global _landmarker
    if _landmarker is None:
        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(_LANDMARKER_MODEL_PATH)),
            running_mode=RunningMode.IMAGE,
        )
        _landmarker = FaceLandmarker.create_from_options(options)
    return _landmarker


def _ensure_recognizer() -> Any:
    global _recognizer
    if _recognizer is None:
        _recognizer = cv2.FaceRecognizerSF.create(str(_SFACE_MODEL_PATH), "")
    return _recognizer


def _save_reference(reference: np.ndarray, path: Path | None = None) -> None:
    ref_path = path if path is not None else default_reference_path()
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ref_path, "wb") as handle:
        np.save(handle, np.asarray(reference, dtype=np.float32))

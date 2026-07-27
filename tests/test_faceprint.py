"""Faceprint engine tests — spec F6 §5 cases.

Uses the committed fixtures under ``fixtures/face`` and the vendored SFace +
Face Landmarker models loaded fully offline. Cutoff assertions import the
same module constants the app uses, so the band a distance falls into is
deterministic, not a judgment call.
"""

from __future__ import annotations

import socket
import types
from pathlib import Path

import cv2
import numpy as np
import pytest

import voicelock.faceprint as fp
from voicelock.faceprint import (
    ACCEPT_CUTOFF,
    BAND_ACCEPT,
    BAND_BORDERLINE,
    BAND_REJECT,
    REJECT_CUTOFF,
    NoFaceError,
    NoReferenceError,
    band_for,
    compare,
    default_reference_path,
    embed_file,
    embed_frame,
    set_reference,
)

FIXTURES = Path(__file__).parent / "fixtures" / "face"


@pytest.fixture(scope="module")
def person_a_1() -> np.ndarray:
    return embed_file(FIXTURES / "personA_1.jpg")


@pytest.fixture(scope="module")
def person_a_2() -> np.ndarray:
    return embed_file(FIXTURES / "personA_2.jpg")


@pytest.fixture(scope="module")
def person_b() -> np.ndarray:
    return embed_file(FIXTURES / "personB.jpg")


def test_default_reference_path() -> None:
    assert default_reference_path() == Path.home() / ".voicelock" / "faceprint.ref"


# --- same face close, different face far (spec §5 cmd 3, also pinned as a
#     permanent regression test rather than only a one-off Gate command) -----
def test_same_face_close_different_face_far(
    person_a_1: np.ndarray, person_a_2: np.ndarray, person_b: np.ndarray
) -> None:
    d_same = compare(person_a_1, person_a_2)
    d_diff_1 = compare(person_a_1, person_b)
    d_diff_2 = compare(person_a_2, person_b)
    assert d_same <= ACCEPT_CUTOFF
    assert d_diff_1 >= REJECT_CUTOFF
    assert d_diff_2 >= REJECT_CUTOFF


def test_set_reference_then_compare_via_band(
    tmp_path: Path, person_a_1: np.ndarray
) -> None:
    ref = tmp_path / "faceprint.ref"
    frame = cv2.imread(str(FIXTURES / "personA_1.jpg"))
    set_reference([frame, frame, frame], path=ref)
    distance = compare(fp.load_reference(ref), person_a_1)
    assert band_for(distance) == BAND_ACCEPT


# --- set_reference: exactly REFERENCE_TAKES frames, averaged ------------------
def test_set_reference_wrong_take_count_raises(tmp_path: Path) -> None:
    frame = cv2.imread(str(FIXTURES / "personA_1.jpg"))
    with pytest.raises(fp.FaceprintError):
        set_reference([frame, frame], path=tmp_path / "faceprint.ref")


def test_set_reference_rejects_faceless_frame_without_saving(tmp_path: Path) -> None:
    ref = tmp_path / "faceprint.ref"
    real = cv2.imread(str(FIXTURES / "personA_1.jpg"))
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    with pytest.raises(NoFaceError):
        set_reference([real, blank, real], path=ref)
    assert not ref.exists()  # nothing persisted -- the faceless frame was not averaged in


def test_embed_frame_rejects_blank_frame() -> None:
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    with pytest.raises(NoFaceError):
        embed_frame(blank)


# --- compare with no reference surfaces a set-reference-first signal ----------
def test_compare_without_reference(tmp_path: Path) -> None:
    with pytest.raises(NoReferenceError):
        fp.load_reference(tmp_path / "missing.ref")


# --- embed_file on a path that isn't a readable image -------------------------
def test_embed_file_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(fp.FaceprintError):
        embed_file(tmp_path / "does_not_exist.jpg")


def test_embed_file_corrupt_image_raises(tmp_path: Path) -> None:
    bad = tmp_path / "not_an_image.jpg"
    bad.write_bytes(b"this is not image data")
    with pytest.raises(fp.FaceprintError):
        embed_file(bad)


def test_band_for_boundaries() -> None:
    # ACCEPT_CUTOFF == REJECT_CUTOFF by decision (2026-07-27) -- the boundary
    # value itself resolves to accept (<=), and anything above is reject.
    assert ACCEPT_CUTOFF == REJECT_CUTOFF
    assert band_for(ACCEPT_CUTOFF) == BAND_ACCEPT
    assert band_for(ACCEPT_CUTOFF + 0.001) == BAND_REJECT
    assert band_for(0.0) == BAND_ACCEPT


def test_band_for_never_returns_borderline_at_this_cutoff() -> None:
    # With ACCEPT_CUTOFF == REJECT_CUTOFF, the borderline band has zero width
    # in practice -- documented in the module, pinned here as a regression.
    assert BAND_BORDERLINE not in (band_for(ACCEPT_CUTOFF - 0.5), band_for(ACCEPT_CUTOFF + 0.5))


# --- several faces: the largest by bounding-box area wins (Q6) ----------------
def test_several_faces_picks_largest_by_bbox_area(monkeypatch: pytest.MonkeyPatch) -> None:
    def make_face(cx: float, cy: float, half: float) -> list[types.SimpleNamespace]:
        # A minimal square ring of points is enough to give _bbox_area a real
        # min/max span; only x/y are read.
        return [
            types.SimpleNamespace(x=cx - half, y=cy - half),
            types.SimpleNamespace(x=cx + half, y=cy - half),
            types.SimpleNamespace(x=cx - half, y=cy + half),
            types.SimpleNamespace(x=cx + half, y=cy + half),
        ]

    small_face = make_face(0.3, 0.3, 0.05)
    large_face = make_face(0.6, 0.6, 0.3)

    class StubResult:
        face_landmarks = [small_face, large_face]

    class StubLandmarker:
        def detect(self, image: object) -> StubResult:
            return StubResult()

    monkeypatch.setattr(fp, "_landmarker", StubLandmarker())
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    picked = fp._detect_largest_face(frame)
    assert picked == large_face


def test_no_face_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    class StubResult:
        face_landmarks: list[object] = []

    class StubLandmarker:
        def detect(self, image: object) -> StubResult:
            return StubResult()

    monkeypatch.setattr(fp, "_landmarker", StubLandmarker())
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    assert fp._detect_largest_face(frame) is None


# --- the model loads from the vendored local path with no network -------------
def test_faceprint_loads_offline_from_vendored_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(fp, "_landmarker", None)
    monkeypatch.setattr(fp, "_recognizer", None)

    def _blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted during offline model load")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)  # any real fetch resolves DNS first

    assert fp._SFACE_MODEL_PATH.is_file()
    assert fp._LANDMARKER_MODEL_PATH.is_file()
    vector = embed_file(FIXTURES / "personA_1.jpg")  # triggers both offline loads
    assert vector.shape[0] > 0


# --- the match test genuinely depends on the face model, not on the assertion
#     being trivially satisfiable (F6's version of F5.5 §5 cmd 4) -------------
def test_dummy_embedder_fails_to_separate_mutation_check() -> None:
    """A mean-pixel-value embedder, with zero face modelling, must NOT
    separate personA_1/personA_2 from personB at the pinned cutoffs -- if it
    did, the real test's pass would prove nothing about the SFace model.
    """

    def dummy_embed(path: Path) -> np.ndarray:
        img = cv2.imread(str(path))
        # Mean BGR pixel value, tiled to look like a feature vector. No face
        # detection, no alignment, no learned representation at all.
        mean_pixel = img.reshape(-1, 3).mean(axis=0).astype(np.float32)
        return np.tile(mean_pixel, 43)[:128]  # arbitrary vector, same dim as SFace's

    def dummy_l2(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.linalg.norm(a.astype(np.float64) - b.astype(np.float64)))

    a1 = dummy_embed(FIXTURES / "personA_1.jpg")
    a2 = dummy_embed(FIXTURES / "personA_2.jpg")
    b = dummy_embed(FIXTURES / "personB.jpg")

    d_same = dummy_l2(a1, a2)
    d_diff_1 = dummy_l2(a1, b)
    d_diff_2 = dummy_l2(a2, b)

    # The dummy must FAIL to reproduce the real separation -- at least one of
    # the "different person" pairs must NOT clear REJECT_CUTOFF while ALSO
    # keeping the same-person pair inside ACCEPT_CUTOFF. If a mean-pixel
    # embedder could do that too, this fixture pair would prove nothing.
    real_style_pass = (
        d_same <= ACCEPT_CUTOFF and d_diff_1 >= REJECT_CUTOFF and d_diff_2 >= REJECT_CUTOFF
    )
    assert not real_style_pass, (
        "a dummy embedder with no face modelling still separates the fixtures "
        f"(same={d_same}, diff1={d_diff_1}, diff2={d_diff_2}) -- "
        "the real test has no teeth"
    )

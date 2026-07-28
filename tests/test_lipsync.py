"""Lip-sync tests — spec F8 §5 cmd 2.

Per Q5, no real video fixture exists in this repo, so the scoring math is
proven with a REAL audio envelope (from an existing voice fixture) paired
with SYNTHETIC mouth-aperture series built to a known relationship — this
proves the correlation math, not that it works on a real face's real video
(the required live manual check, spec §5 cmd 4, is what does that).

The envelope-construction helper below is test-local, not part of
``lipsync.py``'s public surface — Task 3 (the Booth bridge) owns the real,
production envelope construction from a live capture's PCM buffer.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from voicelock import facedetect
from voicelock.lipsync import LAG_WINDOW, SYNC_THRESHOLD, is_live, mouth_aperture, score
from voicelock.voiceprint import SAMPLE_RATE, load_wav

FIXTURES = Path(__file__).parent / "fixtures" / "voiceprint"

# Matches Task 3's real construction (plan.md decision 5): a fixed hop equal
# to one video frame interval, so the envelope lands on the same per-frame
# grid a live mouth-aperture series would.
_HOP = int(SAMPLE_RATE * facedetect.FRAME_INTERVAL)


def _envelope(audio: np.ndarray, hop: int) -> np.ndarray:
    """Fixed-window RMS envelope — the same technique the Visualizer uses."""
    n = audio.size // hop
    return np.array(
        [
            float(np.sqrt(np.mean(np.square(audio[i * hop : (i + 1) * hop], dtype=np.float64))))
            for i in range(n)
        ]
    )


def _shift_no_wrap(x: np.ndarray, shift: int) -> np.ndarray:
    """Non-circular shift, padded with the series' own mean (not zero)."""
    pad_value = x.mean()
    return np.concatenate([np.full(shift, pad_value), x[:-shift]])


@pytest.fixture(scope="module")
def real_envelope() -> np.ndarray:
    audio = load_wav(FIXTURES / "speakerA_live.wav")
    return _envelope(audio, _HOP)


# --- case: in-phase synthetic series scores above SYNC_THRESHOLD -------------
def test_in_phase_series_scores_above_threshold(real_envelope: np.ndarray) -> None:
    """A monotonic (here, affine) transform of the real envelope — max sync."""
    in_phase = real_envelope * 2.0 + 0.1
    result = score(in_phase, real_envelope)
    assert result > SYNC_THRESHOLD
    assert is_live(result) is True


# --- case: a shift INSIDE the lag window still scores above SYNC_THRESHOLD --
def test_shift_inside_lag_window_still_scores_above_threshold(
    real_envelope: np.ndarray,
) -> None:
    """Exercises the lag-search itself, not just the shift=0 case.

    A 4-frame shift is well inside ``LAG_WINDOW = 5``: the true (windowed)
    score finds the aligning lag and scores ~1.0, but a lag-0-only
    correlation on this same pair scores ~-0.06 (below threshold) — so this
    assertion can only pass if the search over lags actually runs, unlike
    the shift=0 in-phase case above, which passes even with the loop
    collapsed to lag=0.
    """
    in_phase = real_envelope * 2.0 + 0.1
    shifted = _shift_no_wrap(in_phase, shift=4)
    result = score(shifted, real_envelope)
    assert result > SYNC_THRESHOLD
    assert is_live(result) is True


# --- case: shifted outside the lag window scores below SYNC_THRESHOLD --------
def test_shifted_series_scores_below_threshold(real_envelope: np.ndarray) -> None:
    """Shifted 15 frames — 3x past LAG_WINDOW=5 — the direct analog of a
    dubbed/desynced clip."""
    in_phase = real_envelope * 2.0 + 0.1
    shifted = _shift_no_wrap(in_phase, shift=15)
    result = score(shifted, real_envelope)
    assert result < SYNC_THRESHOLD
    assert is_live(result) is False


# --- case: a flat (non-moving) series scores below SYNC_THRESHOLD ------------
def test_flat_series_scores_below_threshold(real_envelope: np.ndarray) -> None:
    """A still photo or a muted video: the mouth never moves."""
    flat = np.full(real_envelope.size, 0.5)
    result = score(flat, real_envelope)
    assert result < SYNC_THRESHOLD
    assert is_live(result) is False
    assert result == 0.0  # zero variance -> undefined correlation, defined as 0


# --- case: the constants are named and disclosed -----------------------------
def test_constants_are_named_and_sane() -> None:
    assert LAG_WINDOW > 0
    assert 0.0 < SYNC_THRESHOLD < 1.0

    import voicelock.lipsync as lipsync_module

    docstring = lipsync_module.__doc__.lower()
    assert "synthetic" in docstring
    assert "not" in docstring and "real human lip-sync data" in docstring


# --- case: score() tolerates mismatched lengths without raising --------------
def test_score_compares_over_the_shorter_length(real_envelope: np.ndarray) -> None:
    in_phase = real_envelope * 2.0 + 0.1
    shorter = in_phase[:-5]
    result = score(shorter, real_envelope)
    assert result > SYNC_THRESHOLD  # still in-phase over the overlapping range


# --- case: mouth_aperture() — normalized vertical inner-lip gap --------------
def _landmarks_with(upper_y: float, lower_y: float) -> list[SimpleNamespace]:
    """478 fake landmarks; only the indices mouth_aperture() reads are set
    to meaningful values, the rest are neutral placeholders."""
    points = [SimpleNamespace(x=0.5, y=0.5) for _ in range(478)]
    points[13] = SimpleNamespace(x=0.5, y=upper_y)  # inner upper lip
    points[14] = SimpleNamespace(x=0.5, y=lower_y)  # inner lower lip
    points[33] = SimpleNamespace(x=0.35, y=0.4)  # right-eye outer corner
    points[133] = SimpleNamespace(x=0.45, y=0.4)  # right-eye inner corner
    points[263] = SimpleNamespace(x=0.55, y=0.4)  # left-eye inner corner
    points[362] = SimpleNamespace(x=0.65, y=0.4)  # left-eye outer corner
    return points


def test_mouth_aperture_is_the_normalized_inner_lip_gap() -> None:
    landmarks = _landmarks_with(upper_y=0.45, lower_y=0.55)
    # inter-eye distance: midpoints (0.40, 0.4) and (0.60, 0.4) -> 0.20
    # lip gap: |0.55 - 0.45| = 0.10 -> ratio 0.5
    assert mouth_aperture(landmarks) == pytest.approx(0.5)


def test_mouth_aperture_increases_with_a_wider_gap() -> None:
    closed = mouth_aperture(_landmarks_with(upper_y=0.499, lower_y=0.501))
    open_wide = mouth_aperture(_landmarks_with(upper_y=0.40, lower_y=0.60))
    assert open_wide > closed


def test_mouth_aperture_handles_a_degenerate_zero_reference() -> None:
    landmarks = _landmarks_with(upper_y=0.45, lower_y=0.55)
    for index in (33, 133, 263, 362):
        landmarks[index] = SimpleNamespace(x=0.5, y=0.4)  # all eye points coincide
    assert mouth_aperture(landmarks) == 0.0

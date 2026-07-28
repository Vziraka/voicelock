"""Lip-sync — the second liveness signal: do the lips move with the audio (F8).

Per-frame mouth aperture (from F5's face landmarks) correlated against the
audio envelope over a small lag window, since mouth movement may lead or
trail the audio slightly. Pure numpy, no new dependency — the same hand-
rolled, glass-box approach F4/F7 used for fuzzy commitment.

``score()`` assumes both series already share one sample grid (index *i* in
each is the same instant) — aligning a live capture's mouth-aperture series
and audio envelope onto that grid is the caller's job (F8 Task 3), not this
module's; see ``plan.md``'s Task 3 notes for the exact construction.

**Disclosure (spec §5 item 2's own requirement):** ``SYNC_THRESHOLD`` and
``LAG_WINDOW`` are pinned from THIS module's own synthetic separation
(measured against a real audio envelope from an existing voice fixture,
paired with a synthetic mouth-aperture series built directly from that same
envelope) — not from real human lip-sync data, because this repo has none.
Measured on ``speakerA_live.wav`` (58 envelope frames at the video frame
hop): an in-phase series (a monotonic — here, affine — transform of the
audio envelope) scores ``1.0``; the same series shifted 15 frames outside
the ``LAG_WINDOW = 5`` window scores ``-0.007``; a flat (non-moving) series
scores ``0.0`` by construction (zero variance, so the correlation is
undefined and defined here as 0 rather than NaN). ``SYNC_THRESHOLD = 0.5``
is the midpoint between the in-phase score and that negative-class ceiling.
The required live manual check (spec §5 cmd 4) is what actually exercises
real synchrony.
"""

from __future__ import annotations

from typing import Any

import numpy as np

# Confirmed against MediaPipe's own published Face Mesh topology (the inner
# lip ring's edges: ...(82,13),(13,312)... on top and ...(87,14),(14,317)...
# on the bottom — 13 and 14 sit at the vertical centre of the inner lip,
# symmetric between the two corners), not assumed from index naming — same
# care F7 took confirming SFace's embedding width before importing it.
_UPPER_INNER_LIP = 13
_LOWER_INNER_LIP = 14

# Face-scale reference: inter-eye distance, the same eye-corner indices
# faceprint.py already uses for its own alignment (33/133 and 263/362).
_LEFT_EYE_CORNERS = (33, 133)
_RIGHT_EYE_CORNERS = (263, 362)

# +/- frames on the caller's shared per-frame grid (Task 3 builds that grid
# at facedetect.FRAME_INTERVAL, so +/-5 frames there is roughly +/-167 ms of
# lead/trail tolerance). See the module docstring for how this was measured.
LAG_WINDOW = 5
SYNC_THRESHOLD = 0.5


def mouth_aperture(landmarks: list[Any]) -> float:
    """One scalar: inner-lip vertical gap, normalized by inter-eye distance.

    Reads MediaPipe's normalized (0..1, image-relative) landmark coordinates
    directly — no pixel conversion, unlike ``faceprint.py``'s alignment code,
    because the result only ever feeds ``score()``'s Pearson correlation,
    which is invariant to the constant multiplicative bias an uncorrected
    aspect ratio would otherwise introduce (capture is a fixed 640x480 for
    the whole session, so the bias is constant, not frame-varying).

    Assumes ``landmarks`` is a valid, non-empty 478-point detection (the
    caller's job to skip a faceless frame — this function does not handle
    an empty list).
    """

    def point(index: int) -> np.ndarray:
        lm = landmarks[index]
        return np.array([lm.x, lm.y], dtype=np.float64)

    def midpoint(indices: tuple[int, int]) -> np.ndarray:
        a, b = indices
        return (point(a) + point(b)) / 2.0

    gap = np.linalg.norm(point(_UPPER_INNER_LIP) - point(_LOWER_INNER_LIP))
    left_eye = midpoint(_LEFT_EYE_CORNERS)
    right_eye = midpoint(_RIGHT_EYE_CORNERS)
    reference = float(np.linalg.norm(right_eye - left_eye))
    if reference == 0.0:
        return 0.0
    return float(gap / reference)


def score(
    mouth_series: np.ndarray, audio_envelope: np.ndarray, lag_window: int = LAG_WINDOW
) -> float:
    """Peak normalized cross-correlation between the two series, lag-windowed.

    Both arrays are assumed already on the same sample grid (index *i* in
    each is the same instant) — see the module docstring. If they arrive at
    slightly different lengths, the comparison runs over the shorter
    length rather than raising (a real capture's frame count is not
    perfectly deterministic under drop-don't-queue pacing).

    Returns the highest Pearson correlation found across lags in
    ``[-lag_window, +lag_window]``. A lag ``l >= 0`` compares
    ``mouth_series`` shifted forward by ``l`` samples against
    ``audio_envelope`` (mouth trailing audio); negative ``l`` is the
    reverse (mouth leading audio).
    """
    x = np.asarray(mouth_series, dtype=np.float64).reshape(-1)
    y = np.asarray(audio_envelope, dtype=np.float64).reshape(-1)
    n = min(x.size, y.size)
    x, y = x[:n], y[:n]

    best = -1.0
    for lag in range(-lag_window, lag_window + 1):
        if lag >= 0:
            xa, ya = x[lag:], y[: n - lag]
        else:
            xa, ya = x[: n + lag], y[-lag:]
        if xa.size < 2:
            continue
        best = max(best, _pearson(xa, ya))
    return best


def is_live(sync_score: float) -> bool:
    """Whether a ``score()`` result clears ``SYNC_THRESHOLD``."""
    return sync_score >= SYNC_THRESHOLD


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    a = a - a.mean()
    b = b - b.mean()
    denom = float(np.sqrt(np.sum(a * a) * np.sum(b * b)))
    if denom == 0.0:  # a flat series has zero variance — undefined, treated as 0
        return 0.0
    return float(np.dot(a, b) / denom)

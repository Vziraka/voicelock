"""Voiceprint — speaker identity from speech via the vendored ECAPA model (F3).

Diagnostic only: compute a speaker embedding and a live match distance against a
stored reference voiceprint, colored accept / borderline / reject. No lock and no
key derivation — that is F4. Python owns all voiceprint DSP; the JS UI only
renders the result.

The ECAPA-TDNN weights are vendored under ``models/ecapa/`` and loaded fully
offline (``HF_HUB_OFFLINE=1``, no runtime network).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16_000
EMBEDDING_DIM = 192

# A "Set reference" records this many separate short sentences and averages them.
REFERENCE_TAKES = 3

# A take shorter than this, or near-silent, cannot yield a stable voiceprint.
MIN_SPEECH_SECONDS = 0.4
MIN_RMS = 5e-4

# Cosine-distance three-band cutoffs. Tuned empirically on
# ``tests/fixtures/voiceprint`` with the vendored ECAPA model (same-speaker
# distances clustered at/under ~0.29, a different speaker at ~0.83) and pinned
# here as the single source both the app and the tests import — so the band a
# distance falls into is deterministic, not a judgment call.
ACCEPT_CUTOFF = 0.45  # distance <= this -> accept (green)
REJECT_CUTOFF = 0.65  # distance >= this -> reject (red); between -> borderline (amber)

BAND_ACCEPT = "accept"
BAND_BORDERLINE = "borderline"
BAND_REJECT = "reject"

_MODEL_DIR = Path(__file__).resolve().parent / "models" / "ecapa"

# The loaded ECAPA classifier is cached module-level — loading is slow (~seconds).
_classifier = None


class VoiceprintError(Exception):
    """Base error for voiceprint failures."""


class NeedMoreAudioError(VoiceprintError):
    """A take was too short or too quiet to embed — Booth copy: 'need more audio'."""


class NoReferenceError(VoiceprintError):
    """No reference voiceprint on disk yet — Booth copy: set a reference first."""


def default_reference_path() -> Path:
    """Where the averaged reference voiceprint lives (sibling of the vault)."""
    return Path.home() / ".voicelock" / "voiceprint.ref"


def embed(audio: np.ndarray) -> np.ndarray:
    """Return the L2-normalized ECAPA speaker embedding for mono PCM audio.

    The audio is expected at ``SAMPLE_RATE`` — the only two sources are
    ``capture.py``, which pins the microphone there, and ``load_wav``, which
    refuses anything else.

    Raises ``NeedMoreAudioError`` when the clip is too short or near-silent.
    """
    sig = np.asarray(audio, dtype=np.float32).reshape(-1)
    if sig.size < int(MIN_SPEECH_SECONDS * SAMPLE_RATE) or _rms(sig) < MIN_RMS:
        raise NeedMoreAudioError("need more audio")

    import torch

    classifier = _load_classifier()
    tensor = torch.from_numpy(sig).unsqueeze(0)
    with torch.no_grad():
        vec = classifier.encode_batch(tensor).squeeze().cpu().numpy()
    return _normalize(vec)


def set_reference(
    takes: list[np.ndarray], path: Path | None = None
) -> np.ndarray:
    """Average ``REFERENCE_TAKES`` per-utterance embeddings into one reference.

    Each take is embedded and L2-normalized; the mean is re-normalized and
    persisted (plaintext, not in the vault). A take that is too short or silent
    raises ``NeedMoreAudioError`` before anything is saved — so it is never
    averaged in, and the caller re-records just that take.
    """
    if len(takes) != REFERENCE_TAKES:
        raise VoiceprintError(
            f"need exactly {REFERENCE_TAKES} takes, got {len(takes)}"
        )
    embeddings = [embed(take) for take in takes]  # raises on a short/silent take
    reference = _normalize(np.mean(embeddings, axis=0))
    _save_reference(reference, path)
    return reference


def load_reference(path: Path | None = None) -> np.ndarray:
    """Load the stored reference voiceprint, or raise ``NoReferenceError``."""
    ref_path = path if path is not None else default_reference_path()
    if not ref_path.is_file():
        raise NoReferenceError("no reference voiceprint yet — set one first")
    with open(ref_path, "rb") as handle:
        vec = np.load(handle)
    return _normalize(vec)


def compare(live_audio: np.ndarray, path: Path | None = None) -> tuple[float, str]:
    """Return ``(distance, band)`` of live audio against the stored reference.

    Raises ``NoReferenceError`` if no reference is set, ``NeedMoreAudioError`` if
    the live clip is too short/silent.
    """
    reference = load_reference(path)  # checked first, so no-reference is cheap
    live = embed(live_audio)
    distance = cosine_distance(reference, live)
    return distance, band_for(distance)


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine distance (``1 - cosine similarity``) between two embeddings."""
    a = np.asarray(a, dtype=np.float64).reshape(-1)
    b = np.asarray(b, dtype=np.float64).reshape(-1)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        raise VoiceprintError("cannot compare a zero-length embedding")
    return float(1.0 - np.dot(a, b) / denom)


def band_for(distance: float) -> str:
    """Map a cosine distance to the accept / borderline / reject band."""
    if distance <= ACCEPT_CUTOFF:
        return BAND_ACCEPT
    if distance >= REJECT_CUTOFF:
        return BAND_REJECT
    return BAND_BORDERLINE


def load_wav(path: Path) -> np.ndarray:
    """Decode a mono 16 kHz float32 signal from a WAV/FLAC file (offline).

    Raises ``ValueError``, naming the offending value, for audio that is not
    already mono at ``SAMPLE_RATE`` — such a file is malformed, not a variant.
    """
    import soundfile as sf

    data, sr = sf.read(str(path), dtype="float32", always_2d=False)
    data = np.asarray(data, dtype=np.float32)
    # Refusing instead of converting is correct HERE only because capture.py
    # pins the one real audio source to CHANNELS = 1 at SAMPLE_RATE = 16 kHz,
    # so anything else reaching this loader is a defect worth surfacing rather
    # than a variant worth silently repairing. A source WITHOUT such a pin —
    # camera frames, whose resolution legitimately varies — must convert rather
    # than refuse; do not copy this pattern there.
    if sr != SAMPLE_RATE:  # capture.py pins the rate, so a mismatch is a defect
        raise ValueError(f"{path}: expected {SAMPLE_RATE} Hz audio, got {sr} Hz")
    if data.ndim != 1:  # capture.py pins CHANNELS = 1, so extra channels likewise
        raise ValueError(
            f"{path}: expected mono audio, got {data.shape[1]} channels"
        )
    return data


def _load_classifier():
    """Load the vendored ECAPA model once, fully offline, and cache it."""
    global _classifier
    if _classifier is not None:
        return _classifier

    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from speechbrain.inference.speaker import EncoderClassifier
    from speechbrain.utils.fetching import LocalStrategy

    savedir = Path(tempfile.gettempdir()) / "voicelock_ecapa_cache"
    # source + pretrained_path both point at the vendored dir, and NO_LINK reads
    # the files in place (Windows blocks the default symlink), so the load never
    # touches the network or the HF cache.
    _classifier = EncoderClassifier.from_hparams(
        source=str(_MODEL_DIR),
        savedir=str(savedir),
        run_opts={"device": "cpu"},
        overrides={"pretrained_path": str(_MODEL_DIR)},
        local_strategy=LocalStrategy.NO_LINK,
    )
    return _classifier


def _normalize(vec: np.ndarray) -> np.ndarray:
    vec = np.asarray(vec, dtype=np.float64).reshape(-1)
    norm = float(np.linalg.norm(vec))
    if norm == 0.0:
        raise VoiceprintError("degenerate (zero) embedding")
    return vec / norm


def _rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))


def _save_reference(reference: np.ndarray, path: Path | None = None) -> None:
    ref_path = path if path is not None else default_reference_path()
    ref_path.parent.mkdir(parents=True, exist_ok=True)
    with open(ref_path, "wb") as handle:
        np.save(handle, np.asarray(reference, dtype=np.float64))

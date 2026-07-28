"""Challenge — spoken-word liveness check via the vendored Vosk model (F8).

The first of two new liveness signals: does the attempt SAY the challenge
phrase currently on screen? Defeats a pre-recorded clip saying different
words, or silence. Voice/face identity and lip-sync are separate checks
(``voiceprint.py``/``faceprint.py``/``lipsync.py``) — this module only
decides whether the recognized words match the challenge.

Vosk's grammar-constrained recognition (``KaldiRecognizer(model, rate,
grammar_json)``) decodes directly against a small JSON list of allowed
phrases, so there is no open-vocabulary transcription step and no separate
fuzzy text-match step — matching the pool IS the decoding constraint. The
``vosk-model-small-en-us-0.15`` weights are vendored under
``models/vosk/`` and loaded fully offline (a local path, no runtime
network).

``CHALLENGE_PHRASES`` is a small, hand-authored pool (own words, not sourced
text, per spec Q3) — bounded on purpose, since the exact phrase set is what
gets passed as Vosk's grammar constraint; an unbounded or generated pool
would not fit that constraint as cleanly.
"""

from __future__ import annotations

import json
import re
import string
from pathlib import Path
from random import Random

import numpy as np
import vosk

# capture.py pins the microphone to this rate; duplicated here rather than
# imported, matching voiceprint.py's own local SAMPLE_RATE constant — every
# module that touches raw PCM pins its own copy rather than cross-importing.
SAMPLE_RATE = 16_000

# ~10-20 short, phonetically varied, hand-authored sentences (Q3) — own
# words, not sourced text, mirroring F4/F7's precedent of disclosed literal
# constants. This is the pool Vosk's grammar is built from, so its size is a
# real cost: too large widens what a single utterance could be confused for.
CHALLENGE_PHRASES: tuple[str, ...] = (
    "open the blue door now",
    "silver clouds drift over mountains",
    "my dog runs fast in rain",
    "purple frogs jump near rivers",
    "the kitchen smells like fresh bread",
    "six sailors sang songs at sea",
    "golden leaves fall in autumn",
    "quiet rivers flow past old towns",
    "bright stars shine above the desert",
    "tall trees sway in the wind",
    "fresh coffee brews every morning",
    "wild horses run across the plain",
)

_MODEL_PATH = (
    Path(__file__).resolve().parent
    / "models"
    / "vosk"
    / "vosk-model-small-en-us-0.15"
)

# Loading the model is slow (~seconds) — module-cached like
# voiceprint._load_classifier and faceprint._ensure_recognizer.
_model: vosk.Model | None = None

_PUNCTUATION_TABLE = str.maketrans("", "", string.punctuation)


def pick_challenge(
    previous: str | None = None, rng: Random | None = None
) -> str:
    """Pick a challenge phrase uniformly at random from the pool.

    Excludes ``previous`` from the draw (no-immediate-repeat, Q3) unless the
    pool has only one entry. ``rng`` is injectable (mirrors ``open_camera``/
    ``clock``/``landmarker`` elsewhere in this repo) so the no-repeat
    property is deterministically testable over many draws.
    """
    rng = rng if rng is not None else Random()
    pool = CHALLENGE_PHRASES
    if previous is not None and len(pool) > 1:
        pool = tuple(phrase for phrase in pool if phrase != previous)
    return rng.choice(pool)


def matches(recognized: str, challenge: str) -> bool:
    """Compare recognized text against the challenge phrase.

    Normalizes by lowercasing and stripping punctuation only — no stemming
    or fuzzy edit distance (Q3/Q4 both describe exact-pool matching).
    """
    return _normalize(recognized) == _normalize(challenge)


def check(
    audio: np.ndarray,
    challenge: str,
    decoys: tuple[str, ...] | list[str] = CHALLENGE_PHRASES,
) -> bool:
    """Return whether ``audio`` was recognized as saying ``challenge``.

    Builds a Vosk grammar from ``challenge`` plus ``decoys`` (the rest of the
    pool, per Q3) so the recognizer decodes against the closed set of things
    the speaker could plausibly be asked to say, plus Vosk's catch-all
    ``[unk]`` token for anything else. ``audio`` is this repo's standard
    float32 mono PCM at ``SAMPLE_RATE`` (``capture.pcm_buffer()``'s format);
    converted to the int16 bytes Vosk's API expects — no resampling needed
    since capture is already 16 kHz mono, the rate this model expects.
    """
    model = _ensure_model()
    phrases = list(dict.fromkeys([challenge, *decoys]))  # dedupe, keep order
    grammar = json.dumps([*phrases, "[unk]"])
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE, grammar)
    recognizer.AcceptWaveform(_to_pcm16(audio))
    result = json.loads(recognizer.FinalResult())
    return matches(result.get("text", ""), challenge)


def _to_pcm16(audio: np.ndarray) -> bytes:
    sig = np.asarray(audio, dtype=np.float32).reshape(-1)
    return (np.clip(sig, -1.0, 1.0) * 32767).astype(np.int16).tobytes()


def _normalize(text: str) -> str:
    stripped = text.translate(_PUNCTUATION_TABLE).lower()
    return re.sub(r"\s+", " ", stripped).strip()


def _ensure_model() -> vosk.Model:
    global _model
    if _model is None:
        vosk.SetLogLevel(-1)  # Kaldi logs to stderr by default; silence it
        _model = vosk.Model(str(_MODEL_PATH))
    return _model

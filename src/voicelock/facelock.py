"""Inner lock — a stable key bound to the enrolled faceprint (F7).

The same hand-rolled **code-offset fuzzy commitment** (Juels-Wattenberg, 1999)
as ``middlelock.py``, reparameterized for SFace's 128-dim face embedding
instead of ECAPA's 192-dim voice embedding — one lock layer deeper, for the
face instead of the voice. It turns the noisy faceprint into a stable secret
plus non-secret **helper data**, so the enrolled person recovers the same
secret while a different face does not.

Pipeline (identical shape to ``middlelock.py`` — see that module for the full
rationale of each step): binarize + expand via a seeded LSH projection, keep
the most reliable bits (cross-take sign unanimity, margin as tiebreak), decode
a repetition code with confidence-weighted soft decision, stretch the result
with Argon2id into a SecretBox key.

Two deliberate departures from ``middlelock.py``, both decided at `/plan`:

1. **Variable-length enrollment.** ``middlelock.commit`` hard-asserts exactly
   ``ENROLLMENT_TAKES`` embeddings, because F4 has 5 genuinely independent
   spoken sentences to measure cross-take unanimity against. F7 does not: the
   Gate test enrolls on a single genuine fixture take (A1 alone — this repo
   has exactly one independent same-person face pair, per spec Q1), while
   live production enrolls on ``ENROLLMENT_TAKES = 3`` camera frames from one
   burst. ``commit`` here accepts any non-empty list. At n=1 the reliability
   mask's cross-take-unanimity filter is vacuously true (nothing to disagree
   with), which is the module's own documented fallback to pure margin
   ranking — already the right behaviour, not a special case.
2. **Thin-evidence `CORRECTION_RADIUS`.** ``middlelock``'s 110 was measured
   over 200 independent commits against many voice fixture comparisons. This
   repo has exactly one independent same-person face pair (Douglass A1/A2)
   and one different-person subject (B), so the radius below rests on a
   single genuine residual (enroll A1, reconcile A2) and the lower of two
   impostor residuals (enroll A1 or A2, reconcile B) — n=1 genuine, n=2
   impostor. Measured over repeated commits (each draws a fresh random LSH
   seed, same practice ``middlelock``'s own test uses) to find a value that
   holds across the randomness, not a one-off lucky draw. Disclosed here and
   in spec Q2/§7: this is real measurement, not an invented number, but
   categorically thinner evidence than the voice lock's.

Honest limits — same as ``middlelock.py``: helper data is non-secret and
leaks bounded information about the faceprint; the secret is short
(``KEY_BITS``) because depth, not length, absorbs noise; the inner lock sits
innermost, reached only after the passphrase AND the voice have already
verified, so brute-forcing the short secret costs a KDF per guess.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

import numpy as np
from nacl import pwhash, secret as nacl_secret, utils

# SFace (faceprint.py) emits a 128-dim feature vector (OpenCV's published
# output width for this model). faceprint.py exports no EMBEDDING_DIM
# constant the way voiceprint.py does, and F7 does not modify faceprint.py
# (spec §3 non-goals), so the width is pinned here instead of imported.
EMBEDDING_DIM = 128

# --- Sizing knobs -------------------------------------------------------------
# CANDIDATE_BITS/RELIABLE_BITS/KEY_BITS/REPETITION are reused UNCHANGED from
# middlelock (spec Q2, human-approved 2026-07-27): they size the ECC bit
# budget, not the input embedding width, so there is no mathematical reason to
# scale them by 128/192.

CANDIDATE_BITS = 4096
RELIABLE_BITS = 512
KEY_BITS = 32
REPETITION = RELIABLE_BITS // KEY_BITS

# Measured (see module docstring point 2 and spec Q2/§7), over 100 commits
# (each draws a fresh random LSH seed, same practice middlelock's own test
# uses): enrolling on A1 alone and reconciling against A2 (the genuine pair)
# never exceeds 20 residual bits; enrolling on A1 or A2 and reconciling
# against B (the two impostor measurements) never drops below 170. 95 is the
# midpoint of that 20..170 gap. n=1 genuine / n=2 impostor — thinner evidence
# than middlelock's 200-commit measurement, disclosed honestly rather than
# presented as equally reliable.
CORRECTION_RADIUS = 95

# Live-production enrollment take count (spec Q1 decision 2): reuses F6's
# REFERENCE_TAKES = 3 burst pattern. Deliberately a SEPARATE constant from
# faceprint.REFERENCE_TAKES (also 3, coincidentally) — they gate two
# independent flows (the diagnostic panel vs. this lock) and must not be
# aliased into one just because the numbers currently match.
ENROLLMENT_TAKES = 3

# Argon2id cost for the inner lock. INTERACTIVE, not MODERATE: the outer
# passphrase lock already pays MODERATE and this layer is only reached after
# BOTH the outer and middle locks have already fallen.
_KDF_OPS = pwhash.argon2id.OPSLIMIT_INTERACTIVE
_KDF_MEM = pwhash.argon2id.MEMLIMIT_INTERACTIVE
_SALT_BYTES = pwhash.argon2id.SALTBYTES
_SEED_BYTES = 16

_HELPER_VERSION = 1
_COMMIT_INFO = b"voicelock/inner/commit"
_KEY_INFO = b"voicelock/inner/key"


class FaceLockError(Exception):
    """Base error for inner (face) lock failures."""


class ReconcileError(FaceLockError):
    """The fresh faceprint did not reconcile — Booth copy: face didn't match."""


class HelperDataError(FaceLockError):
    """Helper data is missing, malformed, or from an unsupported version."""


def commit(enrollment_embeddings: list[np.ndarray]) -> tuple[bytes, dict[str, Any]]:
    """Bind a fresh random secret to an enrollment faceprint.

    Takes one or more enrollment embeddings (not frames — the vision pipeline
    stays in ``faceprint``): ``ENROLLMENT_TAKES`` live camera frames in
    production, a single fixture embedding in the Gate test (module docstring
    point 1). Returns ``(secret, helper_data)``; the helper data is non-secret,
    JSON-serializable, and required to reconcile later.
    """
    takes = _stack_embeddings(enrollment_embeddings)
    seed = utils.random(_SEED_BYTES)
    matrix = _projection_matrix(seed, CANDIDATE_BITS)
    projections = takes @ matrix.T  # (takes, CANDIDATE_BITS)

    mask = _reliability_mask(projections)
    reference = _normalize(takes.mean(axis=0))
    reference_bits = _sign_bits(reference @ matrix.T)[mask]

    secret_bits = _random_bits(KEY_BITS)
    codeword = np.repeat(secret_bits, REPETITION)
    offset = np.logical_xor(reference_bits, codeword)

    secret_bytes = np.packbits(secret_bits).tobytes()
    salt = utils.random(_SALT_BYTES)
    master = _stretch(secret_bytes, salt)

    helper_data = {
        "version": _HELPER_VERSION,
        "candidate_bits": CANDIDATE_BITS,
        "key_bits": KEY_BITS,
        "repetition": REPETITION,
        "seed": _b64(seed),
        "mask": _b64(mask.astype("<u2").tobytes()),
        "offset": _b64(np.packbits(offset).tobytes()),
        "salt": _b64(salt),
        "commitment": _b64(_tag(master, _COMMIT_INFO)),
    }
    return secret_bytes, helper_data


def reconcile(helper_data: dict[str, Any], live_embedding: np.ndarray) -> bytes:
    """Recover the committed secret from a fresh faceprint, or raise.

    Raises ``ReconcileError`` when the fresh faceprint is too far from the
    enrolled one — either beyond ``CORRECTION_RADIUS`` after decoding, or with
    a commitment tag that does not match. Never returns a partial or wrong
    secret.
    """
    parsed = _parse_helper(helper_data)
    secret_bits, residual = _decode(parsed, live_embedding)
    if residual > CORRECTION_RADIUS:
        raise ReconcileError(
            f"face did not reconcile: {residual} bits off, radius {CORRECTION_RADIUS}"
        )

    secret_bytes = np.packbits(secret_bits).tobytes()
    master = _stretch(secret_bytes, parsed["salt"])
    if not hmac.compare_digest(_tag(master, _COMMIT_INFO), parsed["commitment"]):
        raise ReconcileError("face did not reconcile: commitment mismatch")
    return secret_bytes


def derive_key(secret_bytes: bytes, salt: bytes) -> bytes:
    """Stretch a reconciled secret into a SecretBox key for the inner lock.

    ``salt`` is the ``salt`` field carried in the helper data, so the same
    (secret, salt) pair reproduces the same key on every unlock.
    """
    if not secret_bytes:
        raise FaceLockError("cannot derive a key from an empty secret")
    return _tag(_stretch(secret_bytes, salt), _KEY_INFO)


def residual_bits(helper_data: dict[str, Any], live_embedding: np.ndarray) -> int:
    """Bit-error count left after decoding — the tuning/diagnostic view.

    Same measurement ``reconcile`` gates on, exposed so the tests can assert
    that a genuine take sits below ``CORRECTION_RADIUS`` and an impostor
    above it.
    """
    return _decode(_parse_helper(helper_data), live_embedding)[1]


# --- internals ----------------------------------------------------------------


def _decode(
    parsed: dict[str, Any], live_embedding: np.ndarray
) -> tuple[np.ndarray, int]:
    """Soft-decode a fresh faceprint against helper data.

    Returns the decoded secret bits and the residual bit-error count — how
    many of the reliable bits still disagree with the re-encoded codeword.
    """
    live = _normalize(np.asarray(live_embedding, dtype=np.float64).reshape(-1))
    if live.size != EMBEDDING_DIM:
        raise FaceLockError(
            f"expected a {EMBEDDING_DIM}-dim embedding, got {live.size}"
        )

    matrix = _projection_matrix(parsed["seed"], parsed["candidate_bits"])
    projections = (live @ matrix.T)[parsed["mask"]]

    # b' XOR P = c XOR e — the codeword seen through the bit-flip error pattern.
    received = np.logical_xor(_sign_bits(projections), parsed["offset"])
    secret_bits = _soft_decode(received, np.abs(projections), parsed["key_bits"])
    residual = int(
        np.count_nonzero(
            np.logical_xor(received, np.repeat(secret_bits, parsed["repetition"]))
        )
    )
    return secret_bits, residual


def _projection_matrix(seed: bytes, candidate_bits: int) -> np.ndarray:
    """The seeded random hyperplanes. Non-secret: the seed is helper data."""
    rng = np.random.default_rng(int.from_bytes(seed, "big"))
    return rng.standard_normal((candidate_bits, EMBEDDING_DIM))


def _reliability_mask(projections: np.ndarray) -> np.ndarray:
    """Pick the ``RELIABLE_BITS`` most stable candidate bits.

    Cross-take sign unanimity is the primary filter, mean projection margin
    the tiebreak among survivors. At n=1 enrollment take (the Gate test, per
    module docstring point 1) unanimity is vacuously true for every candidate
    bit, so this degrades to a pure margin ranking — the documented fallback,
    not a special case.
    """
    signs = projections >= 0.0
    unanimous = np.all(signs == signs[0], axis=0)
    margin = np.abs(projections).mean(axis=0)
    # lexsort's LAST key is primary: unanimous bits first, then widest margin.
    order = np.lexsort((-margin, ~unanimous))
    return np.sort(order[:RELIABLE_BITS])


def _soft_decode(
    received: np.ndarray, confidence: np.ndarray, key_bits: int
) -> np.ndarray:
    """Confidence-weighted majority decode of the repetition code.

    Each copy votes for the bit value it observed, weighted by how far its
    projection sat from the hyperplane — see ``middlelock._soft_decode`` for
    the full rationale (identical here).
    """
    votes = np.where(received, -confidence, confidence)
    return votes.reshape(key_bits, -1).sum(axis=1) < 0.0


def _sign_bits(projections: np.ndarray) -> np.ndarray:
    return projections >= 0.0


def _stack_embeddings(embeddings: list[np.ndarray]) -> np.ndarray:
    """Stack one or more enrollment embeddings (module docstring point 1).

    Unlike ``middlelock._stack_embeddings``, the count is not pinned to a
    fixed ``ENROLLMENT_TAKES`` — only non-empty is required, so the same
    function serves both the Gate test's single fixture take and live
    production's three-frame burst.
    """
    if not embeddings:
        raise FaceLockError("need at least one enrollment embedding, got 0")
    rows = []
    for embedding in embeddings:
        vector = np.asarray(embedding, dtype=np.float64).reshape(-1)
        if vector.size != EMBEDDING_DIM:
            raise FaceLockError(
                f"expected {EMBEDDING_DIM}-dim embeddings, got {vector.size}"
            )
        rows.append(_normalize(vector))
    return np.stack(rows)


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise FaceLockError("degenerate (zero) embedding")
    return vector / norm


def _random_bits(count: int) -> np.ndarray:
    raw = utils.random((count + 7) // 8)
    return np.unpackbits(np.frombuffer(raw, dtype=np.uint8))[:count].astype(bool)


def _stretch(secret_bytes: bytes, salt: bytes) -> bytes:
    """Argon2id over the short secret — one KDF call per guess, by design."""
    return pwhash.argon2id.kdf(
        nacl_secret.SecretBox.KEY_SIZE,
        secret_bytes,
        salt,
        opslimit=_KDF_OPS,
        memlimit=_KDF_MEM,
    )


def _tag(master: bytes, info: bytes) -> bytes:
    return hashlib.sha256(info + master).digest()


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _parse_helper(helper_data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(helper_data, dict):
        raise HelperDataError("helper data must be a JSON object")
    if helper_data.get("version") != _HELPER_VERSION:
        raise HelperDataError(
            f"unsupported helper-data version: {helper_data.get('version')!r}"
        )
    try:
        candidate_bits = int(helper_data["candidate_bits"])
        key_bits = int(helper_data["key_bits"])
        repetition = int(helper_data["repetition"])
        seed = base64.b64decode(helper_data["seed"], validate=True)
        mask = np.frombuffer(
            base64.b64decode(helper_data["mask"], validate=True), dtype="<u2"
        ).astype(np.intp)
        offset_bytes = base64.b64decode(helper_data["offset"], validate=True)
        salt = base64.b64decode(helper_data["salt"], validate=True)
        commitment = base64.b64decode(helper_data["commitment"], validate=True)
    except (KeyError, TypeError, ValueError, base64.binascii.Error) as exc:
        raise HelperDataError("helper data is malformed") from exc

    width = key_bits * repetition
    if mask.size != width:
        raise HelperDataError("helper data is malformed: mask width mismatch")
    if mask.size and int(mask.max()) >= candidate_bits:
        raise HelperDataError("helper data is malformed: mask index out of range")
    offset = np.unpackbits(np.frombuffer(offset_bytes, dtype=np.uint8))[:width]
    if offset.size != width:
        raise HelperDataError("helper data is malformed: offset width mismatch")

    return {
        "candidate_bits": candidate_bits,
        "key_bits": key_bits,
        "repetition": repetition,
        "seed": seed,
        "mask": mask,
        "offset": offset.astype(bool),
        "salt": salt,
        "commitment": commitment,
    }

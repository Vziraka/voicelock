"""Middle lock — a stable key bound to the enrolled voiceprint (F4).

A hand-rolled **code-offset fuzzy commitment** (Juels-Wattenberg, 1999; the
code-offset secure sketch of the fuzzy-extractor framework) in pure numpy — no
new dependency. It turns the noisy 192-dim ECAPA voiceprint into a stable secret
plus non-secret **helper data**, so the same speaker recovers the same secret
while a different speaker does not.

Pipeline, in the order spec 4 pins it:

1. **Binarize + expand.** A seeded random-hyperplane LSH projection maps the
   L2-normalized embedding to ``CANDIDATE_BITS`` sign bits. Raw 192 sign bits
   carry far too much genuine bit-error to key anything, so we project to a large
   candidate pool and mask it down — same final bit count, much higher selection
   pressure. Only the seed is stored, so the pool costs nothing at rest.
2. **Reliability mask.** Keep ``RELIABLE_BITS`` bits, filtered primarily by
   **cross-take sign unanimity** (a bit must come out the same way in every
   enrollment take) and ranked by mean projection margin as the tiebreak.
   Unanimity measures stability under exactly the within-speaker variation the
   lock must survive; margin only proxies it.
3. **Inner code.** A repetition code with **confidence-weighted (soft-decision)
   majority decoding**: each secret bit is decoded by summing its copies' signed
   projection magnitudes, so a near-zero-margin measurement (a coin flip) cannot
   outvote a confident one.
4. **Key.** The recovered secret is stretched with Argon2id into a SecretBox key.

Honest limits (this is a labeled learning demo, not product-grade crypto):
helper data is **non-secret** and leaks bounded information about the voiceprint;
the secret is deliberately short (``KEY_BITS``) because the reliable-bit budget
buys more by going into repetition depth than into key length. That trade is only
sound because the middle lock sits **inside** the passphrase outer lock — the
voice key is never attacked directly until Argon2id on the outer lock has already
fallen. Everything that verifies a guess (the commitment tag and the key itself)
hangs off one Argon2id stretch, so brute-forcing the short secret costs a KDF per
guess rather than a hash per guess.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
from typing import Any

import numpy as np
from nacl import pwhash, secret as nacl_secret, utils

from voicelock.voiceprint import EMBEDDING_DIM

# --- Sizing knobs -------------------------------------------------------------
# Pinned empirically against tests/fixtures/voiceprint (see that README for the
# measured genuine/impostor separation these values are chosen to hold apart).
# The tests import these — they are never re-typed as literals in a test.

# The LSH candidate pool. Large on purpose: masking 512 survivors out of 4096 is a
# far stronger stability filter than projecting straight to 512.
CANDIDATE_BITS = 4096

# Bits kept by the reliability mask — the working width of the inner code.
RELIABLE_BITS = 512

# Secret length. Short by design: depth absorbs noise, length does not.
KEY_BITS = 32

# Copies of each secret bit inside the reliable-bit budget.
REPETITION = RELIABLE_BITS // KEY_BITS

# The correction radius: how many of the RELIABLE_BITS may still disagree with the
# re-encoded codeword after decoding before we call it a different speaker — the
# "how close is close enough" knob, analogous to voiceprint's ACCEPT/REJECT
# cutoffs. Measured over 200 independent commits on the fixtures: the same-speaker
# probe and the enrollment takes leave 0 residual bits, harder same-speaker clips
# (the shorter F3 thirds, cosine 0.12-0.43 from the enrollment mean) reach 63, and
# the impostor never drops below 156. 110 is the midpoint of that 63..156 gap.
#
# Note what this knob can and cannot do: widening it can never admit a wrong
# voice, because the commitment tag below is the authoritative check — a wrong
# secret fails it regardless of the radius. The radius is a cheap early reject
# that saves an Argon2id call on an obvious impostor, and the explicit,
# inspectable place where "close enough" is written down. Narrowing it too far,
# on the other hand, costs genuine unlocks.
CORRECTION_RADIUS = 110

# Enrollment reads this many sentences (spec 3); the mask needs them all to
# measure cross-take unanimity.
ENROLLMENT_TAKES = 5

# Argon2id cost for the middle lock. INTERACTIVE, not MODERATE: the outer
# passphrase lock already pays MODERATE, and an attacker only reaches this layer
# after the outer lock has fallen. Two stretches run per unlock (one to verify the
# commitment, one to derive the key), so the cost is doubled in practice.
_KDF_OPS = pwhash.argon2id.OPSLIMIT_INTERACTIVE
_KDF_MEM = pwhash.argon2id.MEMLIMIT_INTERACTIVE
_SALT_BYTES = pwhash.argon2id.SALTBYTES
_SEED_BYTES = 16

_HELPER_VERSION = 1
_COMMIT_INFO = b"voicelock/middle/commit"
_KEY_INFO = b"voicelock/middle/key"


class MiddleLockError(Exception):
    """Base error for middle-lock failures."""


class ReconcileError(MiddleLockError):
    """The fresh voiceprint did not reconcile — Booth copy: voice didn't match."""


class HelperDataError(MiddleLockError):
    """Helper data is missing, malformed, or from an unsupported version."""


def commit(enrollment_embeddings: list[np.ndarray]) -> tuple[bytes, dict[str, Any]]:
    """Bind a fresh random secret to an enrollment voiceprint.

    Takes the ``ENROLLMENT_TAKES`` per-sentence embeddings (not audio — the DSP
    stays in ``voiceprint``), and returns ``(secret, helper_data)``. The helper
    data is non-secret, JSON-serializable, and required to reconcile later.
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
    """Recover the committed secret from a fresh voiceprint, or raise.

    Raises ``ReconcileError`` when the fresh voiceprint is too far from the
    enrolled one — either beyond ``CORRECTION_RADIUS`` after decoding, or with a
    commitment tag that does not match. Never returns a partial or wrong secret.
    """
    parsed = _parse_helper(helper_data)
    secret_bits, residual = _decode(parsed, live_embedding)
    if residual > CORRECTION_RADIUS:
        raise ReconcileError(
            f"voice did not reconcile: {residual} bits off, radius {CORRECTION_RADIUS}"
        )

    secret_bytes = np.packbits(secret_bits).tobytes()
    master = _stretch(secret_bytes, parsed["salt"])
    if not hmac.compare_digest(_tag(master, _COMMIT_INFO), parsed["commitment"]):
        raise ReconcileError("voice did not reconcile: commitment mismatch")
    return secret_bytes


def derive_key(secret_bytes: bytes, salt: bytes) -> bytes:
    """Stretch a reconciled secret into a SecretBox key for the middle lock.

    ``salt`` is the ``salt`` field carried in the helper data, so the same
    (secret, salt) pair reproduces the same key on every unlock. The key and the
    commitment tag hang off one Argon2id stretch under different info strings —
    verifying a guessed secret therefore costs a KDF, not a bare hash.
    """
    if not secret_bytes:
        raise MiddleLockError("cannot derive a key from an empty secret")
    return _tag(_stretch(secret_bytes, salt), _KEY_INFO)


def residual_bits(helper_data: dict[str, Any], live_embedding: np.ndarray) -> int:
    """Bit-error count left after decoding — the tuning/diagnostic view.

    Same measurement ``reconcile`` gates on, exposed so the tests can assert that
    a genuine take sits below ``CORRECTION_RADIUS`` and an impostor above it.
    """
    return _decode(_parse_helper(helper_data), live_embedding)[1]


# --- internals ----------------------------------------------------------------


def _decode(
    parsed: dict[str, Any], live_embedding: np.ndarray
) -> tuple[np.ndarray, int]:
    """Soft-decode a fresh voiceprint against helper data.

    Returns the decoded secret bits and the residual bit-error count — how many
    of the reliable bits still disagree with the re-encoded codeword. That count
    is the bounded-distance check: decode, re-encode, measure the distance.
    """
    live = _normalize(np.asarray(live_embedding, dtype=np.float64).reshape(-1))
    if live.size != EMBEDDING_DIM:
        raise MiddleLockError(
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

    Cross-take sign unanimity is the primary filter, mean projection margin the
    tiebreak among survivors. If fewer than ``RELIABLE_BITS`` candidates are
    unanimous the ranking simply continues into the non-unanimous ones, worst
    case degrading to a pure margin ranking — the lock still works, it is just
    noisier, and the commitment tag still refuses a wrong secret.
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
    projection sat from the hyperplane. Summing signed magnitudes (rather than
    counting hard signs) keeps a near-zero-margin copy — effectively a coin
    flip — from outvoting a confident one.

    Measured honestly: on the current fixtures soft decoding makes no difference
    (over 40 commits, worst genuine 51 either way; impostor floor 167 soft vs 165
    hard). That is because these fixtures never come near the decision boundary —
    the hardest genuine clip still gets ~1.5 of 16 copies wrong per secret bit,
    nowhere near an 8/16 tie, so no reweighting can change the outcome. It is kept
    because it cannot lose to hard voting and the fixtures under-represent the
    noise a real cross-session unlock brings, which is exactly where marginal
    votes appear.
    """
    votes = np.where(received, -confidence, confidence)
    return votes.reshape(key_bits, -1).sum(axis=1) < 0.0


def _sign_bits(projections: np.ndarray) -> np.ndarray:
    return projections >= 0.0


def _stack_embeddings(embeddings: list[np.ndarray]) -> np.ndarray:
    if len(embeddings) != ENROLLMENT_TAKES:
        raise MiddleLockError(
            f"need exactly {ENROLLMENT_TAKES} enrollment embeddings, "
            f"got {len(embeddings)}"
        )
    rows = []
    for embedding in embeddings:
        vector = np.asarray(embedding, dtype=np.float64).reshape(-1)
        if vector.size != EMBEDDING_DIM:
            raise MiddleLockError(
                f"expected {EMBEDDING_DIM}-dim embeddings, got {vector.size}"
            )
        rows.append(_normalize(vector))
    return np.stack(rows)


def _normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise MiddleLockError("degenerate (zero) embedding")
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

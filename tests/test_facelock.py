"""Face inner-lock tests — spec F7 §5 cmd 1.

Uses the committed A1/A2/B fixtures under ``fixtures/face`` (no new fixtures,
per spec Q1) and the vendored SFace model loaded fully offline — no mocked
embeddings. Every tolerance assertion imports the module constants the app
uses, so the pass/fail boundary is deterministic rather than a judgment call.

Per spec Q1, this repo has exactly one genuine same-person face pair
(personA_1/personA_2) and one different-person subject (personB) — thinner
evidence than ``middlelock``'s 5-take, 200-commit measurement. The Gate test
below enrolls with A1 alone (a single genuine take), consistent with live
production's 3-frame burst only in that both are "one or more" takes
(``facelock.commit``'s variable-length contract, decided at ``/plan``).
"""

from __future__ import annotations

import json
import socket
from pathlib import Path

import numpy as np
import pytest

from voicelock.facelock import (
    CANDIDATE_BITS,
    CORRECTION_RADIUS,
    EMBEDDING_DIM,
    ENROLLMENT_TAKES,
    KEY_BITS,
    RELIABLE_BITS,
    REPETITION,
    FaceLockError,
    HelperDataError,
    ReconcileError,
    commit,
    derive_key,
    reconcile,
    residual_bits,
)
from voicelock.faceprint import embed_file

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


@pytest.fixture(scope="module")
def committed(person_a_1: np.ndarray) -> tuple[bytes, dict]:
    """Enrolled on A1 alone — the Gate test's thin-evidence enrollment (Q1)."""
    return commit([person_a_1])


# --- case: commit emits a secret + JSON-safe helper data ---------------------
def test_commit_emits_secret_and_helper_data(committed: tuple[bytes, dict]) -> None:
    secret, helper = committed

    assert isinstance(secret, bytes)
    assert len(secret) == KEY_BITS // 8

    # The four helper components middlelock's shape pins: LSH seed,
    # reliability mask, XOR offset P, and the commitment over the secret.
    assert set(helper) >= {"seed", "mask", "offset", "commitment"}
    assert helper["candidate_bits"] == CANDIDATE_BITS
    assert helper["key_bits"] == KEY_BITS
    assert helper["repetition"] == REPETITION

    # The vault stores this inside the middle box as JSON, so it must survive
    # a round trip with no custom encoder.
    assert json.loads(json.dumps(helper)) == helper
    assert all(isinstance(value, (int, str)) for value in helper.values())


def test_helper_data_does_not_expose_the_secret(committed: tuple[bytes, dict]) -> None:
    secret, helper = committed
    blob = json.dumps(helper).encode("utf-8")
    assert secret not in blob


# --- case: same-person reconcile recovers the identical secret ---------------
def test_same_person_reconciles_to_identical_secret(
    committed: tuple[bytes, dict], person_a_2: np.ndarray
) -> None:
    secret, helper = committed
    assert reconcile(helper, person_a_2) == secret


def test_reconcile_is_deterministic(
    committed: tuple[bytes, dict], person_a_2: np.ndarray
) -> None:
    _, helper = committed
    assert reconcile(helper, person_a_2) == reconcile(helper, person_a_2)


# --- case: a different person does not reconcile -----------------------------
def test_different_person_raises(
    committed: tuple[bytes, dict], person_b: np.ndarray
) -> None:
    _, helper = committed
    with pytest.raises(ReconcileError):
        reconcile(helper, person_b)


def test_independent_commits_produce_independent_secrets(
    person_a_1: np.ndarray, person_a_2: np.ndarray
) -> None:
    """A fresh enrollment binds a fresh secret — helper data is not a fixed key."""
    first_secret, first_helper = commit([person_a_1])
    second_secret, second_helper = commit([person_a_1])
    assert first_secret != second_secret
    assert first_helper["seed"] != second_helper["seed"]
    # ...and each still reconciles against its OWN helper data.
    assert reconcile(first_helper, person_a_2) == first_secret
    assert reconcile(second_helper, person_a_2) == second_secret


# --- case: variable-length enrollment (decision 1) ----------------------------
def test_commit_accepts_a_single_embedding(person_a_1: np.ndarray) -> None:
    """The Gate-test shape: exactly one genuine take, per spec Q1."""
    secret, helper = commit([person_a_1])
    assert isinstance(secret, bytes)
    assert helper["repetition"] == REPETITION


def test_commit_accepts_multiple_independent_embeddings(
    person_a_1: np.ndarray, person_a_2: np.ndarray
) -> None:
    """Two genuine, independently-photographed takes (not a derived probe)."""
    secret, helper = commit([person_a_1, person_a_2])
    assert reconcile(helper, person_a_1) == secret
    assert reconcile(helper, person_a_2) == secret


def test_commit_rejects_an_empty_enrollment_list() -> None:
    with pytest.raises(FaceLockError):
        commit([])


# --- case: the tolerance knobs are imported constants, unchanged from middlelock
def test_constants_reused_unchanged_from_middlelock() -> None:
    assert CANDIDATE_BITS == 4096
    assert RELIABLE_BITS == 512
    assert KEY_BITS == 32
    assert REPETITION == 16
    assert KEY_BITS * REPETITION == RELIABLE_BITS
    assert RELIABLE_BITS < CANDIDATE_BITS  # the pool is masked DOWN, not up
    assert 0 < CORRECTION_RADIUS < RELIABLE_BITS


def test_genuine_and_impostor_straddle_the_correction_radius(
    person_a_1: np.ndarray, person_a_2: np.ndarray, person_b: np.ndarray
) -> None:
    """The whole feature in one assertion: measured residuals straddle the radius.

    Asserts the ACTUAL measured gap (per spec §5 cmd 1's explicit requirement),
    not just that the constant exists. Enrolls independently on A1 and on A2
    (each a fresh random LSH seed) to get the n=1 genuine / n=2 impostor
    measurements the module docstring discloses.
    """
    _, helper_a1 = commit([person_a_1])
    _, helper_a2 = commit([person_a_2])

    genuine_residual = residual_bits(helper_a1, person_a_2)
    impostor_residual_1 = residual_bits(helper_a1, person_b)
    impostor_residual_2 = residual_bits(helper_a2, person_b)
    impostor_floor = min(impostor_residual_1, impostor_residual_2)

    assert genuine_residual < CORRECTION_RADIUS < impostor_floor, (
        f"genuine={genuine_residual}, impostor_floor={impostor_floor}, "
        f"radius={CORRECTION_RADIUS} — the measured gap does not straddle "
        "the pinned radius"
    )


# --- case: derive_key is a deterministic 32-byte SecretBox key ---------------
def test_derive_key_is_deterministic_and_32_bytes() -> None:
    secret, salt = b"\x01\x02\x03\x04", b"s" * 16
    key = derive_key(secret, salt)
    assert isinstance(key, bytes)
    assert len(key) == 32
    assert derive_key(secret, salt) == key


def test_derive_key_changes_with_secret_and_with_salt() -> None:
    salt, other_salt = b"s" * 16, b"t" * 16
    secret, other_secret = b"\x01\x02\x03\x04", b"\x01\x02\x03\x05"
    base = derive_key(secret, salt)
    assert derive_key(other_secret, salt) != base
    assert derive_key(secret, other_salt) != base


def test_derive_key_refuses_an_empty_secret() -> None:
    with pytest.raises(FaceLockError):
        derive_key(b"", b"s" * 16)


# --- input validation + helper-data integrity --------------------------------
def test_commit_rejects_a_wrong_width_embedding(person_a_1: np.ndarray) -> None:
    with pytest.raises(FaceLockError):
        commit([np.ones(EMBEDDING_DIM + 1)])


def test_reconcile_rejects_a_wrong_width_embedding(
    committed: tuple[bytes, dict],
) -> None:
    _, helper = committed
    with pytest.raises(FaceLockError):
        reconcile(helper, np.ones(EMBEDDING_DIM + 1))


@pytest.mark.parametrize("field", ["seed", "mask", "offset", "commitment"])
def test_replaced_helper_component_fails_closed(
    committed: tuple[bytes, dict], person_a_2: np.ndarray, field: str
) -> None:
    """Swapping a whole helper component for another valid one is refused.

    Uses a second real commit as the donor so every field stays well-formed —
    this probes the crypto, not the parser.
    """
    _, helper = committed
    _, donor = commit([np.eye(EMBEDDING_DIM)[0]])
    with pytest.raises((ReconcileError, HelperDataError)):
        reconcile({**helper, field: donor[field]}, person_a_2)


@pytest.mark.parametrize("field", ["seed", "mask", "offset", "commitment"])
def test_lightly_corrupted_helper_never_yields_a_different_secret(
    committed: tuple[bytes, dict], person_a_2: np.ndarray, field: str
) -> None:
    """Small helper corruption either corrects or fails — never forges a key."""
    secret, helper = committed
    corrupted = {**helper, field: "AAAA" + helper[field][4:]}
    try:
        recovered = reconcile(corrupted, person_a_2)
    except (ReconcileError, HelperDataError):
        return
    assert recovered == secret


def test_unsupported_helper_version_is_refused(committed: tuple[bytes, dict]) -> None:
    _, helper = committed
    with pytest.raises(HelperDataError):
        reconcile({**helper, "version": 99}, np.ones(EMBEDDING_DIM))


def test_missing_helper_fields_are_refused() -> None:
    with pytest.raises(HelperDataError):
        reconcile({"version": 1}, np.ones(EMBEDDING_DIM))


def test_enrollment_takes_constant_is_the_live_production_count() -> None:
    """Decision 2: a constant separate from faceprint.REFERENCE_TAKES."""
    assert ENROLLMENT_TAKES == 3


# --- the whole path stays offline --------------------------------------------
def test_no_network_during_commit_and_reconcile(
    monkeypatch: pytest.MonkeyPatch,
    person_a_1: np.ndarray,
    person_a_2: np.ndarray,
) -> None:
    def _blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted in the inner lock")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)
    secret, helper = commit([person_a_1])
    assert reconcile(helper, person_a_2) == secret

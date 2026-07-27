"""Middle-lock tests — spec F4 §5 cases (1)-(7).

Uses the fixed 5-take enrollment fixtures under ``fixtures/voiceprint`` and the
vendored ECAPA model loaded fully offline (``HF_HUB_OFFLINE``, no network). Every
tolerance assertion imports the module constants the app uses, so the pass/fail
boundary is deterministic rather than a judgment call.

Two halves: the fuzzy-commitment engine (Task 2) and the nested v2 vault it seals
(Task 3, from ``test_nested_vault`` onward).
"""

from __future__ import annotations

import json
import socket
from pathlib import Path

import numpy as np
import pytest

from voicelock.middlelock import (
    CANDIDATE_BITS,
    CORRECTION_RADIUS,
    ENROLLMENT_TAKES,
    KEY_BITS,
    RELIABLE_BITS,
    REPETITION,
    HelperDataError,
    MiddleLockError,
    ReconcileError,
    commit,
    derive_key,
    reconcile,
    residual_bits,
)
from voicelock.facelock import EMBEDDING_DIM as FACE_EMBEDDING_DIM
from voicelock.vault import (
    FORMAT_VERSION,
    MAGIC,
    AuthError,
    LegacyVaultError,
    VoiceAuthError,
)
from voicelock.vault import enroll as vault_enroll
from voicelock.vault import unlock as vault_unlock
from voicelock.voiceprint import EMBEDDING_DIM, embed, load_wav

FIXTURES = Path(__file__).parent / "fixtures" / "voiceprint"
PASSPHRASE = "correct-horse-battery-staple"
NAME = "Ada Lovelace"


@pytest.fixture(scope="module")
def enrollment() -> list[np.ndarray]:
    """The five enrollment voiceprints, as `vault.enroll` will supply them."""
    return [
        embed(load_wav(FIXTURES / f"speakerA_enroll{i}.wav"))
        for i in range(1, ENROLLMENT_TAKES + 1)
    ]


@pytest.fixture(scope="module")
def same_speaker() -> np.ndarray:
    return embed(load_wav(FIXTURES / "speakerA_live.wav"))


@pytest.fixture(scope="module")
def different_speaker() -> np.ndarray:
    return embed(load_wav(FIXTURES / "speakerB.wav"))


@pytest.fixture(scope="module")
def committed(enrollment: list[np.ndarray]) -> tuple[bytes, dict]:
    return commit(enrollment)


# --- case (a): commit emits a secret + JSON-safe helper data ------------------
def test_commit_emits_secret_and_helper_data(committed: tuple[bytes, dict]) -> None:
    secret, helper = committed

    assert isinstance(secret, bytes)
    assert len(secret) == KEY_BITS // 8

    # The four helper components spec §4 pins: LSH seed, reliability mask, XOR
    # offset P, and the commitment over the secret.
    assert set(helper) >= {"seed", "mask", "offset", "commitment"}
    assert helper["candidate_bits"] == CANDIDATE_BITS
    assert helper["key_bits"] == KEY_BITS
    assert helper["repetition"] == REPETITION

    # Task 3 stores this inside the outer passphrase box as JSON, so it must
    # survive a round trip with no custom encoder.
    assert json.loads(json.dumps(helper)) == helper
    assert all(isinstance(value, (int, str)) for value in helper.values())


def test_helper_data_does_not_expose_the_secret(committed: tuple[bytes, dict]) -> None:
    secret, helper = committed
    blob = json.dumps(helper).encode("utf-8")
    assert secret not in blob


# --- case (b): the same speaker reconciles to the identical secret ------------
def test_same_speaker_reconciles_to_identical_secret(
    committed: tuple[bytes, dict], same_speaker: np.ndarray
) -> None:
    secret, helper = committed
    assert reconcile(helper, same_speaker) == secret


def test_each_enrollment_take_reconciles(
    committed: tuple[bytes, dict], enrollment: list[np.ndarray]
) -> None:
    """Every take that shaped the mask must itself still open the lock."""
    secret, helper = committed
    for index, take in enumerate(enrollment, start=1):
        assert reconcile(helper, take) == secret, f"enrollment take {index} failed"


def test_reconcile_is_deterministic(
    committed: tuple[bytes, dict], same_speaker: np.ndarray
) -> None:
    _, helper = committed
    assert reconcile(helper, same_speaker) == reconcile(helper, same_speaker)


# --- case (c): a different speaker does not reconcile ------------------------
def test_different_speaker_raises(
    committed: tuple[bytes, dict], different_speaker: np.ndarray
) -> None:
    _, helper = committed
    with pytest.raises(ReconcileError):
        reconcile(helper, different_speaker)


def test_independent_commits_produce_independent_secrets(
    enrollment: list[np.ndarray], same_speaker: np.ndarray
) -> None:
    """A fresh enrollment binds a fresh secret — helper data is not a fixed key."""
    first_secret, first_helper = commit(enrollment)
    second_secret, second_helper = commit(enrollment)
    assert first_secret != second_secret
    assert first_helper["seed"] != second_helper["seed"]
    # ...and each still reconciles against its OWN helper data.
    assert reconcile(first_helper, same_speaker) == first_secret
    assert reconcile(second_helper, same_speaker) == second_secret


# --- case (d): the tolerance knobs are imported constants, with margin --------
def test_tolerance_constants_are_coherent() -> None:
    assert KEY_BITS * REPETITION == RELIABLE_BITS
    assert RELIABLE_BITS < CANDIDATE_BITS  # the pool is masked DOWN, not up
    assert 0 < CORRECTION_RADIUS < RELIABLE_BITS


def test_genuine_and_impostor_straddle_the_correction_radius(
    committed: tuple[bytes, dict],
    same_speaker: np.ndarray,
    different_speaker: np.ndarray,
    enrollment: list[np.ndarray],
) -> None:
    """The whole feature in one assertion: the clusters sit either side of the radius.

    Margins come from a 200-commit measurement on these fixtures (each commit
    draws a fresh random LSH seed, so this runs against a different projection
    every time): the same-speaker probe and the enrollment takes leave 0 residual
    bits, and the impostor never fell below 156 against a radius of 110. The
    bounds below are set inside those observations so a retune that quietly
    collapses the separation fails here rather than in the demo.
    """
    _, helper = committed

    genuine = [residual_bits(helper, take) for take in enrollment]
    genuine.append(residual_bits(helper, same_speaker))
    impostor = residual_bits(helper, different_speaker)

    assert max(genuine) <= CORRECTION_RADIUS // 4, (
        f"genuine residual {max(genuine)} is too close to radius {CORRECTION_RADIUS}"
    )
    assert impostor >= CORRECTION_RADIUS * 1.3, (
        f"impostor residual {impostor} is too close to radius {CORRECTION_RADIUS}"
    )


def test_a_harder_same_speaker_clip_still_opens_the_lock() -> None:
    """The F3 thirds are shorter, noisier same-speaker audio — they must still open.

    These sit 0.12-0.43 cosine from the enrollment mean, versus 0.06 for the F4
    probe, so they are the closest thing these fixtures have to a real unlock
    recorded under different conditions. Measured worst case over 200 commits: 63
    residual bits against a radius of 110.
    """
    takes = [
        embed(load_wav(FIXTURES / f"speakerA_enroll{i}.wav"))
        for i in range(1, ENROLLMENT_TAKES + 1)
    ]
    secret, helper = commit(takes)
    for index in (1, 2, 3):
        clip = embed(load_wav(FIXTURES / f"speakerA_take{index}.wav"))
        residual = residual_bits(helper, clip)
        assert residual < CORRECTION_RADIUS, (
            f"F3 take{index} left {residual} residual bits — a genuine speaker "
            f"was rejected at radius {CORRECTION_RADIUS}"
        )
        assert reconcile(helper, clip) == secret


# --- case (e): derive_key is a deterministic 32-byte SecretBox key ------------
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
    with pytest.raises(MiddleLockError):
        derive_key(b"", b"s" * 16)


# --- input validation + helper-data integrity --------------------------------
def test_commit_requires_all_enrollment_takes(enrollment: list[np.ndarray]) -> None:
    with pytest.raises(MiddleLockError):
        commit(enrollment[:-1])


def test_commit_rejects_a_wrong_width_embedding(enrollment: list[np.ndarray]) -> None:
    takes = list(enrollment)
    takes[0] = np.ones(EMBEDDING_DIM + 1)
    with pytest.raises(MiddleLockError):
        commit(takes)


def test_reconcile_rejects_a_wrong_width_embedding(
    committed: tuple[bytes, dict],
) -> None:
    _, helper = committed
    with pytest.raises(MiddleLockError):
        reconcile(helper, np.ones(EMBEDDING_DIM + 1))


@pytest.mark.parametrize("field", ["seed", "mask", "offset", "commitment"])
def test_replaced_helper_component_fails_closed(
    committed: tuple[bytes, dict], same_speaker: np.ndarray, field: str
) -> None:
    """Swapping a whole helper component for another valid one is refused.

    Uses a second real commit as the donor so every field stays well-formed —
    this probes the crypto, not the parser.
    """
    _, helper = committed
    _, donor = commit([np.eye(EMBEDDING_DIM)[i] for i in range(ENROLLMENT_TAKES)])
    with pytest.raises((ReconcileError, HelperDataError)):
        reconcile({**helper, field: donor[field]}, same_speaker)


@pytest.mark.parametrize("field", ["seed", "mask", "offset", "commitment"])
def test_lightly_corrupted_helper_never_yields_a_different_secret(
    committed: tuple[bytes, dict], same_speaker: np.ndarray, field: str
) -> None:
    """Small helper corruption either corrects or fails — never forges a key.

    A handful of flipped helper bits is exactly the error pattern the repetition
    code exists to absorb, so recovering the ORIGINAL secret here is correct
    behaviour. What must never happen is a *different* secret coming back, which
    would mean the commitment check can be walked past.
    """
    secret, helper = committed
    corrupted = {**helper, field: "AAAA" + helper[field][4:]}
    try:
        recovered = reconcile(corrupted, same_speaker)
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


# --- the whole path stays offline --------------------------------------------
def test_no_network_during_commit_and_reconcile(
    monkeypatch: pytest.MonkeyPatch,
    enrollment: list[np.ndarray],
    same_speaker: np.ndarray,
) -> None:
    def _blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted in the middle lock")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)
    secret, helper = commit(enrollment)
    assert reconcile(helper, same_speaker) == secret


# =============================================================================
# The nested v3 vault (Task 2) — voice-layer cases end to end, face held constant.
# =============================================================================


def a_faceprint(seed: int = 100) -> np.ndarray:
    """A deterministic synthetic embedding — stands in for a face.

    These vault-level cases are about the voice layer and the peel order, not
    face identity (that is ``test_facelock.py``'s job), so the face is held
    constant here with a synthetic unit-vector embedding.
    """
    vector = np.random.default_rng(seed).standard_normal(FACE_EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


@pytest.fixture
def sealed_vault(tmp_path: Path, enrollment: list[np.ndarray]) -> Path:
    vault = tmp_path / "vault.vl"
    vault_enroll(NAME, PASSPHRASE, enrollment, [a_faceprint()], path=vault)
    return vault


# --- case (1): enroll binds a middle key and seals a nested v3 vault ----------
def test_enroll_seals_a_v3_vault(sealed_vault: Path) -> None:
    raw = sealed_vault.read_bytes()
    assert raw[:4] == MAGIC == b"VLCK"
    assert raw[4] == FORMAT_VERSION == 3


# --- case (2): the same speaker unlocks and gets the display name ------------
def test_same_speaker_unlocks(sealed_vault: Path, same_speaker: np.ndarray) -> None:
    assert vault_unlock(PASSPHRASE, same_speaker, a_faceprint(), path=sealed_vault) == NAME


def test_each_enrollment_take_unlocks(
    sealed_vault: Path, enrollment: list[np.ndarray]
) -> None:
    for index, take in enumerate(enrollment, start=1):
        assert vault_unlock(PASSPHRASE, take, a_faceprint(), path=sealed_vault) == NAME, (
            f"enrollment take {index} could not unlock"
        )


# --- case (3): a different speaker is a MIDDLE reject, with no name ----------
def test_different_speaker_is_a_middle_reject(
    sealed_vault: Path, different_speaker: np.ndarray
) -> None:
    with pytest.raises(VoiceAuthError) as caught:
        vault_unlock(PASSPHRASE, different_speaker, a_faceprint(), path=sealed_vault)
    assert NAME not in str(caught.value)


# --- case (4): a wrong passphrase is an OUTER reject, before the voice --------
def test_wrong_passphrase_is_an_outer_reject(
    sealed_vault: Path, same_speaker: np.ndarray
) -> None:
    with pytest.raises(AuthError) as caught:
        vault_unlock("wrong-passphrase", same_speaker, a_faceprint(), path=sealed_vault)
    assert NAME not in str(caught.value)


def test_wrong_passphrase_outranks_a_wrong_voice(
    sealed_vault: Path, different_speaker: np.ndarray
) -> None:
    """Both factors wrong reports the OUTER cause — the peel order, asserted.

    ``AuthError`` and ``VoiceAuthError`` are siblings, so this fails loudly if the
    voice is ever consulted before the passphrase has been proven.
    """
    with pytest.raises(AuthError):
        vault_unlock("wrong-passphrase", different_speaker, a_faceprint(), path=sealed_vault)


def test_the_two_rejects_are_distinct_types(
    sealed_vault: Path, same_speaker: np.ndarray, different_speaker: np.ndarray
) -> None:
    """The demo's whole point: the outer and middle rejects never collapse."""
    with pytest.raises(AuthError) as outer:
        vault_unlock("wrong-passphrase", same_speaker, a_faceprint(), path=sealed_vault)
    with pytest.raises(VoiceAuthError) as middle:
        vault_unlock(PASSPHRASE, different_speaker, a_faceprint(), path=sealed_vault)
    assert not isinstance(outer.value, VoiceAuthError)
    assert not isinstance(middle.value, AuthError)


# --- case (6): a v1 or v2 vault is refused with the re-enroll signal ---------
def test_v1_vault_is_refused(sealed_vault: Path, same_speaker: np.ndarray) -> None:
    raw = bytearray(sealed_vault.read_bytes())
    raw[4] = 1
    sealed_vault.write_bytes(bytes(raw))
    with pytest.raises(LegacyVaultError, match="re-enroll"):
        vault_unlock(PASSPHRASE, same_speaker, a_faceprint(), path=sealed_vault)


def test_v2_vault_is_refused(sealed_vault: Path, same_speaker: np.ndarray) -> None:
    raw = bytearray(sealed_vault.read_bytes())
    raw[4] = 2
    sealed_vault.write_bytes(bytes(raw))
    with pytest.raises(LegacyVaultError, match="re-enroll"):
        vault_unlock(PASSPHRASE, same_speaker, a_faceprint(), path=sealed_vault)


# --- case (7): no leak — helper data and plaintext stay inside the outer box --
def test_vault_bytes_leak_neither_helper_data_nor_plaintext(
    sealed_vault: Path, enrollment: list[np.ndarray]
) -> None:
    raw = sealed_vault.read_bytes()

    # The display name never appears in the clear.
    assert NAME.encode("utf-8") not in raw
    # Nor does the JSON scaffolding of any nested payload — if helper data sat
    # outside its sealing box, these field names would be readable.
    for marker in (
        b"helper_data_voice",
        b"helper_data_face",
        b"middle_ciphertext",
        b"inner_ciphertext",
        b"schema_version",
        b"seed",
    ):
        assert marker not in raw

    # Nor any part of the reference embedding, in either byte order.
    reference = np.mean(enrollment, axis=0)
    for dtype in ("<f8", ">f8", "<f4", ">f4"):
        assert reference.astype(dtype).tobytes()[:32] not in raw

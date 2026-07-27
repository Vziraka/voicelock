"""Vault file format and enroll/unlock path tests (temp path only).

F4 nested the vault around voice, F7 nests it once more around face, so
``enroll``/``unlock`` now take voiceprints AND faceprints alongside the
passphrase. These cases are about the file format and input validation, not
about speaker/face identity, so they use synthetic unit-vector "voiceprints"/
"faceprints" — the vault never inspects where an embedding came from, and
this keeps the format tests free of the ECAPA/SFace models. Real-identity
behaviour is covered in ``test_middlelock.py`` (voice) and
``test_facelock.py`` (face).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from voicelock.facelock import EMBEDDING_DIM as FACE_EMBEDDING_DIM
from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.vault import (
    FORMAT_VERSION,
    MAGIC,
    AuthError,
    FaceAuthError,
    LegacyVaultError,
    NoVaultError,
    ValidationError,
    VoiceAuthError,
    default_vault_path,
    enroll,
    unlock,
)
from voicelock.voiceprint import EMBEDDING_DIM as VOICE_EMBEDDING_DIM


def a_voiceprint(seed: int = 0) -> np.ndarray:
    """A deterministic synthetic embedding — stands in for a speaker."""
    vector = np.random.default_rng(seed).standard_normal(VOICE_EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def a_faceprint(seed: int = 100) -> np.ndarray:
    """A deterministic synthetic embedding — stands in for a face."""
    vector = np.random.default_rng(seed).standard_normal(FACE_EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def enrollment(seed: int = 0) -> list[np.ndarray]:
    return [a_voiceprint(seed)] * ENROLLMENT_TAKES


def face_enrollment(seed: int = 100) -> list[np.ndarray]:
    return [a_faceprint(seed)]


def test_default_vault_path() -> None:
    assert default_vault_path() == Path.home() / ".voicelock" / "vault.vl"


def test_enroll_writes_vlck_header(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(), path=vault)
    raw = vault.read_bytes()
    assert raw[:4] == MAGIC
    assert raw[:4] == b"VLCK"
    assert vault.stat().st_size > 4


def test_enroll_writes_format_version_three(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(), path=vault)
    assert vault.read_bytes()[4] == FORMAT_VERSION == 3


def test_enroll_empty_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("", "secret", enrollment(), face_enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_empty_passphrase_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("Ada", "", enrollment(), face_enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_whitespace_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("   ", "secret", enrollment(), face_enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_validates_before_touching_the_voice(tmp_path: Path) -> None:
    """A bad name is refused even when the voiceprints/faceprints are unusable."""
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("", "secret", [], [], path=vault)
    assert not vault.exists()


def test_unlock_missing_vault(tmp_path: Path) -> None:
    vault = tmp_path / "missing.vl"
    with pytest.raises(NoVaultError, match="No vault yet — enroll first"):
        unlock("anything", a_voiceprint(), a_faceprint(), path=vault)


def test_unlock_refuses_a_legacy_v1_vault(tmp_path: Path) -> None:
    """A pre-voice vault is refused outright — no passphrase-only bypass."""
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(), path=vault)
    raw = bytearray(vault.read_bytes())
    raw[4] = 1  # stamp it back to the F2 format version
    vault.write_bytes(bytes(raw))

    with pytest.raises(LegacyVaultError, match="re-enroll") as caught:
        unlock("correct-horse", a_voiceprint(), a_faceprint(), path=vault)
    assert "voice" in str(caught.value)


def test_unlock_refuses_a_legacy_v2_vault(tmp_path: Path) -> None:
    """A pre-face vault (F4's format) is refused outright — no bypass."""
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(), path=vault)
    raw = bytearray(vault.read_bytes())
    raw[4] = 2  # stamp it back to the F4 format version
    vault.write_bytes(bytes(raw))

    with pytest.raises(LegacyVaultError, match="re-enroll") as caught:
        unlock("correct-horse", a_voiceprint(), a_faceprint(), path=vault)
    assert "face" in str(caught.value)


# --- the inner (face) reject — new in F7, spec §5 cmd 2 ----------------------
def test_unlock_right_passphrase_and_voice_returns_name(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(), path=vault)
    assert (
        unlock("correct-horse", a_voiceprint(), a_faceprint(), path=vault) == "Ada"
    )


def test_unlock_right_passphrase_and_voice_but_wrong_face_is_an_inner_reject(
    tmp_path: Path,
) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(seed=100), path=vault)
    with pytest.raises(FaceAuthError) as caught:
        unlock(
            "correct-horse", a_voiceprint(), a_faceprint(seed=200), path=vault
        )
    assert "Ada" not in str(caught.value)


def test_wrong_face_reject_is_distinct_from_outer_and_middle(tmp_path: Path) -> None:
    """The demo's whole point extended one layer: three rejects, never collapsed."""
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), face_enrollment(seed=100), path=vault)

    with pytest.raises(FaceAuthError) as inner:
        unlock("correct-horse", a_voiceprint(), a_faceprint(seed=200), path=vault)

    assert not isinstance(inner.value, AuthError)
    assert not isinstance(inner.value, VoiceAuthError)

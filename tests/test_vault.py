"""Vault file format and enroll/unlock path tests (temp path only).

F4 nested the vault, so ``enroll``/``unlock`` now take voiceprints alongside the
passphrase. These cases are about the file format and input validation, not about
speaker identity, so they use synthetic unit-vector "voiceprints" — the vault
never inspects where an embedding came from, and this keeps the format tests free
of the ECAPA model. Real-speaker behaviour is covered in ``test_middlelock.py``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.vault import (
    FORMAT_VERSION,
    MAGIC,
    LegacyVaultError,
    NoVaultError,
    ValidationError,
    default_vault_path,
    enroll,
    unlock,
)
from voicelock.voiceprint import EMBEDDING_DIM


def a_voiceprint(seed: int = 0) -> np.ndarray:
    """A deterministic synthetic embedding — stands in for a speaker."""
    vector = np.random.default_rng(seed).standard_normal(EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def enrollment(seed: int = 0) -> list[np.ndarray]:
    return [a_voiceprint(seed)] * ENROLLMENT_TAKES


def test_default_vault_path() -> None:
    assert default_vault_path() == Path.home() / ".voicelock" / "vault.vl"


def test_enroll_writes_vlck_header(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), path=vault)
    raw = vault.read_bytes()
    assert raw[:4] == MAGIC
    assert raw[:4] == b"VLCK"
    assert vault.stat().st_size > 4


def test_enroll_writes_format_version_two(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), path=vault)
    assert vault.read_bytes()[4] == FORMAT_VERSION == 2


def test_enroll_empty_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("", "secret", enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_empty_passphrase_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("Ada", "", enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_whitespace_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("   ", "secret", enrollment(), path=vault)
    assert not vault.exists()


def test_enroll_validates_before_touching_the_voice(tmp_path: Path) -> None:
    """A bad name is refused even when the voiceprints are unusable."""
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("", "secret", [], path=vault)
    assert not vault.exists()


def test_unlock_missing_vault(tmp_path: Path) -> None:
    vault = tmp_path / "missing.vl"
    with pytest.raises(NoVaultError, match="No vault yet — enroll first"):
        unlock("anything", a_voiceprint(), path=vault)


def test_unlock_refuses_a_legacy_v1_vault(tmp_path: Path) -> None:
    """A pre-voice vault is refused outright — no passphrase-only bypass."""
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", enrollment(), path=vault)
    raw = bytearray(vault.read_bytes())
    raw[4] = 1  # stamp it back to the F2 format version
    vault.write_bytes(bytes(raw))

    with pytest.raises(LegacyVaultError, match="re-enroll"):
        unlock("correct-horse", a_voiceprint(), path=vault)

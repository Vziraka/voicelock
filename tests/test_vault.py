"""Vault file format and enroll/unlock path tests (temp path only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from voicelock.vault import (
    MAGIC,
    NoVaultError,
    ValidationError,
    default_vault_path,
    enroll,
    unlock,
)


def test_default_vault_path() -> None:
    assert default_vault_path() == Path.home() / ".voicelock" / "vault.vl"


def test_enroll_writes_vlck_header(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse", path=vault)
    raw = vault.read_bytes()
    assert raw[:4] == MAGIC
    assert raw[:4] == b"VLCK"
    assert vault.stat().st_size > 4


def test_enroll_empty_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("", "secret", path=vault)
    assert not vault.exists()


def test_enroll_empty_passphrase_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("Ada", "", path=vault)
    assert not vault.exists()


def test_enroll_whitespace_name_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    with pytest.raises(ValidationError):
        enroll("   ", "secret", path=vault)
    assert not vault.exists()


def test_unlock_missing_vault(tmp_path: Path) -> None:
    vault = tmp_path / "missing.vl"
    with pytest.raises(NoVaultError, match="No vault yet — enroll first"):
        unlock("anything", path=vault)

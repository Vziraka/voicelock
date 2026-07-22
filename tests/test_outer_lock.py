"""Outer-lock passphrase seal / open / REJECT tests (temp path only)."""

from __future__ import annotations

from pathlib import Path

import pytest

from voicelock.vault import AuthError, enroll, unlock


def test_unlock_right_passphrase_returns_name(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada Lovelace", "correct-horse-battery", path=vault)
    assert unlock("correct-horse-battery", path=vault) == "Ada Lovelace"


def test_unlock_wrong_passphrase_rejects(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse-battery", path=vault)
    with pytest.raises(AuthError):
        unlock("wrong-passphrase", path=vault)

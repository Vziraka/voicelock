"""BoothApi enroll/unlock bridge tests (temp vault path; no live window)."""

from __future__ import annotations

from pathlib import Path

from voicelock.app import BoothApi


def test_bridge_enroll_unlock_roundtrip(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    api = BoothApi(vault_path=vault)
    enrolled = api.enroll({"name": "Ada", "passphrase": "correct-horse"})
    assert enrolled["ok"] is True
    assert vault.is_file()
    assert vault.read_bytes()[:4] == b"VLCK"

    opened = api.unlock({"passphrase": "correct-horse"})
    assert opened["ok"] is True
    assert opened["name"] == "Ada"


def test_bridge_wrong_passphrase_rejects(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    api = BoothApi(vault_path=vault)
    api.enroll({"name": "Ada", "passphrase": "correct-horse"})
    rejected = api.unlock({"passphrase": "nope"})
    assert rejected["ok"] is False
    assert rejected["error"] == "auth"


def test_bridge_no_vault(tmp_path: Path) -> None:
    api = BoothApi(vault_path=tmp_path / "missing.vl")
    result = api.unlock({"passphrase": "anything"})
    assert result["ok"] is False
    assert result["error"] == "no_vault"


def test_bridge_empty_enroll_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    api = BoothApi(vault_path=vault)
    result = api.enroll({"name": "", "passphrase": "x"})
    assert result["ok"] is False
    assert result["error"] == "validation"
    assert not vault.exists()


def test_bridge_re_enroll_needs_confirm(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    api = BoothApi(vault_path=vault)
    assert api.enroll({"name": "Ada", "passphrase": "one"})["ok"] is True
    blocked = api.enroll({"name": "Bea", "passphrase": "two"})
    assert blocked["needs_confirm"] is True
    overwritten = api.enroll(
        {"name": "Bea", "passphrase": "two", "overwrite": True},
    )
    assert overwritten["ok"] is True
    assert api.unlock({"passphrase": "two"})["name"] == "Bea"

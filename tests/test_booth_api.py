"""BoothApi enroll/unlock + voiceprint bridge tests (temp paths; no live window)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from voicelock.app import BoothApi
from voicelock.voiceprint import load_wav

FIXTURES = Path(__file__).parent / "fixtures" / "voiceprint"


class _StubCapture:
    """Minimal capture exposing the PCM buffer the voiceprint bridge reads."""

    def __init__(self) -> None:
        self._buf = np.zeros(0, dtype=np.float32)

    def set(self, audio: np.ndarray) -> None:
        self._buf = np.asarray(audio, dtype=np.float32)

    def pcm_buffer(self) -> np.ndarray:
        return self._buf


def _fx(name: str) -> np.ndarray:
    return load_wav(FIXTURES / name)


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


def test_bridge_set_reference_then_compare_separates_speakers(tmp_path: Path) -> None:
    ref = tmp_path / "voiceprint.ref"
    cap = _StubCapture()
    api = BoothApi(capture=cap, ref_path=ref)

    cap.set(_fx("speakerA_take1.wav"))
    r1 = api.set_reference()
    assert r1["ok"] is True and r1["done"] is False and r1["progress"] == 1
    cap.set(_fx("speakerA_take2.wav"))
    assert api.set_reference()["progress"] == 2
    cap.set(_fx("speakerA_take3.wav"))
    r3 = api.set_reference()
    assert r3["ok"] is True and r3["done"] is True
    assert ref.is_file()

    cap.set(_fx("speakerA_live.wav"))
    same = api.compare()
    assert same["ok"] is True and same["band"] == "accept"

    cap.set(_fx("speakerB.wav"))
    diff = api.compare()
    assert diff["ok"] is True and diff["band"] == "reject"


def test_bridge_set_reference_rejects_short_take(tmp_path: Path) -> None:
    ref = tmp_path / "voiceprint.ref"
    cap = _StubCapture()
    api = BoothApi(capture=cap, ref_path=ref)
    cap.set(_fx("too_short.wav"))
    result = api.set_reference()
    assert result["ok"] is False
    assert result["error"] == "need_more_audio"
    assert result["progress"] == 0
    assert not ref.exists()


def test_bridge_compare_without_reference(tmp_path: Path) -> None:
    cap = _StubCapture()
    api = BoothApi(capture=cap, ref_path=tmp_path / "none.ref")
    cap.set(_fx("speakerA_live.wav"))
    result = api.compare()
    assert result["ok"] is False
    assert result["error"] == "no_reference"


def test_bridge_reset_reference_clears_a_set_reference(tmp_path: Path) -> None:
    ref = tmp_path / "voiceprint.ref"
    cap = _StubCapture()
    api = BoothApi(capture=cap, ref_path=ref)
    for name in ("speakerA_take1.wav", "speakerA_take2.wav", "speakerA_take3.wav"):
        cap.set(_fx(name))
        api.set_reference()
    assert ref.is_file()

    assert api.reset_reference()["ok"] is True
    assert not ref.exists()

    cap.set(_fx("speakerA_live.wav"))
    after = api.compare()
    assert after["ok"] is False
    assert after["error"] == "no_reference"


def test_bridge_reset_reference_is_noop_and_clears_in_progress(tmp_path: Path) -> None:
    ref = tmp_path / "voiceprint.ref"
    cap = _StubCapture()
    api = BoothApi(capture=cap, ref_path=ref)
    cap.set(_fx("speakerA_take1.wav"))
    assert api.set_reference()["progress"] == 1  # one half-finished take

    assert api.reset_reference()["ok"] is True  # no file yet -> no-op; clears takes
    assert not ref.exists()

    cap.set(_fx("speakerA_take1.wav"))
    assert api.set_reference()["progress"] == 1  # progress restarted from a clean slate

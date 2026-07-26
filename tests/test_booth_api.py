"""BoothApi enroll/unlock + voiceprint bridge tests (temp paths; no live window)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from voicelock.app import MIN_LOCK_SECONDS, BoothApi, lock_voiceprint
from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.voiceprint import (
    ACCEPT_CUTOFF,
    MIN_SPEECH_SECONDS,
    SAMPLE_RATE,
    NeedMoreAudioError,
    cosine_distance,
    embed,
    load_wav,
)

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


def _bank_enrollment(api: BoothApi, cap: _StubCapture) -> None:
    """Record the five enrollment sentences through the bridge."""
    for index in range(1, ENROLLMENT_TAKES + 1):
        cap.set(_fx(f"speakerA_enroll{index}.wav"))
        assert api.enroll_take()["ok"] is True


def _enrolled_booth(tmp_path: Path) -> tuple[BoothApi, _StubCapture, Path]:
    vault = tmp_path / "vault.vl"
    cap = _StubCapture()
    api = BoothApi(capture=cap, vault_path=vault, ref_path=tmp_path / "voiceprint.ref")
    _bank_enrollment(api, cap)
    assert api.enroll({"name": "Ada", "passphrase": "correct-horse"})["ok"] is True
    return api, cap, vault


def test_bridge_enroll_unlock_roundtrip(tmp_path: Path) -> None:
    api, cap, vault = _enrolled_booth(tmp_path)
    assert vault.is_file()
    assert vault.read_bytes()[:4] == b"VLCK"
    assert vault.read_bytes()[4] == 2  # nested v2 layout

    cap.set(_fx("speakerA_live.wav"))
    opened = api.unlock({"passphrase": "correct-horse"})
    assert opened["ok"] is True
    assert opened["name"] == "Ada"


def test_bridge_wrong_passphrase_rejects(tmp_path: Path) -> None:
    api, cap, _ = _enrolled_booth(tmp_path)
    cap.set(_fx("speakerA_live.wav"))
    rejected = api.unlock({"passphrase": "nope"})
    assert rejected["ok"] is False
    assert rejected["error"] == "auth_outer"
    assert "name" not in rejected


def test_bridge_wrong_voice_rejects_distinctly(tmp_path: Path) -> None:
    """The demo's point: wrong passphrase and wrong voice never read the same."""
    api, cap, _ = _enrolled_booth(tmp_path)
    cap.set(_fx("speakerB.wav"))
    rejected = api.unlock({"passphrase": "correct-horse"})
    assert rejected["ok"] is False
    assert rejected["error"] == "auth_voice"
    assert "name" not in rejected


def test_bridge_enroll_take_rejects_a_short_take(tmp_path: Path) -> None:
    cap = _StubCapture()
    api = BoothApi(capture=cap, vault_path=tmp_path / "vault.vl")
    cap.set(_fx("speakerA_enroll1.wav"))
    assert api.enroll_take()["progress"] == 1
    cap.set(_fx("too_short.wav"))
    rejected = api.enroll_take()
    assert rejected["ok"] is False
    assert rejected["error"] == "need_more_audio"
    assert rejected["progress"] == 1  # the bad take did not advance progress


def test_reset_enroll_takes_discards_an_abandoned_run(tmp_path: Path) -> None:
    """An abandoned enrollment must not leak takes into the next one.

    Without this the bridge would keep the takes banked before a Cancel, and the
    next enrollment would seal the vault from those abandoned takes plus new ones
    — binding the middle key partly to audio the user thought they discarded.
    """
    cap = _StubCapture()
    api = BoothApi(capture=cap, vault_path=tmp_path / "vault.vl")

    cap.set(_fx("speakerA_enroll1.wav"))
    api.enroll_take()
    cap.set(_fx("speakerA_enroll2.wav"))
    assert api.enroll_take()["progress"] == 2

    assert api.reset_enroll_takes() == {"ok": True, "progress": 0, "needed": ENROLLMENT_TAKES}

    # The next take starts the count over, so the UI's dots and the bridge agree.
    cap.set(_fx("speakerA_enroll3.wav"))
    assert api.enroll_take()["progress"] == 1


def test_enroll_after_reset_uses_only_the_new_takes(tmp_path: Path) -> None:
    """The vault is sealed from the post-reset takes, not the abandoned ones."""
    cap = _StubCapture()
    api = BoothApi(capture=cap, vault_path=tmp_path / "vault.vl")

    cap.set(_fx("speakerB.wav"))  # an abandoned run by a different speaker
    api.enroll_take()
    api.reset_enroll_takes()

    _bank_enrollment(api, cap)  # a full, clean run by speaker A
    assert api.enroll({"name": "Ada", "passphrase": "correct-horse"})["ok"] is True

    cap.set(_fx("speakerA_live.wav"))
    assert api.unlock({"passphrase": "correct-horse"})["name"] == "Ada"


def test_bridge_enroll_without_voice_takes_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    api = BoothApi(vault_path=vault)
    result = api.enroll({"name": "Ada", "passphrase": "correct-horse"})
    assert result["ok"] is False
    assert result["error"] == "need_voice_takes"
    assert not vault.exists()


def test_bridge_no_vault(tmp_path: Path) -> None:
    api = BoothApi(vault_path=tmp_path / "missing.vl")
    result = api.unlock({"passphrase": "anything"})
    assert result["ok"] is False
    assert result["error"] == "no_vault"


def test_bridge_legacy_v1_vault(tmp_path: Path) -> None:
    api, cap, vault = _enrolled_booth(tmp_path)
    raw = bytearray(vault.read_bytes())
    raw[4] = 1  # stamp it back to the F2 format version
    vault.write_bytes(bytes(raw))

    cap.set(_fx("speakerA_live.wav"))
    result = api.unlock({"passphrase": "correct-horse"})
    assert result["ok"] is False
    assert result["error"] == "legacy_vault"


def test_bridge_empty_enroll_refuses(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    cap = _StubCapture()
    api = BoothApi(capture=cap, vault_path=vault)
    _bank_enrollment(api, cap)
    result = api.enroll({"name": "", "passphrase": "x"})
    assert result["ok"] is False
    assert result["error"] == "validation"
    assert not vault.exists()


def test_bridge_re_enroll_needs_confirm(tmp_path: Path) -> None:
    api, cap, vault = _enrolled_booth(tmp_path)

    _bank_enrollment(api, cap)
    blocked = api.enroll({"name": "Bea", "passphrase": "two"})
    assert blocked["needs_confirm"] is True

    overwritten = api.enroll({"name": "Bea", "passphrase": "two", "overwrite": True})
    assert overwritten["ok"] is True

    cap.set(_fx("speakerA_live.wav"))
    assert api.unlock({"passphrase": "two"})["name"] == "Bea"


# --- lever 5: raised lock floor + window-averaged embedding -------------------
def test_lock_take_is_the_average_of_overlapping_windows() -> None:
    """A lock take is a window average, not one point sample."""
    audio = _fx("speakerA_live.wav")
    averaged = lock_voiceprint(audio)
    single = embed(audio)

    assert averaged.shape == single.shape
    assert np.isclose(np.linalg.norm(averaged), 1.0)
    # It really is a different estimate — if this ever equals the point sample,
    # the averaging has been silently bypassed.
    assert not np.allclose(averaged, single)
    # ...but it still describes the same speaker, so it stays close.
    assert cosine_distance(averaged, single) < ACCEPT_CUTOFF


def test_lock_floor_is_higher_than_the_f3_diagnostic_floor() -> None:
    """A clip good enough for the F3 meter can still be too thin for the lock.

    This is the whole point of the raised floor: `voiceprint.MIN_SPEECH_SECONDS`
    (0.4 s) governs the diagnostic panel, `MIN_LOCK_SECONDS` (1.2 s) governs
    anything that keys the vault. The same recording must be accepted by one and
    refused by the other, or the two floors have silently merged.
    """
    assert MIN_LOCK_SECONDS > MIN_SPEECH_SECONDS

    middling = _fx("speakerA_live.wav")[: int(0.8 * SAMPLE_RATE)]
    assert MIN_SPEECH_SECONDS * SAMPLE_RATE < middling.size < MIN_LOCK_SECONDS * SAMPLE_RATE

    # The F3 diagnostic accepts it...
    embed(middling)
    # ...and the lock path does not.
    with pytest.raises(NeedMoreAudioError):
        lock_voiceprint(middling)


def test_lock_floor_applies_to_both_enroll_and_unlock(tmp_path: Path) -> None:
    """Lever 5 is two-sided — the raised floor guards enrollment and unlock alike."""
    cap = _StubCapture()
    middling = _fx("speakerA_live.wav")[: int(0.8 * SAMPLE_RATE)]

    api, cap_enrolled, _ = _enrolled_booth(tmp_path)
    cap_enrolled.set(middling)
    assert api.unlock({"passphrase": "correct-horse"})["error"] == "need_more_audio"

    fresh = BoothApi(capture=cap, vault_path=tmp_path / "other.vl")
    cap.set(middling)
    banked = fresh.enroll_take()
    assert banked["ok"] is False
    assert banked["error"] == "need_more_audio"
    assert banked["progress"] == 0


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

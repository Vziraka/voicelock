"""BoothApi enroll/unlock + voiceprint bridge tests (temp paths; no live window)."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

from voicelock.app import MIN_LOCK_SECONDS, BoothApi, lock_voiceprint
from voicelock.capture import CaptureStatus
from voicelock.facedetect import FaceStatus, FrameResult
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


class _StubFace:
    """Stands in for FaceEngine — records lifecycle calls, opens no device."""

    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.status = FaceStatus.IDLE
        self.error_message: str | None = None
        self.starts = 0
        self.stops = 0
        self.on_frame = None

    def start(self, on_frame) -> None:
        self.starts += 1
        self.on_frame = on_frame
        if self.fail:
            self.status = FaceStatus.ERROR
            self.error_message = "No camera available"
            return
        self.status = FaceStatus.RUNNING

    def stop(self) -> None:
        self.stops += 1
        if self.status == FaceStatus.RUNNING:
            self.status = FaceStatus.IDLE


class _StubRecordingCapture:
    """Capture surface the record path uses, with no microphone behind it."""

    def __init__(self) -> None:
        self.status = CaptureStatus.IDLE
        self.error_message: str | None = None
        self.levels: list[float] = []
        self.started = 0
        self.stopped = 0

    @property
    def is_recording(self) -> bool:
        return self.status == CaptureStatus.RECORDING

    def start(self) -> None:
        self.started += 1
        self.status = CaptureStatus.RECORDING

    def stop(self) -> np.ndarray:
        self.stopped += 1
        self.status = CaptureStatus.IDLE
        return np.zeros(320, dtype=np.float32)

    def pump(self, frames: np.ndarray | None = None) -> None:
        del frames

    def pcm_buffer(self) -> np.ndarray:
        return np.zeros(320, dtype=np.float32)


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


# ---------------------------------------------------------------------------
# F5 — camera wiring
# ---------------------------------------------------------------------------


def _recording_booth(tmp_path: Path, *, camera_fails: bool = False):
    cap = _StubRecordingCapture()
    face = _StubFace(fail=camera_fails)
    api = BoothApi(
        capture=cap,
        vault_path=tmp_path / "vault.vl",
        ref_path=tmp_path / "voiceprint.ref",
        face=face,
    )
    return api, cap, face


def test_start_record_starts_the_camera_and_stop_record_stops_it(tmp_path: Path) -> None:
    api, cap, face = _recording_booth(tmp_path)

    assert api.start_record()["ok"] is True
    assert face.starts == 1
    assert face.status == FaceStatus.RUNNING
    assert cap.is_recording

    assert api.stop_record()["ok"] is True
    assert face.stops == 1
    assert face.status == FaceStatus.IDLE
    assert not cap.is_recording


def test_a_camera_failure_does_not_prevent_audio_recording(tmp_path: Path) -> None:
    """The microphone is the point of a take; the preview is a companion."""
    api, cap, face = _recording_booth(tmp_path, camera_fails=True)

    result = api.start_record()

    assert result["ok"] is True, "a broken webcam must not fail the take"
    assert cap.started == 1, "capture must still be running"
    assert cap.is_recording
    assert face.status == FaceStatus.ERROR

    assert api.stop_record()["ok"] is True
    assert face.stops == 1, "a failed camera must still be stopped/released"


def test_a_second_record_after_stop_starts_the_camera_again(tmp_path: Path) -> None:
    api, _, face = _recording_booth(tmp_path)

    api.start_record()
    api.stop_record()
    api.start_record()
    api.stop_record()

    assert face.starts == 2
    assert face.stops == 2


def test_shutdown_releases_the_camera(tmp_path: Path) -> None:
    """Closing the window must not leave the webcam light on."""
    api, _, face = _recording_booth(tmp_path)
    api.start_record()

    api.shutdown()

    assert face.stops == 1
    assert face.status == FaceStatus.IDLE


def test_shutdown_is_safe_when_nothing_was_ever_started(tmp_path: Path) -> None:
    api, _, face = _recording_booth(tmp_path)

    api.shutdown()

    assert face.stops == 1  # stop() is safe to call cold


def test_shutdown_does_not_cancel_the_window_close(tmp_path: Path) -> None:
    """pywebview's `closing` event cancels the close if a handler returns False.

    `Event.set` collects handler return values and cancels on `v is False`, so a
    handler that returned False would trap the user in a window it also just
    released the camera out from under. Returning None is the contract.
    """
    api, _, _ = _recording_booth(tmp_path)

    assert api.shutdown() is not False


class _SelfStoppingCapture(_StubRecordingCapture):
    """Ends its own take mid-pump, the way F4.5's 30s soft cap does."""

    def __init__(self, pumps_before_stop: int = 1) -> None:
        super().__init__()
        self._remaining = pumps_before_stop

    def pump(self, frames: np.ndarray | None = None) -> None:
        del frames
        if self.status != CaptureStatus.RECORDING:
            return
        self._remaining -= 1
        if self._remaining <= 0:
            self.status = CaptureStatus.IDLE  # the soft cap firing


def test_the_30s_auto_stop_releases_the_camera_too(tmp_path: Path) -> None:
    """A take can end without anyone pressing Stop — F4.5's soft cap.

    Without this the webcam light stays on and the preview keeps streaming
    after the recording is over, which is the defect the spec headlines.
    """
    cap = _SelfStoppingCapture()
    face = _StubFace()
    api = BoothApi(
        capture=cap,
        vault_path=tmp_path / "vault.vl",
        ref_path=tmp_path / "voiceprint.ref",
        face=face,
    )
    scripts: list[str] = []
    api._eval = scripts.append  # type: ignore[method-assign]

    assert api.start_record()["ok"] is True
    assert face.starts == 1  # the take may already have self-ended by now

    # The pump thread notices the take ended by itself. Wait on the observable
    # end state — the page being told to go idle — rather than on a counter the
    # stub bumps part-way through its own stop().
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline and not any("setFaceIdle" in s for s in scripts):
        time.sleep(0.01)

    assert face.stops == 1, "the camera was left running after the take self-ended"
    assert face.status == FaceStatus.IDLE
    assert any("setFaceIdle" in s for s in scripts), "the smiley never came back"
    assert any("onCaptureEnded" in s for s in scripts), "the take never ended"


def test_frames_are_pushed_to_the_page_as_a_data_uri(tmp_path: Path) -> None:
    """The engine's callback is what reaches the page, unaltered."""
    api, _, face = _recording_booth(tmp_path)
    scripts: list[str] = []
    api._eval = scripts.append  # type: ignore[method-assign]

    api.start_record()
    face.on_frame(FrameResult(data_uri="data:image/jpeg;base64,AAAA", landmarks=[]))

    pushed = [s for s in scripts if "setFaceFrame" in s]
    assert pushed, "no frame reached the page"
    assert "data:image/jpeg;base64,AAAA" in pushed[0]

    api.stop_record()
    assert any("setFaceIdle" in s for s in scripts), "the smiley never came back"

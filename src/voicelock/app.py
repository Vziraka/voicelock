"""pywebview Booth host — bridges UI to capture/playback and outer lock."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import numpy as np
import webview

from voicelock import challenge, facelock, faceprint, lipsync, voiceprint
from voicelock.capture import CaptureEngine, CaptureStatus, DTYPE, MAX_SECONDS, SAMPLE_RATE
from voicelock.facedetect import FRAME_INTERVAL, FaceEngine, FaceStatus, FrameResult
from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.playback import PlaybackEngine
from voicelock.vault import (
    AuthError,
    FaceAuthError,
    LegacyVaultError,
    NoVaultError,
    ValidationError,
    VoiceAuthError,
    default_vault_path,
    enroll as vault_enroll,
    unlock as vault_unlock,
)

UI_PATH = Path(__file__).resolve().parent / "ui" / "index.html"

# --- Lever 5: capture quality for the LOCK path (spec §3, amendment 2026-07-26) --
# The lock asks for meaningfully more speech than F3's 0.4 s diagnostic floor. A
# lock take is also embedded as the average of several overlapping windows rather
# than one point sample, because enrollment averages five takes while unlock has
# only one — that made unlock the noisier half of the comparison and inflated the
# reconcile error rate. Both sides use this path, so both are averaged.
#
# These floors are deliberately NOT shared with `voiceprint`: the F3 diagnostic
# meter keeps its own 0.4 s floor (spec §3 says leave that panel as-is), so the
# same recording can be good enough to show a match distance yet too thin to key
# a lock with.
MIN_LOCK_SECONDS = 1.2
LOCK_WINDOWS = 3
LOCK_WINDOW_FRACTION = 0.7

# --- F8: the single AV capture liveness (challenge + lip-sync) relies on -------
# Estimated, not guessed (project.md's dry-run-before-pinning guardrail) --
# but this environment has no live speaker to time, so the estimate is
# word-count-based rather than a stopwatch reading, disclosed as such:
# CHALLENGE_PHRASES' longest entries are 6 words; at a slow, deliberate
# 1.5 words/sec that is ~4.0 s of pure speech, doubled to ~8.0 s for
# hesitation/lead-in margin, rounded up to a comfortable 10.0 s. Replaces
# spec §2 Q2's provisional "~6-8 s".
LIVENESS_CAPTURE_CEILING_SECONDS = 10.0


_ENVELOPE_HOP = int(SAMPLE_RATE * FRAME_INTERVAL)


def _audio_envelope(audio: np.ndarray) -> np.ndarray:
    """Fixed-hop RMS envelope, one value per video-frame interval.

    A deterministic per-audio-sample grid, unlike the camera's own frame
    delivery (real capture drops frames under load — drop-don't-queue
    pacing — so it is not a guaranteed fixed rate). ``_resample_mouth_series``
    is what actually lines the two series up, by timestamp rather than by
    index — the same fixed-window-RMS technique that already produces the
    Visualizer's levels, just re-run at a hop chosen for this grid instead
    of PortAudio's own irregular per-callback chunk boundaries.
    """
    hop = _ENVELOPE_HOP
    sig = np.asarray(audio, dtype=np.float64).reshape(-1)
    frames = sig.size // hop
    if frames == 0:
        return np.zeros(0, dtype=np.float64)
    return np.array(
        [
            float(np.sqrt(np.mean(np.square(sig[index * hop : (index + 1) * hop]))))
            for index in range(frames)
        ]
    )


def _resample_mouth_series(
    mouth_series: np.ndarray, mouth_timestamps: np.ndarray, envelope_size: int
) -> np.ndarray:
    """Resample retained mouth-aperture samples onto the audio envelope's grid.

    ``_push_face_frame`` timestamps each retained sample against wall-clock
    time since capture start (real camera delivery is not a fixed rate), so
    index *i* in ``mouth_series`` is generally NOT the same instant as
    ``envelope[i]``. Linear interpolation against those real timestamps
    restores that alignment: each envelope index is mapped to the time at
    the CENTRE of its RMS window (matching how the envelope itself sums
    over ``[i*hop, (i+1)*hop)``), and ``np.interp`` gives a mouth-aperture
    value at that exact instant. Timestamps outside the retained range clamp
    to the nearest real sample (``np.interp``'s default), a reasonable
    fallback for a capture that starts or ends a touch late/early on either
    side.
    """
    if mouth_series.size == 0 or envelope_size == 0:
        return np.zeros(0, dtype=np.float64)
    grid = (np.arange(envelope_size, dtype=np.float64) + 0.5) * (_ENVELOPE_HOP / SAMPLE_RATE)
    return np.interp(grid, mouth_timestamps, mouth_series)


def lock_voiceprint(audio: np.ndarray) -> np.ndarray:
    """Embed a lock take as the average of overlapping windows.

    Raises ``voiceprint.NeedMoreAudioError`` when the take is under
    ``MIN_LOCK_SECONDS`` — the caller re-records, reusing F3's "need more audio"
    signal and copy against this raised floor.
    """
    signal = np.asarray(audio, dtype=DTYPE).reshape(-1)
    if signal.size < int(MIN_LOCK_SECONDS * SAMPLE_RATE):
        raise voiceprint.NeedMoreAudioError("need more audio")

    window = min(
        signal.size,
        max(int(MIN_LOCK_SECONDS * SAMPLE_RATE), int(signal.size * LOCK_WINDOW_FRACTION)),
    )
    # A take sitting exactly on the floor gives hop 0, so the three windows are
    # the same audio — averaging them is a no-op rather than a special case.
    hop = (signal.size - window) // (LOCK_WINDOWS - 1)
    embeddings = [
        voiceprint.embed(signal[index * hop : index * hop + window])
        for index in range(LOCK_WINDOWS)
    ]
    averaged = np.mean(embeddings, axis=0)
    return averaged / np.linalg.norm(averaged)


class BoothApi:
    """JS ↔ Python bridge for record / stop / play and vault enroll / unlock."""

    def __init__(
        self,
        capture: CaptureEngine | None = None,
        playback: PlaybackEngine | None = None,
        vault_path: Path | None = None,
        ref_path: Path | None = None,
        face: FaceEngine | None = None,
        face_ref_path: Path | None = None,
    ) -> None:
        self.capture = capture or CaptureEngine()
        self.playback = playback or PlaybackEngine()
        self.vault_path = vault_path if vault_path is not None else default_vault_path()
        self.ref_path = ref_path if ref_path is not None else voiceprint.default_reference_path()
        self.face_ref_path = (
            face_ref_path if face_ref_path is not None else faceprint.default_reference_path()
        )
        self._face_reference_takes: list[np.ndarray] = []
        self._reference_takes: list[np.ndarray] = []
        # F4 enrollment voiceprints, banked one per sentence by enroll_take().
        # Kept separate from _reference_takes: that list belongs to the F3
        # diagnostic panel, which spec §3 keeps as an independent thing.
        self._enroll_voiceprints: list[np.ndarray] = []
        # F7 enrollment faceprints, banked one per burst frame by
        # enroll_face_take(). Kept separate from _face_reference_takes: that
        # list belongs to F6's diagnostic panel, an independent thing (spec §3
        # Q4) that never reads or writes these.
        self._enroll_faceprints: list[np.ndarray] = []
        self._window: Any = None
        self._pumping = False
        self._pump_thread: threading.Thread | None = None
        self._play_watch: threading.Thread | None = None
        self.face = face if face is not None else FaceEngine()
        # F8 liveness: armed only during start_unlock_capture()..
        # stop_unlock_capture(), never during enroll's start_record()/
        # stop_record() — a wholly separate capture pair (plan.md decision 6).
        self._retain_landmarks: bool = False
        self._liveness_mouth_series: list[float] = []
        # Wall-clock seconds since start_unlock_capture(), one per retained
        # mouth-aperture sample -- camera frames do NOT arrive on a
        # guaranteed fixed grid (drop-don't-queue pacing, real processing
        # load), so _liveness_passes() resamples onto the audio envelope's
        # grid by timestamp rather than assuming index-for-index alignment.
        self._liveness_mouth_timestamps: list[float] = []
        self._liveness_capture_started_at: float | None = None
        # The phrase the Booth is currently displaying; None until
        # new_challenge() is first called (plan.md decision 7).
        self._current_challenge: str | None = None

    def bind_window(self, window: Any) -> None:
        self._window = window

    def ready(self) -> dict[str, Any]:
        """Probe the mic once the Booth has loaded."""
        error = self._probe_mic()
        if error is not None:
            self._push_mic_error(error)
            return {"ok": False, "error": error}
        return {"ok": True}

    def enroll_take(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Bank the last captured take as one of the enrollment sentences.

        Called once per recorded sentence until ``ENROLLMENT_TAKES`` are banked;
        ``enroll`` then seals the vault from them. A too-short or silent take is
        rejected with ``need_more_audio`` and does NOT advance progress — the
        caller re-records just that sentence, with no penalty.
        """
        buf = self.capture.pcm_buffer()
        try:
            embedding = lock_voiceprint(buf)
        except voiceprint.NeedMoreAudioError:
            return {
                "ok": False,
                "error": "need_more_audio",
                "progress": len(self._enroll_voiceprints),
            }
        self._enroll_voiceprints.append(embedding)
        progress = len(self._enroll_voiceprints)
        return {
            "ok": True,
            "done": progress >= ENROLLMENT_TAKES,
            "progress": progress,
            "needed": ENROLLMENT_TAKES,
        }

    def reset_enroll_takes(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Discard a half-finished enrollment run.

        The Booth calls this whenever the enroll panel is opened or cancelled.
        Without it, takes banked during an abandoned attempt would survive and be
        sealed into the next vault alongside the new ones — so the middle key
        could end up bound partly to whatever was recorded and thrown away,
        including a different speaker's voice.
        """
        self._enroll_voiceprints = []
        return {"ok": True, "progress": 0, "needed": ENROLLMENT_TAKES}

    def enroll_face_take(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Bank the last camera frame as one of the enrollment faces.

        Called once per press until ``facelock.ENROLLMENT_TAKES`` are banked;
        ``enroll`` then seals the vault's inner lock from them. A frame with
        no face (or no camera frame yet) is rejected with ``no_face`` and does
        NOT advance — mirrors ``enroll_take``'s ``need_more_audio`` shape for
        the voice path.
        """
        frame = self.face.last_frame
        if frame is None:
            return {
                "ok": False,
                "error": "no_face",
                "progress": len(self._enroll_faceprints),
            }
        try:
            embedding = faceprint.embed_frame(frame)
        except faceprint.NoFaceError:
            return {
                "ok": False,
                "error": "no_face",
                "progress": len(self._enroll_faceprints),
            }
        self._enroll_faceprints.append(embedding)
        progress = len(self._enroll_faceprints)
        return {
            "ok": True,
            "done": progress >= facelock.ENROLLMENT_TAKES,
            "progress": progress,
            "needed": facelock.ENROLLMENT_TAKES,
        }

    def reset_enroll_face_takes(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Discard a half-finished face-enrollment run.

        Mirrors ``reset_enroll_takes`` exactly, for the same reason: without
        it, an abandoned run's banked faces would survive into the next
        enrollment's inner key, possibly a different person's.
        """
        self._enroll_faceprints = []
        return {"ok": True, "progress": 0, "needed": facelock.ENROLLMENT_TAKES}

    def enroll(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Seal (or overwrite) the Vault with name + passphrase + voice + face."""
        data = payload or {}
        name = str(data.get("name", "") or "")
        passphrase = str(data.get("passphrase", "") or "")
        overwrite = bool(data.get("overwrite", False))

        if self.vault_path.is_file() and not overwrite:
            return {"ok": False, "needs_confirm": True}

        if len(self._enroll_voiceprints) < ENROLLMENT_TAKES:
            return {
                "ok": False,
                "error": "need_voice_takes",
                "progress": len(self._enroll_voiceprints),
                "needed": ENROLLMENT_TAKES,
            }

        if len(self._enroll_faceprints) < facelock.ENROLLMENT_TAKES:
            return {
                "ok": False,
                "error": "need_face_takes",
                "progress": len(self._enroll_faceprints),
                "needed": facelock.ENROLLMENT_TAKES,
            }

        voiceprints = self._enroll_voiceprints[:ENROLLMENT_TAKES]
        faceprints = self._enroll_faceprints[: facelock.ENROLLMENT_TAKES]
        try:
            vault_enroll(name, passphrase, voiceprints, faceprints, path=self.vault_path)
        except ValidationError as exc:
            return {
                "ok": False,
                "error": "validation",
                "message": str(exc) or "Name and passphrase are required",
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc) or "Enroll failed"}
        # A sealed vault consumes the run.
        self._enroll_voiceprints = []
        self._enroll_faceprints = []
        return {"ok": True, "name": name.strip(), "path": str(self.vault_path)}

    def new_challenge(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Pick a fresh random challenge phrase and store it for the next unlock.

        Called by the UI whenever the Unlock panel becomes active and again
        after each completed attempt (plan.md decision 7), so the
        no-immediate-repeat property (``challenge.pick_challenge``) holds
        across real usage, not just within one bridge instance's lifetime.
        Python is authoritative for the phrase shown — JS renders only.
        """
        phrase = challenge.pick_challenge(previous=self._current_challenge)
        self._current_challenge = phrase
        return {"ok": True, "phrase": phrase}

    def start_unlock_capture(self) -> dict[str, Any]:
        """Start the single AV capture liveness (and unlock) relies on.

        Distinct from ``start_record()`` (enroll voice/face keep using that
        pair unmodified) — mirrors its camera-then-pump ordering and
        mic-failure-must-not-cost-the-take handling exactly, adding only:
        arm landmark retention + clear the mouth-aperture series, and cap
        this take at ``LIVENESS_CAPTURE_CEILING_SECONDS`` instead of the
        30 s enroll/diagnostic soft cap. ``capture.max_seconds`` is set only
        AFTER a mic failure is ruled out, so a failed attempt here can never
        leave a later enroll take capped at the (shorter) liveness ceiling.
        """
        if self.playback.is_playing:
            self.stop_playback()
        if self.capture.is_recording:
            return self.stop_unlock_capture()
        self._liveness_mouth_series = []
        self._liveness_mouth_timestamps = []
        self._retain_landmarks = True
        self.capture.start()
        if self.capture.status == CaptureStatus.ERROR:
            self._retain_landmarks = False
            error = self.capture.error_message or "No microphone available"
            self._push_mic_error(error)
            return {"ok": False, "error": error}
        self.capture.max_seconds = LIVENESS_CAPTURE_CEILING_SECONDS
        # Reference point for mouth-sample timestamps -- anchored here since
        # the audio envelope's own timeline (_audio_envelope) starts from
        # the beginning of the recorded PCM, i.e. right after capture.start().
        self._liveness_capture_started_at = time.monotonic()
        # Camera before pump, same reasoning as start_record(): the pump loop
        # is what notices a take ending and tears the camera down.
        self._start_camera()
        self._start_pump()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setRecording && "
            "window.voicelockBooth.setRecording(true)"
        )
        return {"ok": True}

    def stop_unlock_capture(self) -> dict[str, Any]:
        """Stop the AV capture, release the camera, and restore the mic's
        normal 30 s cap for whatever recording happens next."""
        if self.playback.is_playing:
            return self.stop_playback()
        self._stop_pump()
        self._stop_camera()
        buf = self.capture.stop()
        self.capture.max_seconds = MAX_SECONDS
        self._retain_landmarks = False
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setRecording && "
            "window.voicelockBooth.setRecording(false)"
        )
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setLevel && "
            "window.voicelockBooth.setLevel(0.11)"
        )
        return {"ok": True, "samples": int(buf.size)}

    def unlock(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Peel outer, middle, then inner — but only once liveness passes.

        Per spec Q6, the challenge-word-match and lip-sync checks run BEFORE
        any call into the vault layer: a failed liveness attempt makes ZERO
        calls to ``vault_unlock`` and learns nothing about whether the
        underlying voice/face would have matched. The four REJECT reasons
        stay visibly distinct: ``auth_liveness`` (new, this feature), then
        the existing ``auth_outer``, ``auth_voice``, ``auth_face``. No
        failure path returns a ``name``.
        """
        data = payload or {}
        passphrase = str(data.get("passphrase", "") or "")

        if not self.vault_path.is_file():
            return {"ok": False, "error": "no_vault"}

        try:
            voiceprint_vector = lock_voiceprint(self.capture.pcm_buffer())
        except voiceprint.NeedMoreAudioError:
            return {"ok": False, "error": "need_more_audio"}

        frame = self.face.last_frame
        if frame is None:
            return {"ok": False, "error": "no_face"}
        try:
            faceprint_vector = faceprint.embed_frame(frame)
        except faceprint.NoFaceError:
            return {"ok": False, "error": "no_face"}

        if not self._liveness_passes():
            return {"ok": False, "error": "auth_liveness"}

        try:
            name = vault_unlock(
                passphrase, voiceprint_vector, faceprint_vector, path=self.vault_path
            )
        except NoVaultError:
            return {"ok": False, "error": "no_vault"}
        except AuthError:
            return {"ok": False, "error": "auth_outer"}
        except VoiceAuthError:
            return {"ok": False, "error": "auth_voice"}
        except FaceAuthError:
            return {"ok": False, "error": "auth_face"}
        except LegacyVaultError:
            return {"ok": False, "error": "legacy_vault"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc) or "Unlock failed"}
        return {"ok": True, "name": name}

    def _liveness_passes(self) -> bool:
        """Both the spoken-word challenge AND the lip-sync check must pass.

        No challenge picked yet (``new_challenge()`` never called) fails
        closed rather than raising — a real UI always calls it before the
        Unlock panel is usable, but a bridge caller that skips it must not
        crash the app.
        """
        if self._current_challenge is None:
            return False
        audio = self.capture.pcm_buffer()
        challenge_ok = challenge.check(audio, self._current_challenge)
        envelope = _audio_envelope(audio)
        mouth_series = np.asarray(self._liveness_mouth_series, dtype=np.float64)
        mouth_timestamps = np.asarray(self._liveness_mouth_timestamps, dtype=np.float64)
        resampled_mouth = _resample_mouth_series(mouth_series, mouth_timestamps, envelope.size)
        sync_score = lipsync.score(resampled_mouth, envelope)
        return challenge_ok and lipsync.is_live(sync_score)

    def set_reference(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Consume the last captured take as one of the reference sentences.

        Called once per recorded sentence; after ``REFERENCE_TAKES`` valid takes
        the averaged reference is persisted. A too-short/silent take is rejected
        with ``need_more_audio`` and is not added — the caller re-records it.
        """
        buf = self.capture.pcm_buffer()
        try:
            voiceprint.embed(buf)  # validate this take before accepting it
        except voiceprint.NeedMoreAudioError:
            return {
                "ok": False,
                "error": "need_more_audio",
                "progress": len(self._reference_takes),
            }
        self._reference_takes.append(np.asarray(buf, dtype=DTYPE))
        progress = len(self._reference_takes)
        if progress < voiceprint.REFERENCE_TAKES:
            return {"ok": True, "done": False, "progress": progress}

        takes = self._reference_takes[: voiceprint.REFERENCE_TAKES]
        self._reference_takes = []
        try:
            voiceprint.set_reference(takes, path=self.ref_path)
        except voiceprint.VoiceprintError as exc:
            return {"ok": False, "error": str(exc) or "Set reference failed", "progress": 0}
        return {"ok": True, "done": True, "progress": voiceprint.REFERENCE_TAKES}

    def compare(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Match the last captured take against the stored reference voiceprint."""
        buf = self.capture.pcm_buffer()
        try:
            distance, band = voiceprint.compare(buf, path=self.ref_path)
        except voiceprint.NoReferenceError:
            return {"ok": False, "error": "no_reference"}
        except voiceprint.NeedMoreAudioError:
            return {"ok": False, "error": "need_more_audio"}
        return {"ok": True, "distance": distance, "band": band}

    def reset_reference(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Clear the stored reference voiceprint and any half-finished take run."""
        self._reference_takes = []
        self.ref_path.unlink(missing_ok=True)
        return {"ok": True}

    def set_face_reference(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Bank the last camera frame as one of the face reference takes.

        Called once per press until ``faceprint.REFERENCE_TAKES`` valid frames
        are banked; on the last one the averaged reference is persisted. A
        frame with no face (or no camera frame yet) is rejected with
        ``no_face`` and NOT added — mirrors ``set_reference``'s
        ``need_more_audio`` shape for the voice path.
        """
        frame = self.face.last_frame
        if frame is None:
            return {"ok": False, "error": "no_face", "progress": len(self._face_reference_takes)}
        try:
            faceprint.embed_frame(frame)  # validate this frame before accepting it
        except faceprint.NoFaceError:
            return {"ok": False, "error": "no_face", "progress": len(self._face_reference_takes)}
        self._face_reference_takes.append(frame)
        progress = len(self._face_reference_takes)
        if progress < faceprint.REFERENCE_TAKES:
            return {"ok": True, "done": False, "progress": progress}

        takes = self._face_reference_takes[: faceprint.REFERENCE_TAKES]
        self._face_reference_takes = []
        try:
            faceprint.set_reference(takes, path=self.face_ref_path)
        except faceprint.FaceprintError as exc:
            return {"ok": False, "error": str(exc) or "Set reference failed", "progress": 0}
        return {"ok": True, "done": True, "progress": faceprint.REFERENCE_TAKES}

    def compare_face(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Match the last camera frame against the stored reference faceprint.

        Called on a low fixed interval from JS, never from inside
        ``FaceEngine``'s 30 fps loop. The reference is checked first (cheap),
        mirroring ``voiceprint.compare``'s ordering, so a missing reference
        never costs a face embed.
        """
        try:
            reference = faceprint.load_reference(self.face_ref_path)
        except faceprint.NoReferenceError:
            return {"ok": False, "error": "no_reference"}
        frame = self.face.last_frame
        if frame is None:
            return {"ok": False, "error": "no_face"}
        try:
            live = faceprint.embed_frame(frame)
        except faceprint.NoFaceError:
            return {"ok": False, "error": "no_face"}
        distance = faceprint.compare(live, reference)
        return {"ok": True, "distance": distance, "band": faceprint.band_for(distance)}

    def reset_face_reference(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Clear the stored reference faceprint and any half-finished take run."""
        self._face_reference_takes = []
        self.face_ref_path.unlink(missing_ok=True)
        return {"ok": True}

    def start_record(self) -> dict[str, Any]:
        if self.playback.is_playing:
            self.stop_playback()
        if self.capture.is_recording:
            return self.stop_record()
        self.capture.start()
        if self.capture.status == CaptureStatus.ERROR:
            error = self.capture.error_message or "No microphone available"
            self._push_mic_error(error)
            return {"ok": False, "error": error}
        # Camera before pump: the pump loop is what notices a take ending and
        # tears the camera down, so it must not be able to run before the camera
        # has started. (Capture stays first of all — a camera failure must never
        # cost the take.)
        self._start_camera()
        self._start_pump()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setRecording && "
            "window.voicelockBooth.setRecording(true)"
        )
        return {"ok": True}

    def stop_record(self) -> dict[str, Any]:
        if self.playback.is_playing:
            return self.stop_playback()
        self._stop_pump()
        self._stop_camera()
        buf = self.capture.stop()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setRecording && "
            "window.voicelockBooth.setRecording(false)"
        )
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setLevel && "
            "window.voicelockBooth.setLevel(0.11)"
        )
        return {"ok": True, "samples": int(buf.size)}

    def play(self) -> dict[str, Any]:
        buf = self.capture.pcm_buffer()
        if buf.size == 0:
            return {"ok": False, "error": "Nothing to play yet"}
        try:
            self.playback.play_buffer(buf, block=False)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc) or "Playback failed"}
        self._start_play_watch()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setPlaying && "
            "window.voicelockBooth.setPlaying(true)"
        )
        return {"ok": True, "samples": int(buf.size), "playing": True}

    def stop_playback(self) -> dict[str, Any]:
        self.playback.stop()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setPlaying && "
            "window.voicelockBooth.setPlaying(false)"
        )
        return {"ok": True, "playing": False}

    def _probe_mic(self) -> str | None:
        try:
            stream = self.capture.open_input(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype=DTYPE,
            )
            try:
                stream.close()
            except Exception:  # noqa: BLE001
                pass
            return None
        except Exception as exc:  # noqa: BLE001
            from voicelock.capture import _mic_error_message

            return _mic_error_message(exc)

    def _start_pump(self) -> None:
        self._stop_pump()
        self._pumping = True
        thread = threading.Thread(target=self._pump_loop, name="voicelock-levels", daemon=True)
        self._pump_thread = thread
        thread.start()

    def _stop_pump(self) -> None:
        self._pumping = False
        thread = self._pump_thread
        self._pump_thread = None
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)

    def _pump_loop(self) -> None:
        while self._pumping:
            self.capture.pump()
            if not self.capture.is_recording:
                self._pumping = False
                # The take ended without anyone pressing Stop — F4.5's 30s soft
                # cap, or F8's shorter liveness ceiling. Release the camera here
                # too, or the webcam light stays on and the preview keeps
                # streaming after the recording is over. This path bypasses
                # stop_record()/stop_unlock_capture() entirely (it is what
                # notices the take ended, not something they call), so their
                # own F8 bookkeeping is repeated here — harmless for a plain
                # start_record() take, since both fields are already at their
                # rest values in that case.
                self._stop_camera()
                self.capture.max_seconds = MAX_SECONDS
                self._retain_landmarks = False
                samples = int(self.capture.pcm_buffer().size)
                self._eval(
                    "window.voicelockBooth && window.voicelockBooth.onCaptureEnded && "
                    f"window.voicelockBooth.onCaptureEnded({samples})"
                )
                break
            if self.capture.levels:
                level = float(self.capture.levels[-1])
                self._eval(
                    "window.voicelockBooth && window.voicelockBooth.setLevel && "
                    f"window.voicelockBooth.setLevel({level:.4f})"
                )
            time.sleep(0.05)

    def _start_play_watch(self) -> None:
        prior = self._play_watch
        if prior is not None and prior.is_alive():
            # Prior wait will exit after sd.stop(); don't join on the API thread.
            pass
        thread = threading.Thread(target=self._play_watch_loop, name="voicelock-play", daemon=True)
        self._play_watch = thread
        thread.start()

    def _play_watch_loop(self) -> None:
        try:
            self.playback.wait()
        except Exception:  # noqa: BLE001
            pass
        if not self.playback.interrupted:
            self.playback.completed = True
        self.playback.is_playing = False
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setPlaying && "
            "window.voicelockBooth.setPlaying(false)"
        )

    def _start_camera(self) -> None:
        """Start the FaceView preview. A camera failure must NOT fail the take.

        The microphone is the point of a recording; the preview is a companion.
        A broken or missing webcam surfaces its message the way a mic error
        does and leaves capture running.
        """
        self.face.start(self._push_face_frame)
        if self.face.status == FaceStatus.ERROR:
            self._push_mic_error(self.face.error_message or "No camera available")

    def _stop_camera(self) -> None:
        self.face.stop()
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setFaceIdle && "
            "window.voicelockBooth.setFaceIdle()"
        )

    def _push_face_frame(self, result: FrameResult) -> None:
        # Additive only: zero change to the composite/evaluate_js path below,
        # or to FaceEngine/facedetect.py (spec §4's F1-F7 engines constraint).
        # A faceless frame (no landmarks) is skipped, not appended as 0 —
        # lipsync.score() already tolerates a shorter mouth-aperture series.
        # Real camera delivery is NOT a guaranteed fixed-rate grid (dropped
        # frames under load), so each sample is timestamped and
        # _liveness_passes() resamples onto the audio envelope's own grid
        # rather than assuming index-for-index alignment.
        if self._retain_landmarks and result.landmarks and self._liveness_capture_started_at is not None:
            elapsed = time.monotonic() - self._liveness_capture_started_at
            self._liveness_mouth_series.append(lipsync.mouth_aperture(result.landmarks))
            self._liveness_mouth_timestamps.append(elapsed)
        # The data URI is base64 — no quote or backslash can appear in it, so it
        # needs no escaping the way a free-text error message does.
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.setFaceFrame && "
            f"window.voicelockBooth.setFaceFrame('{result.data_uri}')"
        )

    def shutdown(self) -> None:
        """Release devices when the window closes.

        A webcam light still on after the app exits is the same defect as one
        that never turned off on Stop. `FaceEngine.stop()` is safe to call twice
        and after a failed start, which is what lets this run unconditionally.

        The microphone is deliberately NOT stopped here. The spec scopes the
        close handler to the camera, an in-flight PortAudio stream is closed by
        process exit, and that has been the behaviour since F1 — this handler
        exists to fix the camera, not to quietly change the audio path.
        """
        self._stop_pump()
        self.face.stop()

    def _push_mic_error(self, message: str) -> None:
        safe = message.replace("\\", "\\\\").replace("'", "\\'")
        self._eval(
            "window.voicelockBooth && window.voicelockBooth.showMicError && "
            f"window.voicelockBooth.showMicError('{safe}')"
        )

    def _eval(self, script: str) -> None:
        window = self._window
        if window is None:
            return
        try:
            window.evaluate_js(script)
        except Exception:  # noqa: BLE001
            pass


def main() -> None:
    if not UI_PATH.is_file():
        raise SystemExit(f"Booth UI missing: {UI_PATH}")
    api = BoothApi()
    window = webview.create_window(
        "VoiceLock",
        url=UI_PATH.as_uri(),
        js_api=api,
        width=1100,
        height=740,
        min_size=(900, 600),
    )
    api.bind_window(window)
    # Closing the window must release the camera too — a stuck webcam light
    # after the app exits is the same defect as one that never went out on Stop.
    window.events.closing += api.shutdown
    webview.start()


if __name__ == "__main__":
    main()

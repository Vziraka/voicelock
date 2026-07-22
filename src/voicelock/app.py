"""pywebview Booth host — bridges UI to capture/playback and outer lock."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any

import webview

from voicelock.capture import CaptureEngine, CaptureStatus, DTYPE, SAMPLE_RATE
from voicelock.playback import PlaybackEngine
from voicelock.vault import (
    AuthError,
    NoVaultError,
    ValidationError,
    default_vault_path,
    enroll as vault_enroll,
    unlock as vault_unlock,
)

UI_PATH = Path(__file__).resolve().parent / "ui" / "index.html"


class BoothApi:
    """JS ↔ Python bridge for record / stop / play and vault enroll / unlock."""

    def __init__(
        self,
        capture: CaptureEngine | None = None,
        playback: PlaybackEngine | None = None,
        vault_path: Path | None = None,
    ) -> None:
        self.capture = capture or CaptureEngine()
        self.playback = playback or PlaybackEngine()
        self.vault_path = vault_path if vault_path is not None else default_vault_path()
        self._window: Any = None
        self._pumping = False
        self._pump_thread: threading.Thread | None = None
        self._play_watch: threading.Thread | None = None

    def bind_window(self, window: Any) -> None:
        self._window = window

    def ready(self) -> dict[str, Any]:
        """Probe the mic once the Booth has loaded."""
        error = self._probe_mic()
        if error is not None:
            self._push_mic_error(error)
            return {"ok": False, "error": error}
        return {"ok": True}

    def enroll(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Seal (or overwrite) the Vault with name + passphrase."""
        data = payload or {}
        name = str(data.get("name", "") or "")
        passphrase = str(data.get("passphrase", "") or "")
        overwrite = bool(data.get("overwrite", False))

        if self.vault_path.is_file() and not overwrite:
            return {"ok": False, "needs_confirm": True}

        try:
            vault_enroll(name, passphrase, path=self.vault_path)
        except ValidationError as exc:
            return {
                "ok": False,
                "error": "validation",
                "message": str(exc) or "Name and passphrase are required",
            }
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc) or "Enroll failed"}
        return {"ok": True, "name": name.strip(), "path": str(self.vault_path)}

    def unlock(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Open the outer lock; return the enrolled display name."""
        data = payload or {}
        passphrase = str(data.get("passphrase", "") or "")
        try:
            name = vault_unlock(passphrase, path=self.vault_path)
        except NoVaultError:
            return {"ok": False, "error": "no_vault"}
        except AuthError:
            return {"ok": False, "error": "auth"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": str(exc) or "Unlock failed"}
        return {"ok": True, "name": name}

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
    webview.start()


if __name__ == "__main__":
    main()

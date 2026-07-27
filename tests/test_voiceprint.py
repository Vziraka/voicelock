"""Voiceprint engine tests — spec F3 §5 cases (1)-(5).

Uses fixed audio fixtures under ``fixtures/voiceprint`` and the vendored ECAPA
model loaded fully offline (``HF_HUB_OFFLINE``, no network). Cutoff assertions
import the same module constants the app uses, so they are deterministic.
"""

from __future__ import annotations

import socket
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf

import voicelock.voiceprint as vp
from voicelock.voiceprint import (
    ACCEPT_CUTOFF,
    BAND_ACCEPT,
    BAND_REJECT,
    EMBEDDING_DIM,
    REJECT_CUTOFF,
    SAMPLE_RATE,
    NeedMoreAudioError,
    NoReferenceError,
    band_for,
    compare,
    default_reference_path,
    embed,
    load_wav,
    set_reference,
)

FIXTURES = Path(__file__).parent / "fixtures" / "voiceprint"


@pytest.fixture(scope="module")
def speaker_a_takes() -> list[np.ndarray]:
    return [load_wav(FIXTURES / f"speakerA_take{i}.wav") for i in (1, 2, 3)]


def test_default_reference_path() -> None:
    assert default_reference_path() == Path.home() / ".voicelock" / "voiceprint.ref"


# --- case (1): the compare pipeline runs end to end and bands its result ------
def test_compare_pipeline_runs_end_to_end(
    tmp_path: Path, speaker_a_takes: list[np.ndarray]
) -> None:
    """Set a reference, compare against it, and get an accept-banded distance.

    This proves the *pipeline* — embed, average, persist, load, distance, band —
    not the speaker model. `speakerA_live.wav` is a **sub-window of the same
    recording** the three reference takes are cut from (see
    `fixtures/voiceprint/README.md`), so a measure with no speaker modelling at
    all would land in the accept band too. The teeth are in
    `test_different_speaker_rejects`, whose impostor comes from a different
    recording of a different speaker.
    """
    ref = tmp_path / "voiceprint.ref"
    set_reference(speaker_a_takes, path=ref)
    distance, band = compare(load_wav(FIXTURES / "speakerA_live.wav"), path=ref)
    assert distance <= ACCEPT_CUTOFF
    assert band == BAND_ACCEPT


# --- case (2): different-speaker fixtures land in the reject band -------------
def test_different_speaker_rejects(
    tmp_path: Path, speaker_a_takes: list[np.ndarray]
) -> None:
    ref = tmp_path / "voiceprint.ref"
    set_reference(speaker_a_takes, path=ref)
    distance, band = compare(load_wav(FIXTURES / "speakerB.wav"), path=ref)
    assert distance >= REJECT_CUTOFF
    assert band == BAND_REJECT


# --- case (3a): Set reference averages 3 embeddings into one unit vector ------
def test_set_reference_averages_three(
    tmp_path: Path, speaker_a_takes: list[np.ndarray]
) -> None:
    ref = tmp_path / "voiceprint.ref"
    reference = set_reference(speaker_a_takes, path=ref)
    assert reference.shape == (EMBEDDING_DIM,)
    assert np.isclose(np.linalg.norm(reference), 1.0)
    assert ref.exists()
    # It is exactly the re-normalized mean of the per-take embeddings.
    manual = np.mean([embed(t) for t in speaker_a_takes], axis=0)
    manual = manual / np.linalg.norm(manual)
    assert np.allclose(reference, manual, atol=1e-9)


# --- case (3b): a too-short/silent take is rejected and not averaged in -------
def test_too_short_take_rejected_not_averaged(
    tmp_path: Path, speaker_a_takes: list[np.ndarray]
) -> None:
    ref = tmp_path / "voiceprint.ref"
    takes = [speaker_a_takes[0], load_wav(FIXTURES / "too_short.wav"), speaker_a_takes[2]]
    with pytest.raises(NeedMoreAudioError):
        set_reference(takes, path=ref)
    assert not ref.exists()  # nothing persisted -> the bad take was not averaged in


def test_silent_take_rejected() -> None:
    with pytest.raises(NeedMoreAudioError):
        embed(np.zeros(SAMPLE_RATE, dtype=np.float32))  # 1 s of silence


# --- case (4): compare with no reference surfaces a set-reference-first signal -
def test_compare_without_reference(tmp_path: Path) -> None:
    with pytest.raises(NoReferenceError):
        compare(np.zeros(SAMPLE_RATE, dtype=np.float32), path=tmp_path / "missing.ref")


# --- case (5): the model loads from the vendored local path with no network ---
def test_model_loads_offline_from_vendored_path(
    monkeypatch: pytest.MonkeyPatch, speaker_a_takes: list[np.ndarray]
) -> None:
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setattr(vp, "_classifier", None)  # force a fresh load under the block

    def _blocked(*args: object, **kwargs: object) -> None:
        raise AssertionError("network access attempted during offline model load")

    monkeypatch.setattr(socket, "getaddrinfo", _blocked)  # any real fetch resolves DNS first

    assert vp._MODEL_DIR.is_dir()
    assert (vp._MODEL_DIR / "embedding_model.ckpt").exists()
    vector = embed(speaker_a_takes[0])  # triggers the offline load, no network
    assert vector.shape == (EMBEDDING_DIM,)
    assert np.isclose(np.linalg.norm(vector), 1.0)


# --- F5.5: load_wav refuses bad audio instead of quietly converting it --------
# Both drive a real file written and read back through soundfile, so the raises
# are exercised end to end rather than through a monkeypatched decoder.
def test_load_wav_refuses_multichannel(tmp_path: Path) -> None:
    """Stereo audio raises and names the channel count — it is not downmixed."""
    path = tmp_path / "stereo.wav"
    sf.write(path, np.zeros((SAMPLE_RATE, 2), dtype=np.float32), SAMPLE_RATE)
    with pytest.raises(ValueError) as excinfo:
        load_wav(path)
    assert "2 channels" in str(excinfo.value)  # the real count, not a generic message


def test_load_wav_refuses_wrong_sample_rate(tmp_path: Path) -> None:
    """44.1 kHz audio raises and names the real rate — it is not resampled."""
    path = tmp_path / "rate44100.wav"
    sf.write(path, np.zeros(44_100, dtype=np.float32), 44_100)
    with pytest.raises(ValueError) as excinfo:
        load_wav(path)
    assert "44100 Hz" in str(excinfo.value)  # the real rate, not a generic message


def test_band_for_boundaries() -> None:
    assert band_for(ACCEPT_CUTOFF) == BAND_ACCEPT
    assert band_for(REJECT_CUTOFF) == BAND_REJECT
    assert band_for((ACCEPT_CUTOFF + REJECT_CUTOFF) / 2) == "borderline"

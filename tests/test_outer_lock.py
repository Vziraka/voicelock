"""Outer-lock passphrase seal / open / REJECT tests (temp path only).

The outer lock is unchanged by F4/F7, but ``enroll``/``unlock`` now carry
voiceprints and faceprints, so these cases pass synthetic embeddings and hold
both constant — what is under test here is the passphrase layer only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from voicelock.facelock import EMBEDDING_DIM as FACE_EMBEDDING_DIM
from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.vault import AuthError, enroll, unlock
from voicelock.voiceprint import EMBEDDING_DIM as VOICE_EMBEDDING_DIM


def a_voiceprint() -> np.ndarray:
    vector = np.random.default_rng(0).standard_normal(VOICE_EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def a_faceprint() -> np.ndarray:
    vector = np.random.default_rng(100).standard_normal(FACE_EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def enrollment() -> list[np.ndarray]:
    return [a_voiceprint()] * ENROLLMENT_TAKES


def face_enrollment() -> list[np.ndarray]:
    return [a_faceprint()]


def test_unlock_right_passphrase_returns_name(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada Lovelace", "correct-horse-battery", enrollment(), face_enrollment(), path=vault)
    assert (
        unlock("correct-horse-battery", a_voiceprint(), a_faceprint(), path=vault)
        == "Ada Lovelace"
    )


def test_unlock_wrong_passphrase_rejects(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse-battery", enrollment(), face_enrollment(), path=vault)
    with pytest.raises(AuthError):
        unlock("wrong-passphrase", a_voiceprint(), a_faceprint(), path=vault)

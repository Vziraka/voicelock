"""Outer-lock passphrase seal / open / REJECT tests (temp path only).

The outer lock is unchanged by F4, but ``enroll``/``unlock`` now carry
voiceprints, so these cases pass a synthetic embedding and hold the voice
constant — what is under test here is the passphrase layer only.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from voicelock.middlelock import ENROLLMENT_TAKES
from voicelock.vault import AuthError, enroll, unlock
from voicelock.voiceprint import EMBEDDING_DIM


def a_voiceprint() -> np.ndarray:
    vector = np.random.default_rng(0).standard_normal(EMBEDDING_DIM)
    return vector / np.linalg.norm(vector)


def enrollment() -> list[np.ndarray]:
    return [a_voiceprint()] * ENROLLMENT_TAKES


def test_unlock_right_passphrase_returns_name(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada Lovelace", "correct-horse-battery", enrollment(), path=vault)
    assert unlock("correct-horse-battery", a_voiceprint(), path=vault) == "Ada Lovelace"


def test_unlock_wrong_passphrase_rejects(tmp_path: Path) -> None:
    vault = tmp_path / "vault.vl"
    enroll("Ada", "correct-horse-battery", enrollment(), path=vault)
    with pytest.raises(AuthError):
        unlock("wrong-passphrase", a_voiceprint(), path=vault)

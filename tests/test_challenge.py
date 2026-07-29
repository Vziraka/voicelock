"""Challenge-phrase tests — spec F8 §5 cmd 1.

Three independent pieces, matching the module's own shape:

1. the phrase pool + no-immediate-repeat draw (no model load);
2. ``matches()`` — pure text comparison (no model load);
3. a REAL (unmocked) Vosk grammar-constrained run against an existing voice
   fixture, asserting REJECT — this repo's voice fixtures do not say any
   challenge phrase, so only the reject path is provable here (Q5's
   disclosed limitation; see ``test_real_vosk_rejects_a_fixture_not_saying_the_challenge``).
"""

from __future__ import annotations

from pathlib import Path
from random import Random

import pytest

from voicelock.challenge import (
    CHALLENGE_PHRASES,
    check,
    matches,
    pick_challenge,
)
from voicelock.voiceprint import load_wav

FIXTURES = Path(__file__).parent / "fixtures" / "voiceprint"


# --- case: the phrase pool -----------------------------------------------------
def test_phrase_pool_is_a_fixed_non_empty_constant() -> None:
    assert isinstance(CHALLENGE_PHRASES, tuple)
    assert 10 <= len(CHALLENGE_PHRASES) <= 20
    assert len(set(CHALLENGE_PHRASES)) == len(CHALLENGE_PHRASES)  # no duplicates
    assert all(isinstance(phrase, str) and phrase.strip() for phrase in CHALLENGE_PHRASES)


def test_pick_challenge_returns_a_pool_member() -> None:
    rng = Random(0)
    for _ in range(50):
        assert pick_challenge(rng=rng) in CHALLENGE_PHRASES


def test_pick_challenge_never_repeats_the_immediately_previous_phrase() -> None:
    """Exercised over enough draws that a false failure is statistically negligible.

    With a 12-entry pool, an unconstrained draw would repeat ~1/12 of the time;
    200 consecutive draws never repeating is not luck, it is the no-repeat filter.
    """
    rng = Random(42)
    previous = pick_challenge(rng=rng)
    for _ in range(200):
        current = pick_challenge(previous=previous, rng=rng)
        assert current != previous
        previous = current


def test_pick_challenge_covers_the_whole_pool_over_many_draws() -> None:
    rng = Random(7)
    seen = set()
    previous = None
    for _ in range(500):
        previous = pick_challenge(previous=previous, rng=rng)
        seen.add(previous)
    assert seen == set(CHALLENGE_PHRASES)


# --- case: matches() — substring containment (2026-07-29 live-demo fix) -------
@pytest.mark.parametrize(
    ("recognized", "challenge", "expected"),
    [
        ("open the blue door now", "open the blue door now", True),
        ("Open, the Blue Door Now!", "open the blue door now", True),
        ("silver clouds drift over mountains", "open the blue door now", False),
        ("the [unk]", "open the blue door now", False),
        ("", "open the blue door now", False),
        # Real Vosk decode noise observed in the live demo (2026-07-29):
        # a stray leading word, and the phrase appearing twice in one take.
        ("my open the blue door now", "open the blue door now", True),
        ("open the blue door now open the blue door now", "open the blue door now", True),
        # The target phrase must still appear whole -- a partial overlap
        # (missing a word) does not count as saying it.
        ("open the blue door", "open the blue door now", False),
    ],
)
def test_matches_synthetic_table(recognized: str, challenge: str, expected: bool) -> None:
    assert matches(recognized, challenge) is expected


# --- case: real Vosk, reject path only (Q5's disclosed limitation) -------------
def test_real_vosk_rejects_a_fixture_not_saying_the_challenge() -> None:
    """Real (unmocked) Vosk decoding against a real voice fixture.

    ``speakerA_take1.wav`` is a VoxCeleb clip that does not say any
    hand-authored challenge phrase (Q3) — this repo has no honest fixture of
    someone saying a challenge phrase, so this test can only prove the
    REJECT path for real. It does NOT and CANNOT prove ``check()`` correctly
    ACCEPTs a real "yes, this is the challenge" utterance; that is proven
    only by the required live manual check (spec §5 cmd 4).
    """
    audio = load_wav(FIXTURES / "speakerA_take1.wav")
    assert check(audio, CHALLENGE_PHRASES[0]) is False

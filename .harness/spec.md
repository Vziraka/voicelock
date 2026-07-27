# Spec: F5.5 — Voiceprint dead-surface hygiene

Feature: Feature 5.5 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [ ] Approved by human

- **Mode:** Mode 4 (Continuous roadmap). Set by the human 2026-07-26. The
unlock was checked mechanically, not assumed: all 29 files in
`memory/verdicts/` record `"dev_mode": "Mode 3"`, and the completion reports
for F3, F4 and F5 are in git history (`627963e`, `22e6a4a`, `319b48b`) — both
conditions the universal Modes section requires. Mode 4 means this feature runs
to DONE unattended and **F6's spec is then drafted with its questions embedded
and parked at the approval gate** — never approved, never built.
Mode 4's autonomy is bounded here by an unusually settled design: the scope was
cut on measurement during grilling, no dependency changes, no live surface, and
§5 pins that no measured constant may move.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

> **This spec explicitly UNFREEZES `src/voicelock/voiceprint.py`.** F4's spec §4
> froze it as "the identity source, unchanged", and F5 inherited that. That
> freeze was correct while F4's measured constants were being pinned against it.
> It is lifted **for the named deletions in §4 only** — no behaviour on any live
> path changes, and §5 pins that the measured constants do not move.

## 1. Outcome

Remove surface from the voiceprint engine that no caller and no test can reach,
and stop one test from claiming to prove something it cannot. Sourced from
calibration run 2 (`.out-of-scope/2026-07-26-calibration-findings-run2.md`),
the same channel that produced F4.5.

This is a hygiene feature, deliberately inserted before F6 for the same reason
F4.5 was inserted before F5: **F6 reopens this exact module.** F6 adds a second
vendored model (OpenCV SFace) and a faceprint that mirrors the voiceprint's
shape, so it will read `voiceprint.py` as the pattern to copy. Copying dead
branches is how the F4.5 fake-stream pattern nearly propagated into F5.

Three things must be true when this is done:

1. **No unreachable surface in `voiceprint.py`.** `_resample`, both of its call
   sites, the stereo-downmix branch, and the `sample_rate` parameters on
   `embed` and `compare` are gone. This was the one blocking finding **both**
   independent F3-T2 verifiers agreed on, and it is a direct hit on the earned
   "no unexercised branch" guardrail.
2. **Bad audio is refused loudly, not misread quietly.** `load_wav` raises a
   clear `ValueError` naming the problem when handed multichannel or
   non-16 kHz audio, instead of silently converting it. A test drives both
   raises, so this replacement is genuinely exercised rather than being new
   dead surface of its own.
3. **The same-speaker test stops overclaiming.** It is renamed and documented
   to say what it actually proves — that the compare pipeline runs end to end —
   with a pointer to the impostor test, which carries the real teeth.

Demo: `uv run pytest` stays green with the same measured constants, and
`voiceprint.py` no longer contains a line that cannot execute.

## 2. Grilling record — ambiguity scan

**Status: CLEAR** — every category resolved; the `Mode:` line is set and the
Mode 2+ blind-spot question is answered, so zero clarification markers remain
(2026-07-26).

| Category | Verdict | Resolved by |
| --- | --- | --- |
| Functional scope & behavior | Clear | Three items in §1, bounded by §3. Scope was cut down mid-grilling on evidence — see "What changed during grilling" below. |
| Domain & data model | Clear | No format, vault, or crypto surface touched. No persisted artifact changes. The `.ref` reference-vector file format is untouched. |
| Interaction & UX flow | Clear | No UI change of any kind. `app.py` calls `embed`/`compare` positionally and passes no `sample_rate` (verified by grep, 2026-07-26), so no bridge or Booth surface moves. |
| Non-functional (perf, security) | Clear | Strictly a deletion plus two raises; no performance or security surface. Offline-only untouched. |
| Integration & dependencies | Clear | **No new dependencies.** Nothing added to `pyproject.toml`; no TECH-PICK trigger. |
| Edge cases & failure modes | Clear | The two cases the deleted code pretended to handle become explicit raises with tests (§1.2). The frozen-module conflict is resolved by the §0 unfreeze note. |
| Completion signals | Clear | §5 pins six runnable commands, including a permanent mutation-resistance proof and an assertion that the measured constants did not move. |
| Terminology (matches `CONTEXT.md`) | Clear | Uses **Voiceprint** as the glossary defines it. No new terms. |

**What changed during grilling (recorded because the scope shrank on evidence):**
the feature was drafted with a fourth item — replacing the vacuous same-speaker
assertion with an *ordering* assertion on the byte-disjoint `enroll1`/`enroll5`
pair. It was **dropped after measurement disproved it**. A dummy embedder with
no speaker modelling at all (a 192-bin log-magnitude spectrum) orders that pair
correctly too — 0.077 < 0.113 — so the proposed test would have passed just as
vacuously as the one it replaced. The root confound is not the byte overlap: both
speaker-A clips come from **one recording session**, so any content-derived
measure puts them nearer each other than a differently-recorded speaker. With one
clip per speaker in the Apache-2.0 source and offline-only forbidding a fetch, no
fixture-based same-speaker assertion can be made mutation-resistant. That is
already the standing position of `tests/fixtures/voiceprint/README.md:89-93`, and
it stands. Item 3 is what survives: stop the test overclaiming.

## 3. Non-goals

- **Re-pinning `ACCEPT_CUTOFF`, `REJECT_CUTOFF`, or F4's `CORRECTION_RADIUS`.**
  Explicitly forbidden here. §5 asserts they do not move. Re-measuring them is a
  measurement task needing its own spec and honest fixtures.
- **New or replacement fixtures.** No new audio enters the repo. The two-clips
  problem is real and stays F9's / a future fixture feature's.
- **Touching `middlelock.py`, `vault.py`, or the F4 construction.**
- **`load_reference`'s re-normalize** (`voiceprint.py:112`). A verifier flagged
  it as survivable under mutation, but it is an unconditional defensive
  statement on data read from disk, not an unreachable branch — a different
  category from the guardrail's target. Deliberately left alone on a frozen
  identity module.
- **Any UI, camera, or face surface.** F6 owns those.

## 4. Constraints

- **No new dependencies.** Nothing enters `pyproject.toml`.
- **`voiceprint.py` is unfrozen for these deletions only** (see §0). Every other
  line of it stays as F4 left it.
- **No live-path behaviour may change.** Verified precondition: `app.py:66`,
  `app.py:221` and `app.py:245` are the only production callers, and none passes
  `sample_rate`; `capture.py` pins the only real audio source to 16 kHz mono.
  So removing the parameters is caller-safe.
- **The deletions, precisely:** `_resample` (`voiceprint.py:206-211`); its call
  sites at `:71-72` and `:156-157`; the `data.ndim > 1` downmix at `:154-155`;
  the `sample_rate` parameter on `embed` (`:65`) and on `compare` (`:116`); and
  `compare`'s internal pass-through at `:124`.
- **The replacements, precisely:** `load_wav` raises `ValueError` naming the
  actual sample rate when it is not `SAMPLE_RATE`, and raises `ValueError`
  naming the channel count when the data is not mono.
- **Test renaming:** `test_same_speaker_accepts` is renamed to say what it
  proves, and carries a docstring stating that the probe is a sub-window of the
  reference audio and that the impostor test is the one with teeth.

## 5. Verification — definition of done (runnable)

**Standing** (the regression net — `project.md`'s Gate commands):

- `uv run ruff check .` → exit 0.
- `uv run pytest` → exit 0. Reference: 122 passing before this feature; the
  count rises by the new `load_wav` tests and must not fall.

**Feature-specific:**

1. **The dead surface is gone.**
   `uv run python -c "import inspect; from voicelock import voiceprint as v; s = inspect.getsource(v); assert '_resample' not in s, '_resample survives'; assert 'sample_rate' not in str(inspect.signature(v.embed)), 'embed still takes sample_rate'; assert 'sample_rate' not in str(inspect.signature(v.compare)), 'compare still takes sample_rate'; assert '.ndim > 1' not in s, 'the downmix branch survives'"`
   → exit 0.

2. **Bad audio raises instead of being converted** — the behaviour, driven
   directly rather than through a name filter:
   ```
   uv run python -c "
   import numpy as np, soundfile as sf, tempfile, pathlib
   from voicelock.voiceprint import load_wav
   d = pathlib.Path(tempfile.mkdtemp())
   sf.write(d / 'stereo.wav', np.zeros((16000, 2), dtype='float32'), 16000)
   sf.write(d / 'rate.wav', np.zeros(44100, dtype='float32'), 44100)
   for name in ('stereo.wav', 'rate.wav'):
       try:
           load_wav(d / name)
       except ValueError:
           continue
       raise SystemExit('load_wav accepted ' + name)
   "
   ```
   → exit 0.

   And the tests for it must actually exist — a `-k` filter that matches
   nothing still exits 0, so the count is asserted rather than assumed:
   `uv run python -c "import pathlib; t = pathlib.Path('tests/test_voiceprint.py').read_text(encoding='utf-8'); assert 'multichannel' in t, 'no multichannel load_wav test'; assert t.count('pytest.raises(ValueError)') >= 2, 'fewer than 2 ValueError tests for load_wav'"`
   → exit 0.

3. **The measured constants did not move.**
   `uv run python -c "from voicelock.voiceprint import ACCEPT_CUTOFF, REJECT_CUTOFF; assert ACCEPT_CUTOFF == 0.45, ACCEPT_CUTOFF; assert REJECT_CUTOFF == 0.65, REJECT_CUTOFF"`
   → exit 0. This is the anti-temptation pin: nothing in this feature may be
   "fixed" by moving a threshold.

4. **The impostor test genuinely depends on the speaker model** — a permanent,
   runnable mutation proof, and the enforcement half of the guardrail adopted
   2026-07-26 ("a test must assert something that would break if the behaviour
   were removed"):
   `uv run python -c "import numpy as np, pathlib; from voicelock import voiceprint as vp; f = lambda a: (lambda v: (v / np.linalg.norm(v)).astype(np.float32))(np.log1p(np.array([b.mean() for b in np.array_split(np.abs(np.fft.rfft(a.astype(np.float64))), 192)]))); d = pathlib.Path('tests/fixtures/voiceprint'); ref = vp._normalize(np.mean([f(vp.load_wav(d / ('speakerA_take%d.wav' % i))) for i in (1, 2, 3)], axis=0)); dist = vp.cosine_distance(ref, f(vp.load_wav(d / 'speakerB.wav'))); assert dist < vp.REJECT_CUTOFF, 'a dummy embedder with no speaker modelling still rejects the impostor - the impostor test has no teeth'"`
   → exit 0. Measured 2026-07-26: real ECAPA scores the impostor **0.832**
   (reject); the dummy scores **0.113** (accept), so the assertion holds and the
   test is proven mutation-sensitive.

5. **The overclaiming test name is gone.**
   `uv run python -c "import pathlib; t = pathlib.Path('tests/test_voiceprint.py').read_text(encoding='utf-8'); assert 'def test_same_speaker_accepts' not in t, 'the overclaiming test name survives'; assert 'sub-window' in t or 'same recording' in t, 'the fixture limitation is not documented at the test'"`
   → exit 0.

**No manual check is required.** Unlike F1–F5 this feature has no live surface:
it deletes unreachable code and renames a test. Nothing a human could observe in
the Booth changes, so a live demo would be theatre rather than evidence. This is
a deliberate departure from the per-feature manual-check precedent, and the
reason is recorded here rather than left implicit.

**Out-of-scope default (Modes 3–4):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

**"If every gate passed but the feature were still wrong, what would be wrong?"**
**RESOLVED 2026-07-26 (human's answer): F6 would copy the strict-rejection
pattern into a place it does not belong.**

Every §5 command could pass and this feature could still do net harm, because
its stated purpose is that **F6 inherits `voiceprint.py` as the pattern to
copy** (§1). The pattern it will inherit is "refuse unexpected input loudly" —
and that is correct **only** because `capture.py` pins the microphone to exactly
one sample rate and one channel, so any deviation genuinely is a bug. F6's image
path has **no equivalent pin**: camera frames legitimately vary in resolution,
and a faceprint module that raises on an unexpected frame size would reject
valid input. The gates cannot catch this, because the damage lands in a feature
that does not exist yet.

**Chosen mitigation (a required check, not accepted risk):** the justification
travels with the code.

- The `ValueError` raises in `load_wav` each carry a comment stating that the
  pin in `capture.py` is what makes refusal correct here, and that a source
  without such a pin must convert rather than refuse.
- §5 command 6 (below) asserts that comment exists, so it cannot be dropped in
  a later tidy-up.

7. **The rejection's justification is recorded at the code.**
   `uv run python -c "import inspect; from voicelock import voiceprint as v; s = inspect.getsource(v.load_wav); assert 'capture.py' in s, 'the raises do not explain that the pinned capture rate is what justifies refusing'"`
   → exit 0.

*(Numbered 7 to follow §5's list; it is a §5 Verification command and the Gate
runs it with the others.)*

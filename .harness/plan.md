# Plan — F5.5 — Voiceprint dead-surface hygiene

## Active context
- Updated: 2026-07-26
- Feature: Feature 5.5 from `roadmap.md` · Mode: Mode 4 · Phase: **building —
  Task 1 `DONE` (`rejects: 1`), Task 2 `REVIEW`. Then Task 3 (LAST, full spec
  Verification), then the Mode 4 tail.**
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)
- Spec: `spec.md` holds F5.5's spec, `Status: CLEAR`, zero clarification
  markers, **both boxes checked** (box 2 by the human, 2026-07-26). F5's ledger
  is closed and lives in git (`b246cb2`); this file replaces it.
- **Mode 4 tail:** after Task 3 reaches `DONE` and wrap-up writes the completion
  report, this feature's session drafts **F6's spec with its questions embedded
  and parks it at the approval gate** — never approved, never built. That draft
  is not a task in this ledger; it is Mode 4's defined tail.

### Why this feature exists, in one line
F6 reopens `voiceprint.py` and will read it as the pattern to copy. F4.5 exists
because a bad pattern nearly propagated into F5; this is the same argument one
feature later. Source: calibration run 2
(`.out-of-scope/2026-07-26-calibration-findings-run2.md`).

### The dependency that fixes the task order
`_resample` has **two** call sites — `embed` (`voiceprint.py:72`) and `load_wav`
(`:157`). It cannot be deleted until **both** are gone. Task 1 removes
`load_wav`'s, Task 2 removes `embed`'s and then deletes the function. That
ordering is forced, not stylistic, and it is why the deletion is not one task.

### The named blind spot, carried from `spec.md` §6
"Refuse unexpected input" is correct here **only** because `capture.py` pins the
mic to one rate and one channel. **F6 must not copy it** — camera frames
legitimately vary in resolution. Task 1 writes that justification beside the
raises and a done-criterion asserts it stays there.

### Memory spine (≤5)
1. **Where we are: Task 1 `DONE`; Tasks 2 and 3 are pure subtraction and
   renaming.** `load_wav` now refuses bad audio, but **`_resample` still exists
   and `embed` still calls it** — Task 2 removes that last caller and then the
   function. Suite stands at **124 passed**, up from 122.
2. **This feature's criteria match SOURCE TEXT literally — spell the code to
   satisfy them, never edit the criterion.** Task 1 lost a full verify cycle to
   exactly this: `spec.md` §5 cmd 2 counts the substring
   `pytest.raises(ValueError)`, and `pytest.raises(ValueError, match=...)`
   counts 0. Still ahead: Task 2's `'.ndim > 1' not in s` and `sample_rate`
   absent from both signatures; Task 3's `def test_same_speaker_accepts` absent
   and `sub-window`/`same recording` present. A criterion is `spec.md`'s and
   human-approved — changing one is a spec amendment.
3. **Nothing may be fixed by moving a threshold.** `ACCEPT_CUTOFF = 0.45` and
   `REJECT_CUTOFF = 0.65` are pinned by a done-criterion on Tasks 2 and 3, and
   §5 cmds 3 and 4 **pass today and must keep passing**.
4. **Scope shrank during grilling, on measurement.** A fourth item — an ordering
   assertion on the byte-disjoint `enroll1`/`enroll5` pair — was drafted then
   **disproved**: a dummy embedder with no speaker modelling orders that pair
   correctly too (0.077 < 0.113). Root cause is one recording session per
   speaker, not byte overlap. **Do not re-propose it.**
5. **`voiceprint.py` is unfrozen for the named deletions only** (`spec.md` §0);
   `load_reference`'s re-normalize (`:112`) is a deliberate **§3 non-goal**. No
   new dependencies, no UI, no live surface, and **no manual check** — the first
   feature with none, and `spec.md` §5 records why.

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — `load_wav`: refuse bad audio instead of silently converting it
  - state: DONE
  - rejects: 1
  - verdict: `memory/verdicts/2026-07-26-F5.5-T1.json` — GATE PASS (5/5, `pytest`
    124 passed / 0 failed), REVIEW APPROVE (spec pass · standards pass),
    mechanism `subagent`, 2026-07-26
  - files: `src/voicelock/voiceprint.py`, `tests/test_voiceprint.py`
  - notes: Edit `load_wav` (`:148-158`) only. Remove the downmix branch
    (`:154-155`) and the resample call (`:156-157`); in their place raise
    `ValueError` naming the **actual** offending value — the real channel count,
    the real sample rate — not a generic message, because the whole point is
    that a malformed fixture fails loudly and legibly.
    **Leave `_resample` in place.** `embed` still calls it; deleting it here
    would break Task 2's starting state. This task removes one of its two
    callers, nothing more.
    **Write the justification beside the raises** (`spec.md` §6): a comment
    stating that `capture.py`'s pinned 16 kHz mono source is what makes refusing
    correct, and that a source without such a pin must convert rather than
    refuse. This is the F6 blind-spot mitigation and it is a done-criterion, not
    a nicety.
    Tests: at least two, using `pytest.raises(ValueError)`, driving a real
    stereo file and a real 44.1 kHz file written to `tmp_path` with `soundfile`
    — a genuine round-trip, not a monkeypatched `sf.read`. The replacement must
    be exercised, or it is new dead surface of exactly the kind this feature
    removes.
    **Why first:** it is the only task that adds behaviour; Tasks 2 and 3 are
    pure subtraction and renaming, and both are cleaner against a `load_wav`
    that already refuses bad input.
    **Retry 1 note (from the Gate FAIL below):** done-criterion 2 counts the
    **literal substring** `pytest.raises(ValueError)`, so
    `pytest.raises(ValueError, match=...)` does not count — the comma breaks the
    match. Write the raises as `with pytest.raises(ValueError) as exc:` and keep
    the message assertion on `str(exc.value)`; that satisfies the command as
    written **and** keeps the test stronger than the command demands. Do NOT
    edit the criterion to fit the code — it is repeated verbatim in `spec.md`
    §5 cmd 2 and in Task 3's full list, and changing it is a spec amendment
    needing human approval.
  - done-criteria:
    - §5 cmd 2, behaviour half — verbatim, exit 0:
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
    - `uv run python -c "import pathlib; t = pathlib.Path('tests/test_voiceprint.py').read_text(encoding='utf-8'); assert 'multichannel' in t, 'no multichannel load_wav test'; assert t.count('pytest.raises(ValueError)') >= 2, 'fewer than 2 ValueError tests for load_wav'"` → exit 0 (§5 cmd 2, second half — a `-k` filter matching nothing also exits 0, so the tests' existence is asserted rather than assumed)
    - `uv run python -c "import inspect; from voicelock import voiceprint as v; s = inspect.getsource(v.load_wav); assert 'capture.py' in s, 'the raises do not explain that the pinned capture rate is what justifies refusing'"` → exit 0 (§6's command — the F6 blind-spot mitigation)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; the count rises by the new tests and must not fall below 122)
  - feedback:
    - **GATE FAIL #1 (2026-07-26, subagent verifier, base `b063f30` → head
      `a6572c0`).** Done-criterion 2 (`plan.md:103` = `spec.md` §5 cmd 2 second
      half) exited 1: `AssertionError: fewer than 2 ValueError tests for
      load_wav`. The command counts the literal substring
      `pytest.raises(ValueError)`; the two new tests were written as
      `pytest.raises(ValueError, match="2 channels")`
      (`tests/test_voiceprint.py:130`) and
      `pytest.raises(ValueError, match="44100 Hz")` (`:138`), so the literal
      count measured **0**, not 2. Every other criterion passed: behaviour half
      exit 0, §6 justification command exit 0, `ruff` exit 0, `pytest` exit 0
      with **124 passed** (up from 122, 0 failed). Scope check PASS —
      `_resample` correctly left in place, no protected-file writes.
      Command-vs-code mismatch, not a behaviour defect; the fix is in the test
      spelling, not in the criterion.

- [ ] **Task 2** — Remove the `sample_rate` parameters and delete `_resample`
  - state: REVIEW
  - rejects: 0
  - files: `src/voicelock/voiceprint.py`
  - notes: Pure subtraction, no test changes expected. Remove: the
    `sample_rate` parameter on `embed` (`:65`) and its branch (`:71-72`); the
    `sample_rate` parameter on `compare` (`:116`) and its pass-through at
    `:124` (`embed(live_audio, sample_rate)` → `embed(live_audio)`); then
    `_resample` itself (`:206-211`), which is callerless once those two go.
    **Caller-safety is already verified, not assumed** (`spec.md` §4): the only
    production callers are `app.py:66` `embed(signal[...])`, `app.py:221`
    `embed(buf)` and `app.py:245` `compare(buf, path=self.ref_path)` — all
    one-positional-arg or keyword `path`, none passing `sample_rate`. Removing a
    middle positional parameter from `compare` is therefore safe. Every test
    call is likewise single-argument.
    **Do not touch `load_reference`'s re-normalize** (`:112`) — `spec.md` §3
    lists it as a non-goal on purpose.
    Expect the suite to stay at Task 1's count; if any test fails, a caller was
    missed and that is the finding, not a nuisance.
  - done-criteria:
    - `uv run python -c "import inspect; from voicelock import voiceprint as v; s = inspect.getsource(v); assert '_resample' not in s, '_resample survives'; assert 'sample_rate' not in str(inspect.signature(v.embed)), 'embed still takes sample_rate'; assert 'sample_rate' not in str(inspect.signature(v.compare)), 'compare still takes sample_rate'; assert '.ndim > 1' not in s, 'the downmix branch survives'"` → exit 0 (§5 cmd 1)
    - `uv run python -c "from voicelock.voiceprint import ACCEPT_CUTOFF, REJECT_CUTOFF; assert ACCEPT_CUTOFF == 0.45, ACCEPT_CUTOFF; assert REJECT_CUTOFF == 0.65, REJECT_CUTOFF"` → exit 0 (§5 cmd 3 — the anti-temptation pin)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, count unchanged from Task 1)
  - feedback: (none)

- [ ] **Task 3** — Stop the same-speaker test overclaiming *(LAST task — full spec Verification)*
  - state: TODO
  - rejects: 0
  - files: `tests/test_voiceprint.py`
  - notes: Rename `test_same_speaker_accepts` to say what it actually proves —
    that the compare pipeline runs end to end — and give it a docstring stating
    plainly that its probe (`speakerA_live.wav`) is a **sub-window of the same
    recording** as the reference takes, so it cannot prove the speaker model
    works, and pointing at the impostor test as the one that can.
    **No assertion changes, no fixture changes.** The measured behaviour stays
    exactly as it is; only the name and the documentation move. Anything more
    was tried and disproved — see memory spine item 1.
    **This is the LAST task**, so its done-criterion is the FULL `spec.md`
    Verification list (found by name, not section number). That list includes
    §5 cmd 4, the permanent mutation proof that the impostor test genuinely
    depends on the speaker model — the enforcement half of the guardrail adopted
    2026-07-26.
    **No manual check** — `spec.md` §5 states why: this feature has no live
    surface, so a Booth demo would be theatre, not evidence. The verifier should
    NOT `ESCALATE_HUMAN` for a missing manual check on this feature; that
    departure from F1–F5 is deliberate and recorded in the spec.
  - done-criteria: **the FULL list from `spec.md`'s Verification section**, namely —
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, ≥122 passing)
    - §5 cmd 1 — the dead surface is gone → exit 0
    - §5 cmd 2 — both halves: bad audio raises, and the tests for it exist → exit 0
    - §5 cmd 3 — `ACCEPT_CUTOFF == 0.45` and `REJECT_CUTOFF == 0.65` → exit 0
    - §5 cmd 4 — the dummy-embedder mutation proof: a no-speaker-model embedder must FAIL to reject the impostor → exit 0
    - §5 cmd 5 — `uv run python -c "import pathlib; t = pathlib.Path('tests/test_voiceprint.py').read_text(encoding='utf-8'); assert 'def test_same_speaker_accepts' not in t, 'the overclaiming test name survives'; assert 'sub-window' in t or 'same recording' in t, 'the fixture limitation is not documented at the test'"` → exit 0
    - §6's command — the rejection's justification is still recorded at the code → exit 0
  - feedback: (none)

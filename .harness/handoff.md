# Handoff — F5.5 Task 1 DONE, Task 2 next

**Mode 4.** Task 1 is closed with a verdict file. Tasks 2 and 3 remain, and the
approved spec's `Mode:` line is the standing "go" for both — no further human
approval is needed inside F5.5.

## Changed

**Task 1 — `load_wav` refuses bad audio instead of silently converting it.**
`src/voicelock/voiceprint.py` and `tests/test_voiceprint.py`. Details live in
the diff and in `plan.md` Task 1; the short version:

- The stereo downmix and the resample call inside `load_wav` are replaced by two
  `ValueError`s that name the offending value (`got 44100 Hz`, `got 2 channels`).
- The `spec.md` §6 justification travels with the code: refusal is correct only
  because `capture.py` pins the one real source to `CHANNELS = 1` at 16 kHz, and
  a source without such a pin — camera frames — must convert, not refuse.
- Two tests drive both raises through a real `soundfile` round-trip in
  `tmp_path`. Suite went 122 → **124 passed, 0 failed**.
- `_resample` deliberately survives — `embed` still calls it. Task 2 removes
  that caller and then the function. That ordering is the whole reason the
  deletion is two tasks.

## Failed + lesson

**Gate FAIL #1** (`rejects: 1` of the 3-cap). Done-criterion 2 — `spec.md` §5
cmd 2's second half — counts the **literal substring**
`pytest.raises(ValueError)`. The tests were spelled
`pytest.raises(ValueError, match="2 channels")`, so the comma broke the match
and the count measured 0, not 2. Every other criterion passed on that attempt,
`pytest` included. The fix was in the test spelling —
`with pytest.raises(ValueError) as excinfo:` plus an assertion on
`str(excinfo.value)`, which satisfies the command as written and keeps the
message assertion. The criterion itself was **not** touched: it is a
human-approved `spec.md` command, repeated verbatim in Task 3's full list, so
editing it to fit the code would be a spec amendment.

Full arc, both verdicts, and the verifier's mutation check are archived in
`memory/verdicts/2026-07-26-F5.5-T1.json`.

## Pending guardrail

**One proposal, awaiting the human's yes/no.** Not written to `project.md`;
`learn` may not write it unapproved.

> - **[Done]** A Verification command that asserts on **source text** must match
>   the behaviour's *meaning*, not one exact spelling — use a regex or an AST
>   check, not `str.count` on a literal. `warn` · expires: 2027-01-31
>   - _Evidence:_ F5.5 Task 1 (2026-07-26) cost a full verify cycle to a Gate
>     FAIL that found no defect. `spec.md` §5 cmd 2 asserts
>     `t.count('pytest.raises(ValueError)') >= 2` as a proxy for "the tests
>     exist"; the tests existed, passed, and were **stronger** than the criterion
>     demanded (they pinned the real channel count and the real sample rate), but
>     were spelled `pytest.raises(ValueError, match=...)` and counted 0.
>     `re.findall(r'pytest\.raises\(\s*ValueError\b', t)` would have counted 2.
>     Not a one-off: this repo now leans on source-text criteria routinely — the
>     per-module stream-fake tripwire asserts `read`/`release` appear in
>     `tests/test_facedetect.py`, and F5.5 alone carries five more
>     (`.ndim > 1`, `sample_rate`, `def test_same_speaker_accepts`,
>     `sub-window`, `capture.py`). Task 1 dodged the `.ndim > 1` one only by
>     deliberate spelling, which is exactly the fragility the rule names.
>     Enforcement beats memory here and is cheap — write the criteria as
>     regexes — but that changes `spec.md`'s Verification commands, so it goes
>     through the spec/approval path rather than being applied at wrap-up.
>   - _Overlap-checked_ against all six current guardrails: closest is "a test
>     must assert something that would break if the behaviour were removed", and
>     it is the converse — that rule catches a **test** that passes vacuously;
>     this one catches a **criterion** that fails a sound test. Low overlap; a
>     new entry rather than an edit.

## next_action

**`/implement` Task 2** — remove the `sample_rate` parameters from `embed` and
`compare`, then delete the now-callerless `_resample`. Pure subtraction, no test
changes expected. Mode 4 starts it without a further "go".

## Where the rest lives

- Task ledger, feedback log, memory spine → `plan.md`
- What is fixed and why → `spec.md` (§3 non-goals, §4 the precise deletions,
  §5 the seven runnable commands, §6 the F6 blind spot)
- Task 1's full verdict, gate output, and reviewer note →
  `memory/verdicts/2026-07-26-F5.5-T1.json`
- Why this feature exists at all →
  `.out-of-scope/2026-07-26-calibration-findings-run2.md`

## Still not to be re-litigated

1. **Do not re-propose the ordering assertion** on the `enroll1`/`enroll5` pair
   — disproved by measurement (a dummy embedder orders it correctly too:
   0.077 < 0.113). `plan.md` memory spine.
2. **Do not move a threshold to make anything pass.** `ACCEPT_CUTOFF = 0.45`
   and `REJECT_CUTOFF = 0.65` are pinned by done-criteria on Tasks 2 and 3.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:112`) —
   `spec.md` §3 keeps it deliberately.
4. **Do not expect a manual check.** `spec.md` §5 records why this feature has
   none. A verifier should **not** `ESCALATE_HUMAN` over its absence.

## Verifier path

**Subagent** (`project.md` Environment; used for Task 1 twice, both times
returning the template's structure and writing no state). At Mode 4 the
implement session spawns it with `formats/VERIFIER-PROMPT.md` **verbatim** and
is the executor of the returned verdict; wanting to override = `ESCALATE_HUMAN`.

## Mode 4 tail — after Task 3

Once Task 3 is `DONE` and wrap-up writes F5.5's completion report, the session
drafts **F6 — Faceprint on screen**'s spec with every grilling question embedded
as a clarification marker and its `Mode:` line left blank, then **parks it at
the approval gate and stops.** Never approved, never built.

## Commits

- Task 1 attempt 1: `b063f30` (DOING) → `a6572c0` (build) → `e21665c`
  (bookkeeping) → `b9007a3` (GATE FAIL #1 recorded)
- Task 1 retry 1: `a16841f` (DOING) → **`d110551` (build)** → `552da43`
  (bookkeeping) → this wrap-up commit
- Session base was `5d39918`. Remote `origin` exists (private); pushes stay
  human-gated at the feature-end checkpoint, so nothing is pushed yet.

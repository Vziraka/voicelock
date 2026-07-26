# Calibration run — 2026-07-26 (first ever)

Run by `curate` per `CALIBRATION.md`. Trigger conditions were both met: the folder
held ≥5 verdicts (19), and harness files had changed since the last curate (never
curated; `project.md` gained its first earned guardrail the same day).

**The archive itself is NOT edited.** This file records the finding beside it, as
`CALIBRATION.md` requires.

## Result: 0 of 3 agreement

| Archived verdict | Archived | Fresh re-run | Agree? |
|---|---|---|---|
| `2026-07-22-F1-T2` (capture engine) | GATE PASS · APPROVE | GATE PASS · **REJECT** (5 findings) | ✗ |
| `2026-07-22-F2-T3` (Booth enroll/unlock chrome) | GATE PASS · APPROVE | GATE PASS · **REJECT** (4 findings) | ✗ |
| `2026-07-22-F3-T2` (voiceprint engine) | GATE PASS · APPROVE | GATE PASS · **REJECT** (3 findings) | ✗ |

Every fresh Gate passed. All three disagreements are on the **Reviewer** axes.

## Which way does the disagreement point?

`CALIBRATION.md` frames the question as: did the harness change degrade the
verifier, or were the archived verdicts wrong? **The evidence points at the
archived verdicts**, not at the change.

The harness change under test was the new `[Forbidden]` guardrail about uncalled,
untested code. It accounts for roughly one finding per task. But **each task also
produced at least one substantive finding entirely independent of it**:

- **F1-T2** — `capture.py:117-118` calls `_close_stream()` (`stream.stop()` then
  `stream.close()`) from inside the PortAudio callback, on the line directly after
  a comment saying the callback cannot safely do that. `Pa_StopStream` blocks
  until the callback returns, so it waits on itself. Nothing catches it because
  `FakeStream` never invokes the callback — `_on_audio`, the path all real
  microphone audio takes, has zero test coverage. **Verified independently.**
- **F2-T3** — the overwrite-confirm button called `hideOverwriteConfirm()`, which
  zeroed the very `pendingOverwrite` flag it existed to set, so confirming an
  overwrite discarded the confirmation and re-showed the banner forever.
  **Verified independently against the archived blob.**
- **F3-T2** — `voiceprint.py:150` imports `soundfile`, which is not in
  `pyproject.toml` and reaches the environment only as a SpeechBrain transitive.
  **Verified independently.**

None of those three is a dead-code finding. The honest reading is that the F1–F3
reviews — the project's earliest — were **more lenient** than today's, and the
new guardrail is a contributing factor to the disagreement, not its cause.

## Confounds in THIS run — read before trusting the 0/3 number

Three flaws in the calibration setup, all mine, all likely to inflate disagreement:

1. **Priming.** The calibration brief told each agent that "`project.md`'s
   guardrails are what we are calibrating against." That plausibly primed them to
   hunt dead code specifically. A neutral brief would be a fairer test.
2. **Wrong plan supplied for F2-T3.** The historical `plan.md` was extracted at
   the *spec's* commit (`4a85ae5`, where the plan was still F1's) instead of the
   task's head (`eabbf15`). The agent caught the mismatch itself and recovered via
   `git show` — but the setup was wrong. Extract state files at the task's HEAD,
   not at the `spec:` field's commit.
3. **Commands run against today's tree.** The working tree is at F4's HEAD, so a
   command like `uv run pytest` proves today's state, not the archived Gate's.
   Two of the three agents flagged this unprompted and scoped their claims
   accordingly. A stricter run would use a worktree checked out at the archived
   commit.

## Consequences

- **Do NOT revert the guardrail.** It is not what drove these rejects.
- **The three archived verdicts stand as historical record** and are not edited.
  This file is the recorded finding that they were lenient.
- **Three live code defects were surfaced** and are logged for future work — see
  `.out-of-scope/2026-07-26-calibration-findings.md`. They are NOT fixed here:
  curate is a gardening pass, and fixing shipped code needs its own spec/plan.
- **Next calibration run should fix the three confounds above** before its number
  is treated as a real agreement rate.

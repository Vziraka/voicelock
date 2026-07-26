# Handoff — F4.5 Task 2 DONE, Task 3 next (the last one) · 2026-07-26

Session type: `/implement` → subagent verification → `wrap-up`. Task 2 of 3.
Mode 3, so the session continues to Task 3 without a human word.

## Changed this session
- **`tests/test_capture.py`** — the only source file. `ReentrantTeardown`
  (`BaseException`), `FakeStream.deliver()` with 2-D `(frames, channels)`
  delivery, the `delivering` / `callback_stopped` flags, and the re-entrant
  teardown guard; plus three new tests. The five pump-driven tests are
  unmodified. `capture.py` is byte-identical to base — by design, which is why
  all of it passes at base.
- State: `plan.md` (Task 2 `TODO → DOING → REVIEW → DONE`, spine refreshed),
  this file, and the verdict
  `memory/verdicts/2026-07-26-F4.5-T2.json`.
- Rationale lives where it belongs, not restated here: the per-branch design in
  `plan.md` Task 2's notes, the full evidence and the four resolved doubts in
  the verdict file.

## Failed + lesson
Nothing failed. Gate 4/4 exit 0 (`8 passed` in the capture file, `86 passed`
whole suite), Reviewer APPROVE on both axes, first pass, `rejects: 0`.
`learn` compound scan ran: **no lesson met the bar** — `"lesson": "none"`. Two
candidates were examined and both rejected in the verdict file's note; the
strongest of them ("a fake must invoke the callback it is handed") is the
substance of this feature rather than a generalization of it, and is more
honestly assessable after F5 actually inherits the pattern.

## next_action
1. **`/implement` Task 3 — the feature's LAST task.** `_on_audio` raises
   `sd.CallbackStop` instead of tearing down its own stream, landed together
   with its regression tests. Trigger satisfied: Task 2's wrap-up completed
   (verdict written, state committed) and Mode 3 is the standing go.
2. **Task 3 carries the FULL `spec.md` Verification list**, not just
   `plan.md` done-criteria — it is the last task.
3. **Expect ESCALATE_HUMAN at the Gate** on spec §5's required 31-second live
   Booth check (`uv run voicelock` → Record → past 30 s without pressing Stop →
   auto-stops, window stays responsive, Play works). Do **not** mark Task 3
   `DONE` and do **not** write its verdict until the human attests it
   (F3-T5 / F4-T5 precedent). This is the one human touchpoint left in F4.5,
   alongside the feature-end checkpoint that follows it.
4. **Repro first (defect-fix task).** Run `uv run pytest tests/test_capture.py -q`
   at base before changing `capture.py` and record the failure — Task 3's two
   new tests must fail *fast* at base via Task 2's tripwire, not hang. A fix
   whose repro was never seen failing is not a verified fix.
5. **Task 2 note that lands in Task 3:** `deliver()` absorbs `sd.CallbackStop`
   the way PortAudio does rather than re-raising it, so "the supported stop is
   used" is asserted via `stream.callback_stopped` / `stream.delivering`, or by
   calling `_on_audio` directly. The verifier confirmed both routes are open.
6. After F4.5 is DONE: `/spec` for **F5 — Camera booth**, starting with its
   TECH-PICK (offline face detect / landmark / embedding stack). Named only,
   not started.

## Where the rest lives
- Task ledger and per-task notes → `plan.md`.
- What F4.5 is and why it runs before F5 → `spec.md` §1, `roadmap.md` F4.5.
- The two findings this feature does NOT fix (3 and 4, filed for F9) →
  `.out-of-scope/2026-07-26-calibration-findings.md`.

## Pending guardrail
None. Task 2's `learn` scan proposed nothing.

## Commits
Base `8f86fc7` → build commit `f2a1013` → bookkeeping `fc7f5c8` → the wrap-up
state commit that follows this file. `0106418` is the committed `DOING` write.
Curate check: 21 verdict `.json` files vs `project.md`'s "verdicts then: 19" →
**2 tasks since the last curate; not due** (threshold 10).
Remote: **none** — local history only, nothing pushed. The push gate is the
feature-end checkpoint after Task 3.

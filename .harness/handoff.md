# Handoff — F4.5 Task 1 DONE, Task 2 next · 2026-07-26

Session type: `/implement` → subagent verification → `wrap-up`. Task 1 of 3.
Mode 3, so the session continues to Task 2 without a human word.

## Changed this session
- **`pyproject.toml`** — `"soundfile>=0.14.0"` declared in
  `[project].dependencies`. **`uv.lock`** — the two direct-edge lines only; no
  package version moved. **No code file touched** (zero `.py` / `src/` /
  `tests/` / UI files in `727fbbc..0ae0fd3`).
- State: `plan.md` (Task 1 `TODO → DOING → REVIEW → DONE`, spine refreshed),
  this file, and the verdict
  `memory/verdicts/2026-07-26-F4.5-T1.json`.
- Rationale lives where it belongs, not restated here: the dependency choice in
  `memory/decisions.md` (2026-07-26 TECH-PICK), the task's reasoning in
  `plan.md` Task 1's notes, the full verdict evidence in the verdict file.

## Failed + lesson
Nothing failed. Gate 4/4 exit 0, Reviewer APPROVE on both axes, first pass,
`rejects: 0`. `learn` compound scan ran: **no lesson met the bar** — recorded as
`"lesson": "none"` in the verdict file. The only judgment the task contained
(soundfile vs torchaudio vs dev-group vs stdlib `wave`) was made and recorded at
TECH-PICK time, before the spec existed.

## next_action
1. **`/implement` Task 2** — `FakeStream` delivers frames through the REAL
   callback + a re-entrant-teardown tripwire. Trigger satisfied: Task 1's
   wrap-up completed (verdict file written, state committed), and `spec.md`'s
   approved `Mode: Mode 3` is the standing go inside this feature.
2. **Read before building Task 2** (carried forward, still live):
   `capture.py:135-142` wraps `stream.stop()` / `stream.close()` in
   `except Exception: pass`, so the tripwire must raise a **`BaseException`
   subclass** — otherwise it is swallowed silently and Task 3's regression
   passes while the defect is still there. Full detail in Task 2's notes.
3. **Task 3 will reach the Gate as ESCALATE_HUMAN** on spec §5's required
   31-second live Booth check. Do not mark it `DONE` or write its verdict until
   the human attests it (F3-T5 / F4-T5 precedent).
4. After F4.5 is DONE: `/spec` for **F5 — Camera booth**, starting with its
   TECH-PICK (offline face detect / landmark / embedding stack). Not started
   here — named only.

## Where the rest lives
- Task ledger and per-task notes → `plan.md`.
- What F4.5 is and why it runs before F5 → `spec.md` §1, `roadmap.md` F4.5.
- The two findings this feature does NOT fix (3 and 4, filed for F9) →
  `.out-of-scope/2026-07-26-calibration-findings.md`.

## Pending guardrail
None. (The F4 Task 5 proposal was approved and written to
`constitution/project.md` during the plan session; Task 1's `learn` scan
proposed nothing new.)

## Commits
Base `727fbbc` → build commit `0ae0fd3` → bookkeeping `b48f546` → the wrap-up
state commit that follows this file. `da7b8f9` is the committed `DOING` write.
Curate check: 20 verdict `.json` files vs `project.md`'s "verdicts then: 19" →
**1 task since the last curate; not due** (threshold 10).
Remote: **none** — local history only, nothing pushed. The push gate is the
feature-end checkpoint after Task 3.

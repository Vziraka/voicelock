# Handoff

## F8 Task 2 — `lipsync.py` · REVIEW (retry 1), awaiting re-verification

**2026-07-28.** First verifier run: GATE PASS, REVIEW REJECT (Standards axis
only — Spec axis APPROVED). Finding: no test exercised the lag-search loop
at `lipsync.py`'s `score()` — every existing test used shift=0 (lag-search
irrelevant) or a shift already scoring below threshold at lag-0 too, so
collapsing the loop to lag=0-only left all 8 tests green. A direct hit on
`project.md`'s mutation-sensitivity guardrail. Fixed this session: added a
4-frame in-window-shift test, mutation-verified by temporarily collapsing
the loop and confirming only the new test fails, then reverting (working
tree confirmed byte-identical to the pre-mutation file). Task 2 moved
`REVIEW → TODO → DOING → REVIEW` (retry 1 of 3, `rejects: 1`).

### Changed this retry

- `tests/test_lipsync.py` — added
  `test_shift_inside_lag_window_still_scores_above_threshold` (4-frame
  in-window shift, asserts `is_live() is True`). `src/voicelock/lipsync.py`
  itself is unchanged (mutated and reverted during verification only —
  `git diff` on it is empty).

### Verification run this session (build-time only, not the Gate)

- `uv run ruff check .` → clean
- `uv run pytest tests/test_lipsync.py -q` → 9 passed
- `uv run pytest` → 205 passed (up from 204 pre-retry)
- Mutation check (disclosed per the guardrail): collapsed the lag-search
  loop to `range(0, 1)`, ran `test_lipsync.py` → 1 failed (the new test,
  exactly as expected), 8 passed; reverted; `diff` against a pre-mutation
  backup showed zero differences.

### next_action

**Verifier**: spawn the clean-context verifier again
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 2 (retry 1)`,
base `0f21cdd`, head `1e42625` — this retry's DOING→build commits; the
prior REJECT's full-task diff `bc91244`..`6959dee` is also in history for
whole-task context). Mode 3 build↔verify cycles run unattended.

### Session commits

This retry's DOING → build: `0f21cdd` → `1e42625`. Full Task 2 history:
`bc91244` (DOING) → `6959dee` (build 1) → `c81a34e` (handoff 1) →
`16d6769` (REJECT 1 recorded) → `0f21cdd` (DOING retry 1) → `1e42625`
(build 2, this retry) → next commit is this file (bookkeeping 2).

### Open items for whoever picks up Task 3 (unchanged from before this retry)

- Task 3 (Booth bridge) needs both Task 1 and Task 2 landed — it imports
  both `challenge.py` and `lipsync.py`.
- `LIVENESS_CAPTURE_CEILING_SECONDS` must be dry-run-measured against
  Task 1's authored phrase pool before being pinned, replacing spec §2
  Q2's provisional "~6-8 s" — per `plan.md`'s Task 3 notes.
- The audio envelope Task 3 builds for the real unlock flow must use the
  same fixed-hop-at-`FRAME_INTERVAL` construction `test_lipsync.py`'s
  local `_envelope()` helper mirrors (plan.md decision 5) — not an import,
  Task 3 writes its own copy in `app.py`.

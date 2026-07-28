# Handoff

## F8 Task 1 — Vendor Vosk + `challenge.py` · REVIEW (retry 1), awaiting re-verification

**2026-07-28.** First verifier run: GATE PASS, REVIEW REJECT (Standards axis
only — Spec axis APPROVED). Finding: `ChallengeError` at
`src/voicelock/challenge.py` had zero callers and zero test references,
violating `project.md`'s earned no-unexercised-surface guardrail. Fixed this
session by deleting the class; `check()`/`matches()` already return plain
`bool` and never raise, so no exception type is needed for this task's scope.
Task 1 moved `REVIEW → TODO → DOING → REVIEW` (retry 1 of the 3-attempt
budget, `rejects: 1` in `plan.md`).

### Changed this retry

- `src/voicelock/challenge.py` — deleted the unused `ChallengeError` class.
  Nothing else touched.

### Verification run this session (build-time only, not the Gate)

- `uv run ruff check .` → clean
- `uv run pytest` → 196 passed (unchanged from the pre-retry run — the fix
  removed dead code only, no test depended on it)

### next_action

**Verifier**: spawn the clean-context verifier again
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 1 (retry 1)`,
base `1d4b261`, head `1b7635e` — this retry's DOING→build commits; the
prior REJECT's full-task diff `b3be5c6`..`5e637e1` is also in history if the
verifier wants the whole task's context). Mode 3 build↔verify cycles run
unattended, no human input needed.

### Session commits

This retry's DOING → build: `1d4b261` → `1b7635e`. Full Task 1 history:
`b3be5c6` (DOING) → `5e637e1` (build 1) → `d99cea2` (handoff 1) → `796fad3`
(REJECT 1 recorded) → `1d4b261` (DOING retry 1) → `1b7635e` (build 2, this
retry) → next commit is this file (bookkeeping 2).

### Open items for whoever picks up Task 2 (unchanged from before this retry)

- `lipsync.py` is next (independent of Task 1, per `plan.md`'s ordering
  rationale) — confirm the exact upper/lower inner-lip landmark indices
  against MediaPipe's published topology before hard-coding them.
- `SYNC_THRESHOLD` and the lag-window width (Task 2) remain
  measured-not-guessed constants per `project.md`'s dry-run-before-pinning
  guardrail — Task 2's own `plan.md` notes say what to measure them
  against.

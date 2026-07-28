# Handoff

## F8 Task 1 — Vendor Vosk + `challenge.py` · DONE

**2026-07-28.** Verified and wrapped up. `rejects: 1` (one Standards-axis
REJECT — an unused `ChallengeError` class, fixed same session — see
`memory/verdicts/2026-07-28-F8-T1.json` for the full history).

### Changed (final state)

- `pyproject.toml` / `uv.lock` — `vosk>=0.3.45` added, resolved cleanly, no
  other pinned package moved.
- `src/voicelock/models/vosk/vosk-model-small-en-us-0.15/` (new) — vendored
  offline, `LICENSE` (Apache-2.0) + `NOTICE` (per-asset evidence) beside it.
- `src/voicelock/challenge.py` (new) — `CHALLENGE_PHRASES` (12 hand-authored
  phrases), `pick_challenge()`, `matches()`, `check()`.
- `tests/test_challenge.py` (new) — 10 tests.

### Failed + lesson

REJECT 1: unused `ChallengeError` class (no callers, no tests) — the fourth
occurrence of `project.md`'s existing no-unexercised-surface guardrail
(added 2026-07-26 on three F4 REJECTs of the same shape). No new guardrail
written this task — not a new pattern, the existing rule caught it as
designed. Full reasoning in the verdict file's `note` field.

### next_action

**Task 2 — `lipsync.py`** (independent of Task 1, ordered second only
because Task 1 carried the dependency work — see `plan.md`'s "Named
architecture decisions" section, decision 4, for the exact call shapes).
Mode 3's standing approval covers task-to-task progression inside this
feature — this wrap-up completing is the precondition; the next `/implement`
session starts Task 2 itself. Open items carried forward, unchanged:

- Confirm the exact upper/lower inner-lip landmark indices against
  MediaPipe's published topology before hard-coding them in `lipsync.py`
  (same care F7 took confirming SFace's embedding width before importing
  it).
- `SYNC_THRESHOLD` and the lag-window width are measured-not-guessed
  constants (Task 2's own `plan.md` notes say what to measure them
  against), per `project.md`'s dry-run-before-pinning guardrail.

### Where the rest lives

Full task history, decisions, and the licence-evidence trail: `plan.md`
Task 1 (notes + build notes + feedback log), `memory/verdicts/2026-07-28-
F8-T1.json`, `src/voicelock/models/vosk/NOTICE`.

### Session commits

Task 1 full history: `b3be5c6` (DOING) → `5e637e1` (build 1) → `d99cea2`
(handoff 1) → `796fad3` (REJECT 1 recorded) → `1d4b261` (DOING retry 1) →
`1b7635e` (build 2) → `6ac0a59` (handoff 2) → next commit is this
wrap-up's state-file checkpoint (plan.md DONE + verdict + this handoff).

### Pending guardrail

None.

### Curate due

12 tasks since the last curate pass (2026-07-26, verdicts then: 29; now 41).
A reminder only — curate stays human-invoked, nothing blocks on it.

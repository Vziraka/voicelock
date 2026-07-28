# Handoff

## F8 Task 2 — `lipsync.py` · DONE

**2026-07-28.** Verified and wrapped up. `rejects: 1` (one Standards-axis
REJECT — an untested lag-search loop, fixed same session — see
`memory/verdicts/2026-07-28-F8-T2.json` for the full history).

### Changed (final state)

- `src/voicelock/lipsync.py` (new) — `mouth_aperture()`, `score()`/
  `is_live()`, constants `LAG_WINDOW = 5`, `SYNC_THRESHOLD = 0.5` (dry-run
  measured on `speakerA_live.wav`).
- `tests/test_lipsync.py` (new) — 9 tests, including the retry's
  lag-search-exercising in-window-shift test.

### Failed + lesson

REJECT 1: no test exercised the lag-search loop itself (every case used
shift=0 or a shift already below threshold at lag-0 too) — a hit on
`project.md`'s existing mutation-sensitivity guardrail (second confirmed
firing, first was F5 Task 5). No new guardrail written — not a new
pattern. Full reasoning, including a self-critical note about running the
mutation check proactively during build rather than only after a REJECT,
is in the verdict file's `note` field.

### next_action

**Task 3 — Booth bridge** (`app.py`): AV-capture retention, the liveness
gate wired before `vault.unlock`, `auth_liveness` reject. Needs both Task 1
and Task 2 landed (now true) — imports `challenge.py` and `lipsync.py`.
Mode 3's standing approval covers task-to-task progression — this wrap-up
completing is the precondition; the next `/implement` session starts
Task 3 itself. Carried-forward open items (`plan.md`'s Task 3 notes have
the full detail):

- `LIVENESS_CAPTURE_CEILING_SECONDS` must be dry-run-measured against
  Task 1's authored phrase pool before being pinned (read the longest
  phrase aloud, or a documented words-per-second estimate), replacing
  spec §2 Q2's provisional "~6-8 s".
- The audio envelope for the real unlock flow must use the same
  fixed-hop-at-`FRAME_INTERVAL` construction `test_lipsync.py`'s local
  `_envelope()` helper mirrors — Task 3 writes its own copy in `app.py`,
  not an import (that helper is test-local, not part of `lipsync.py`'s
  public surface).
- `start_unlock_capture()`/`stop_unlock_capture()` mirror the existing
  `start_record()`/`stop_record()` pair's ordering and mic-failure
  handling exactly (plan.md decision 6) — do not improvise a new shape.

### Where the rest lives

Full task history, decisions, and the measurement trail: `plan.md` Task 2
(notes + build notes + feedback log), `memory/verdicts/2026-07-28-F8-T2.json`.

### Session commits

Task 2 full history: `bc91244` (DOING) → `6959dee` (build 1) → `c81a34e`
(handoff 1) → `16d6769` (REJECT 1 recorded) → `0f21cdd` (DOING retry 1) →
`1e42625` (build 2) → `9230111` (handoff 2) → next commit is this
wrap-up's state-file checkpoint (plan.md DONE + verdict + this handoff).

### Pending guardrail

None.

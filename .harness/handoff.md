# F7 — Task 2 (merged) · retry 1 of 3 · BUILT, IN REVIEW

**Base (this retry):** `656cd65` (Task 2's prior REVIEW build commit).
**Build commit (retry 1 fix):** `436660d` — `tests/test_booth_api.py` (5 new
tests) + `plan.md` (feedback logged, `rejects: 1`, back to `REVIEW`).

## What happened
First verification pass: **GATE PASS** (181 passed, ruff 0), **REVIEW
REJECT** (Standards + Spec axes, narrow and mechanical — no crypto or
peel-order defect). Full findings quoted in `plan.md`'s Task 2 feedback log.
Summary: three new face-bridge surfaces shipped with zero test coverage —
`enroll_face_take()`'s `no_face` edge (both the no-frame and faceless-frame
cases), `unlock()`'s equivalent new `no_face` edge, and
`reset_enroll_face_takes()` had zero callers and zero tests anywhere in the
diff (a direct hit on `project.md`'s earned no-unexercised-surface
guardrail).

**Fix, same session (Mode 3 — unattended retry):** re-read the feedback
first, then added 5 tests to `tests/test_booth_api.py`, each mirroring the
already-covered voice-side equivalent exactly:
`test_bridge_enroll_face_take_rejects_a_faceless_frame`,
`test_bridge_enroll_face_take_no_camera_frame_yet`,
`test_reset_enroll_face_takes_discards_an_abandoned_run`,
`test_bridge_unlock_no_camera_frame_yet`,
`test_bridge_unlock_no_face_in_current_frame`. Chose to add coverage rather
than delete `reset_enroll_face_takes()` (the other valid fix per F4's
precedent) because `plan.md` decision 3 explicitly commits to building this
method in this task, mirroring the voice pair — deferring it to Task 3
would just recreate the gap when the UI needs it.

No production code changed in this retry — only test coverage was added.
`src/voicelock/vault.py` and `src/voicelock/app.py` are unchanged since the
first verification pass.

## Gate commands run this session (this retry)
- `uv run ruff check .` → exit 0
- `uv run pytest tests/test_booth_api.py -q` → exit 0, **41 passed** (36 + 5 new)
- `uv run pytest` → exit 0, **186 passed** (up from 181; 0 failed)

## What the verifier should know
- This is **retry 1 of 3** (`plan.md`'s `rejects: 1`) — the prior REJECT's
  reasoning is quoted in full in `plan.md`'s Task 2 feedback log; re-check
  that each of the three findings is now actually covered, not just that the
  suite is green.
- No production code (`vault.py`, `app.py`) changed since the first pass —
  only `tests/test_booth_api.py` gained 5 tests. If re-reviewing the Spec/
  Standards axes on production code, the first verifier's notes on scope
  (the vault+bridge merge, `memory/deviations.md` F7-T2) still apply
  unchanged.
- `middlelock.py`, `voiceprint.py`, `faceprint.py`, `facedetect.py`,
  `facelock.py` remain untouched.

## next_action
Mode 3 is the standing "go". Spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, verbatim, task id `Task 2`, base `656cd65`,
head `436660d`) — this session proceeds immediately. On APPROVE, `wrap-up`
marks Task 2 `DONE` and Task 3 (Booth UI, the LAST task) starts unattended.
On a second REJECT, `rejects` → 2/3 and the same unattended retry protocol
applies; a third REJECT sets Task 2 `BLOCKED` per the universal cap.

## Pending guardrail
Still open from the prior handoff: the recurring signature-coupling BLOCKED
shape (F4 Task 3, now F7 Task 2) is worth raising at this task's `learn`
scan once APPROVE lands, including that F4's own proposed guardrail for it
was never adopted into `project.md`.

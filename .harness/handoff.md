# F7 — Task 2 (merged) · DONE · Task 3 next

**Verdict:** `memory/verdicts/2026-07-27-F7-T2.json` — GATE PASS, REVIEW
APPROVE on retry 1 of 3, mechanism `subagent`.
**Final build commit:** `436660d`. **Base:** `9d2b4b6`.

## Changed
`src/voicelock/vault.py` — bumped to v3, nested face inner lock (Q3's
layout verbatim), `FaceAuthError`, both legacy versions refused by name.
`src/voicelock/app.py` — Booth bridge: `_enroll_faceprints`,
`enroll_face_take()`/`reset_enroll_face_takes()` (mirroring the voice
pair), `need_face_takes` guard, `unlock()`'s face capture + `auth_face`
mapping. Test files: `tests/test_vault.py`, `tests/test_outer_lock.py`,
`tests/test_middlelock.py` (unavoidably coupled callers), and
`tests/test_booth_api.py` (36 tests + 5 more on the REJECT-1 retry).

## Failed + lesson
**Two things worth carrying forward, both already closed out:**
1. A plan-contradiction BLOCKED stop (identical shape to F4 Task 3) —
   resolved by human decision to merge this task with the former standalone
   bridge task (`memory/deviations.md` F7-T2). **This recurrence is now a
   guardrail** — human-approved and written to `project.md`: "when `/plan`
   splits a signature change to a shared function across two tasks, grep for
   every in-repo caller before assigning `files:` lines."
2. One REJECT (retry 1 of 3) for missing test coverage on new bridge
   surfaces (`no_face` edges, an unexercised `reset_enroll_face_takes()`) —
   fixed same session, no new guardrail needed (the existing
   no-unexercised-surface guardrail already covers it; it caught the gap
   exactly as designed).

## next_action
Mode 3 is the standing "go" — **Task 3** (Booth UI: enroll-face capture
step + third reject chip — the LAST task, full spec Verification including
the required live manual check) starts unattended, same session.
(curate due — 10 verdicts since `Last curated: 2026-07-26`)

## Where the rest lives
`plan.md`'s Task 3 entry (renumbered from the former Task 4) — notes and
done-criteria unchanged from the original plan, just the number moved.

## Commits this session
`9d2b4b6` (Task 2 DOING) → `7272339` (vault half BLOCKED) → `6147254`
(UNBLOCKED, plan amended) → `656cd65` (bridge half, REVIEW) → `cea959a`
(handoff) → `436660d` (retry 1 fix, REVIEW) → `f8138c8` (retry handoff) →
this wrap-up's commits (verdict + project.md guardrail + plan.md DONE).

## Pending guardrail
None — the one earned this task was human-approved and written during this
wrap-up (see `project.md`'s newest `[Forbidden]` entry, dated 2026-07-27).

# Handoff — F3 spec amended (Reset control); next: HUMAN re-checks box 2

## Session
- Date: 2026-07-23
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: **spec amendment** — Reset control drafted; awaiting box-2 re-approval
- Mode: **Mode 3** (unchanged)

## What changed this turn (spec amendment only — no code)
- `spec.md`: added a **Reset** control to F3.
  - §0 Approval gate: **box 2 un-checked `[ ]`** + a dated amendment note. Grilling
    box 1 stays `[x]` (Status still CLEAR; `[NEEDS-CLARIFICATION:` scan = 0).
  - §1 Outcome: Reset clears the reference → no-reference state.
  - §2 Interaction/UX row: updated to include the Reset action.
  - §4 Constraints: new "Reset reference" bullet — deletes
    `~/.voicelock/voiceprint.ref` + discards any half-finished take run, empties
    the 3-take progress, returns the meter to "set reference first"; **no confirm
    prompt**; Python owns the clear, JS renders only.
  - §5 Verification: new automated check (`tests/test_booth_api.py` —
    `reset_reference` clears the reference so `compare` → `no_reference` again,
    file gone) + a Reset step added to the manual demo line.
- `roadmap.md`: parked **F11 — Manage enrollment from inside the vault**
  (post-F7; human-requested 2026-07-23; not yet specced).
- No `plan.md` re-plan yet, no code — those wait for box-2 re-approval.

## Two UX decisions baked into the amendment (change before approving if you disagree)
- Reset needs **no confirmation prompt** (low-stakes, re-settable).
- Reset **also discards a half-finished 1-or-2-take run** (always a clean slate).

## Next action
1. **HUMAN:** in `spec.md` §0, review the amendment + the changed sections
   (§1/§4/§5), then **re-type the `x` in box 2** (Approved by human). The agent
   never checks it.
2. On approval → **re-plan** (this session or a fresh one):
   - Add **Task 5 — Reset control** as the new LAST task; its done-criterion =
     the FULL §5 Verification (now incl. the reset test + the reset manual step).
   - Reclassify **Task 4** to intermediate and **close it DONE** on its already-
     passed automated verification (verifier: Gate exit 0 + both Review axes
     APPROVE; the ESCALATE was only the manual line, which moves to Task 5).
     Human approved this closure path 2026-07-23.
   - Build Task 5 (commit DOING first) → verify → the human runs ONE combined
     manual Booth demo (set reference · same→accept · different→reject · reset).

## Where the rest lives
- Task ledger + spine: `plan.md` (not re-planned yet — Task 4 still shows REVIEW).
  Requirements: `spec.md`. Deviations: `memory/deviations.md`.

## Commits
- This turn: spec amendment + roadmap park + state (see git log after commit).
- Remote: none — local history only, no push.

## Pending guardrail
- None.

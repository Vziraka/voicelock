# Handoff — F3 amendment approved; Task 4 DONE; next: /implement Task 5 (Reset)

## Session
- Date: 2026-07-23
- Feature: F3 — Voiceprint on screen (`spec.md`, amended 2026-07-23)
- Phase: Task 4 DONE (intermediate close); Task 5 (Reset, LAST task) TODO
- Mode: **Mode 3**

## Done this turn
- Human re-approved the Reset amendment (spec `b0eaad8`, box 2 `[x]`).
- Closed **Task 4** as an intermediate DONE on its passed automated verification
  (verifier: `ruff` 0, full `pytest` 33 passed, `test_voiceprint` 9 passed, both
  Review axes APPROVE; overall ESCALATE was only the manual demo). Verdict:
  `memory/verdicts/2026-07-22-F3-T4.json` (APPROVE). The FULL-§5 manual demo moved
  to Task 5 (new last task). Human-approved closure path.
- Re-planned: added **Task 5 — Reset control** as the LAST task.

## next_action
- `/implement` **Task 5** (commit DOING first):
  - `src/voicelock/app.py`: `BoothApi.reset_reference()` → delete the injectable
    `ref_path` (no-op if absent) + clear `_reference_takes`; return `{ok: true}`.
  - `src/voicelock/ui/index.html`: a **Reset** button in the `.voiceprint` panel
    → calls the bridge → `showSetReferenceFirst()` + `setReferenceProgress(0)`.
    JS renders only; no confirm prompt. Keep everything else unchanged.
  - `tests/test_booth_api.py`: after a reference is set, `reset_reference` clears
    it → `compare` returns `no_reference` again + the file is gone.
  - Done-criterion = FULL amended §5 (ruff · full pytest · test_voiceprint ·
    test_booth_api · human-attested manual demo incl. the reset step).
- After the automated Gate passes, the manual demo needs the HUMAN (real mic) —
  expect verifier ESCALATE_HUMAN on the manual line; the human runs ONE combined
  demo, then wrap-up marks Task 5 DONE + writes the Mode-3 completion report,
  completing F3.

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md` (amended). Deviations:
  `memory/deviations.md`. Roadmap F11 parked (vault-side enrollment management).

## Commits
- Amendment: `2d99487` · approval: `b0eaad8` · Task 4 close + re-plan: this commit.
- Remote: none — local history only, no push.

## Pending guardrail
- None.

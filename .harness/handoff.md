# Handoff — F1 completion report (Mode 3)

Feature 1 is complete pending the feature-end commit/push checkpoint.

## Outcome vs spec
Spec Outcome: local Booth window — record from mic, live visualizer, play back.
Shipped: `uv run voicelock` opens the Booth; Record/Stop/Play wired through
pywebview; bars react to levels; mic errors disable Record; soft-cap take-ready;
Stop works during playback. No auth/vault/voiceprint (non-goals held).

## Final Gate evidence (Task 5)
- `uv run ruff check .` → exit 0
- `uv run pytest` → exit 0 (8 passed, 0 failed)
- `uv run pytest tests/test_capture.py tests/test_playback.py -q` → exit 0 (7 passed)
- Manual `uv run voicelock` Record → viz → Stop → Play → human-attested PASS

## Retry counts
- Task 1: rejects 0
- Task 2: rejects 0
- Task 3: rejects 0
- Task 4: rejects 0
- Task 5: rejects 1 (soft-cap Play) + human stoppable-playback fix after demo

## Deviations
None recorded in `memory/deviations.md` during F1.

## Escalations
Gate ESCALATE_HUMAN on live Booth (accepted blind spot) — resolved by human
manual demo PASS. Soft-cap REJECT fixed before that.

## Next
Roadmap F1 checked. Next feature is F2 (passphrase-only vault) via `/spec` when
you want it. Feature-end checkpoint: approve the wrap-up commit message (and
push if/when you want a remote — currently none).

- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `memory/verdicts/2026-07-22-F1-T{1..5}.json` · `memory/codebase-map.md`
- **Wrap-up:** complete for Task 5 / F1 — awaiting feature-end commit approval

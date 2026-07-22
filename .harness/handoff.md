# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 5 REJECT (review) — soft-cap auto-stop
  does not set take-ready / Play. `rejects: 1`. Feedback in `plan.md`.
- **Commits:** base 72b7fab4cabafd45bc19a0852d82f683ba314346 → head
  06c8560d7f568db019b8420ad171cfd4c54d830f (rejected build)
- **Failed + lesson:** soft-cap path must push sample count into JS so `hasTake`
  enables Play before the next Record clears the buffer.
- **Next action:** Mode 3 — re-implement Task 5 per feedback (rejects 1/3)
- **Pending guardrail:** none
- **Where the rest lives:** `plan.md` Task 5 feedback · `src/voicelock/app.py` ·
  `src/voicelock/ui/index.html`
- **Wrap-up:** not run — REJECT path

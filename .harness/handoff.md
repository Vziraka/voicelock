# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 4 Booth UI chrome — `src/voicelock/ui/index.html`
  (mock layout; Record/Stop/Play + canvas + mic-error hooks; no Google Fonts).
- **Commits:** base 1b0c865a3a8f1f31831ec4ac19305a7ef479535f → head
  ac884d834c161cfae65623e40708b9945f5c1f37
- **Failed + lesson:** none
- **Next action:** Mode 3 — clean-context verifier for Task 4
  (`formats/VERIFIER-PROMPT.md`, fill-ins only).
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `design/voicelock-mock.html` · `memory/verdicts/2026-07-22-F1-T3.json`
- **Local smoke (implementor, disclosed):** Task 4 python path assert ·
  `uv run ruff check .` — exit 0; Gate still owns verification.
- **Wrap-up:** not run — awaiting verifier

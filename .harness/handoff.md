# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 2 capture engine — `src/voicelock/capture.py`,
  `tests/test_capture.py` (fake streams: start/stop buffer, levels, mic error, 30s cap).
- **Commits:** base 8cb7572adfe764ab0ef38d67e3d21c1589bafb08 → head
  6c0329bf4b167522903c14ac6d98e019743e41c6
- **Failed + lesson:** none
- **Next action:** Mode 3 — clean-context verifier for Task 2
  (`formats/VERIFIER-PROMPT.md`, fill-ins only).
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `memory/decisions.md` · `memory/verdicts/2026-07-22-F1-T1.json` ·
  `memory/research/2026-07-22-f1-audio-capture.md`
- **Local smoke (implementor, disclosed):** `uv run pytest tests/test_capture.py -q`
  · `uv run ruff check .` — exit 0; Gate still owns verification.
- **Wrap-up:** not run — awaiting verifier

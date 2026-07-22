# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 3 playback engine — `src/voicelock/playback.py`,
  `tests/test_playback.py` (injectable play/wait; non-empty buffer completes).
- **Commits:** base 10233150695d12d385e28f3cc0979661efd4302a → head
  dc11dfd744c7fa16d44b0abed2d00b72b89bc8de
- **Failed + lesson:** none
- **Next action:** Mode 3 — clean-context verifier for Task 3
  (`formats/VERIFIER-PROMPT.md`, fill-ins only).
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `memory/decisions.md` · `memory/verdicts/2026-07-22-F1-T2.json` ·
  `memory/research/2026-07-22-f1-audio-capture.md`
- **Local smoke (implementor, disclosed):** `uv run pytest tests/test_playback.py -q`
  · `uv run ruff check .` — exit 0; Gate still owns verification.
- **Wrap-up:** not run — awaiting verifier
- **Note:** Task 3 DOING landed in the Task 2 wrap-up commit (same HEAD base);
  build commit is separate.

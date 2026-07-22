# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 5 pywebview Booth host — `src/voicelock/app.py`,
  `__main__.py`, `ui/index.html` bridge wiring, `[project.scripts] voicelock`.
- **Commits:** base 72b7fab4cabafd45bc19a0852d82f683ba314346 → head
  06c8560d7f568db019b8420ad171cfd4c54d830f
- **Failed + lesson:** none
- **Next action:** Mode 3 — clean-context verifier for Task 5 (LAST; FULL
  Verification list). Manual demo line (`uv run voicelock` Record→Stop→Play)
  needs human observation; automated Gate commands are the exit-0 subset.
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` Verification · `plan.md` ·
  `src/voicelock/capture.py` · `src/voicelock/playback.py` · `src/voicelock/ui/`
- **Local smoke (implementor, disclosed):** `uv sync` · `uv run ruff check .` ·
  `uv run pytest` — exit 0; Gate still owns verification.
- **Wrap-up:** not run — awaiting verifier

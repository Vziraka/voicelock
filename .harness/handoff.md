# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 1 scaffold — `pyproject.toml`, `uv.lock`,
  `.python-version` (3.11), `src/voicelock/__init__.py`, `tests/test_package.py`.
  Approved deps only (pywebview, sounddevice, numpy, ruff, pytest). Numpy pinned
  `>=2.0,<2.3` because numpy 2.5.x needs Python ≥3.12 and the stack is 3.11.
- **Commits:** base 4d0a2778104cec36d0b4306b275bc07856f79d27 → head
  2bcd5f5ddb04fd7b794265a54e4f299f700075b6
- **Failed + lesson:** none
- **Next action:** Mode 3 — clean-context verifier for Task 1
  (`formats/VERIFIER-PROMPT.md`, fill-ins only).
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `memory/decisions.md` · `memory/research/2026-07-22-f1-ui-shell.md` ·
  `memory/research/2026-07-22-f1-audio-capture.md`
- **Local smoke (implementor, disclosed):** `uv sync` · `uv run ruff check .` ·
  `uv run pytest` — all exit 0 this session; Gate still owns verification.
- **Wrap-up:** not run — awaiting verifier

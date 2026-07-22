# Conventions — VoiceLock

The full naming / structure / style guide. The non-negotiables are mirrored as
rules in `project.md`; this is the detail behind them.

Declared greenfield via `intake-scaffold` (2026-07-22), after `design` locked
Approach B and F1–F6. Marked defaults may be revisited when real code exists.
UI toolkit (desktop shell) is deferred to F1 TECH-PICK.

## Stack (human-decided)
- Python **3.11** + **uv** (`pyproject.toml` + `uv.lock`). No bare pip installs.
- Engine (audio, crypto, voiceprint) in Python; booth **looks** in HTML/CSS/JS.
- Desktop UI shell TBD at F1 (TECH-PICK) — must render JS UI and bridge to Python.
- Design mock under `design/` is a **reference starting point**, not final chrome
  (human will edit animations / polish over time).
- Offline-only at runtime — no network calls.
- No new dependencies without human approval (TECH-PICK).

## Naming
- Files/modules: `snake_case.py`
- Functions/methods/variables: `snake_case`
- Types/classes: `PascalCase`
- Tests: `tests/test_<module>.py`
- Prefer `CONTEXT.md` terms in identifiers (vault, booth, enroll, voiceprint…).

## Structure
- App code: `src/voicelock/`
- UI assets (HTML/CSS/JS): `src/voicelock/ui/`
- Tests: `tests/` (top-level)
- Design reference (read-only source of visual truth until adapted): `design/`
- Python owns audio / DSP / crypto / state; JS owns rendering only.

## Style
- Lint: **ruff** — `uv run ruff check .` must exit 0.
- Tests: **pytest** — `uv run pytest` must exit 0. Audio tests use injected fake
  streams; never depend on a real microphone in automated tests.
- Patterns we use: booth UI modes; stacked outer/inner locks per roadmap;
  glossary terms in code and docs.
- Patterns we avoid: business logic in JS; network access; global mutable state;
  claiming deepfake-proofing.

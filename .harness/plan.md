# Plan — F1 — The recording booth

## Active context
- Updated: 2026-07-22
- Spec: `spec.md` · Feature: Feature 1 from `roadmap.md` · Mode: Mode 3 · Phase: implement
  (next: Task 4 — Booth UI chrome · DOING)
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only when the Gate exited 0 **and** the Reviewer approved.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — Scaffold uv package + Gate tooling (`pyproject.toml`, `uv.lock`, `src/voicelock/__init__.py`, `tests/` so pytest collects)
  - state: DONE
  - rejects: 0
  - files: `pyproject.toml`, `uv.lock`, `src/voicelock/__init__.py`, `tests/` (minimal so the suite runs)
  - notes: pin approved deps only — pywebview, sounddevice, numpy, ruff, pytest. No entry-point window yet.
  - done-criteria:
    - `uv sync` → exit 0
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [x] **Task 2** — Capture engine with injectable streams (`src/voicelock/capture.py`, `tests/test_capture.py`)
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/capture.py`, `tests/test_capture.py`
  - notes: 16 kHz mono PCM; click-toggle start/stop; soft auto-stop at 30s; emit level frames for bars; mic-unavailable returns an error state (no crash, no silent success). Tests inject fake streams only.
  - done-criteria:
    - `uv run pytest tests/test_capture.py -q` → exit 0; final summary reports 0 failed. Must cover with injected fake streams: (1) start/stop yields a non-empty PCM buffer; (2) level frames emit during capture; (3) mic-unavailable surfaces an error state; (4) recording auto-stops by the 30s soft cap (fake/fast stream or clock is fine).
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [x] **Task 3** — Playback engine with injectable streams (`src/voicelock/playback.py`, `tests/test_playback.py`)
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/playback.py`, `tests/test_playback.py`
  - notes: play a captured PCM buffer to completion; tests inject fake output device/stream — no real speakers required in Gate.
  - done-criteria:
    - `uv run pytest tests/test_playback.py -q` → exit 0; final summary reports 0 failed. Must cover: playback of a non-empty captured buffer completes without error (injected fake stream).
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [ ] **Task 4** — Booth UI chrome from mock, offline (`src/voicelock/ui/` adapted from `design/voicelock-mock.html`)
  - state: REVIEW
  - rejects: 0
  - files: `src/voicelock/ui/index.html` (and any split CSS/JS under `src/voicelock/ui/` if extracted)
  - notes: keep mock layout/branding/sidebar/panels as visual context. Only prepare DOM hooks for Record / Stop / Play, bars canvas, and a mic-error message — wiring is Task 5. Strip runtime network font loads (offline-only). Other mock controls stay visible and inert.
  - done-criteria:
    - `uv run python -c "from pathlib import Path; p = Path('src/voicelock/ui'); assert (p / 'index.html').is_file(); t = (p / 'index.html').read_text(encoding='utf-8'); assert 'record' in t.lower(); assert 'canvas' in t.lower(); assert 'fonts.googleapis.com' not in t.lower(); assert 'fonts.gstatic.com' not in t.lower()"` → exit 0
    - `uv run ruff check .` → exit 0
  - feedback: (none)

- [ ] **Task 5** — pywebview Booth host + bridge: live record → bars → play (+ mic error); `uv run voicelock` entry
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py` (or equivalent host module), `src/voicelock/__main__.py` and/or `[project.scripts]` entry in `pyproject.toml`, bridge API, `src/voicelock/ui/` JS hooks wired to Python capture/playback
  - notes: LAST task — Gate runs the FULL Verification list from `spec.md`. Click-toggle Record/Stop; manual Play after stop; bars react to level frames while recording; mic missing/denied disables Record and shows a short Booth message; window stays open. Auto-discovered out-of-scope work → `.out-of-scope/`, never build.
  - done-criteria: FULL list from `spec.md` **Verification** (standing + feature-specific + required manual demo line)
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-22 — F1 Task 4 REVIEW: Booth UI chrome offline with Record/Stop/Play hooks.
2. Capture + playback ready with injectable streams (Gate-safe).
3. Live Booth still Tasks 4–5 (chrome then pywebview bridge).
4. Blind spot accepted: live window/mic proven only by manual Verification (Task 5).
5. Mode 3 standing go — continue until feature-end checkpoint.

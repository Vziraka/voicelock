# Handoff

## F8 Task 1 — Vendor Vosk + `challenge.py` · REVIEW, awaiting verification

**2026-07-28.** Built and committed. Task 1 moved `DOING → REVIEW`.

### Changed

- `pyproject.toml` — added `vosk>=0.3.45` to `dependencies`.
- `uv.lock` — resolved `vosk==0.3.45` (+ its transitives `cffi`/`requests`/
  `tqdm`/`srt`/`websockets`); diff is additions only, no other pinned
  package moved.
- `src/voicelock/models/vosk/vosk-model-small-en-us-0.15/` (new) — the
  vendored model, downloaded fresh from `alphacephei.com/vosk/models/
  vosk-model-small-en-us-0.15.zip`, `LICENSE` (Apache-2.0, reused pristine
  text) and `NOTICE` (source, size, sha256, and the per-asset licence
  evidence — the distribution page's own table, since the archive's
  bundled README carries no licence text itself).
- `src/voicelock/challenge.py` (new) — `CHALLENGE_PHRASES` (12 own-authored
  short sentences), `pick_challenge()`, `matches()`, `check()`.
- `tests/test_challenge.py` (new) — 10 tests: pool/no-repeat, `matches()`
  synthetic table, one real (unmocked) Vosk reject-path run against
  `speakerA_take1.wav`.

### Measured/decided during build (not guessed)

- Vosk's real constructor signature was confirmed by reading the installed
  package's own source (`vosk.KaldiRecognizer(model, sample_rate,
  grammar_json_str)`), not assumed from the spec-time research.
- The reject-path Gate test was dry-run before being written into the test
  file, per the dry-run-before-pinning guardrail: against the full
  12-phrase grammar, `speakerA_take1.wav` recognizes as `"the [unk]"`,
  which does not match any challenge phrase — a real reject.
- Model licence: the vendored archive's own bundled `README` states only
  "Copyright 2020 Alpha Cephei Inc" with no licence text — checked first,
  per the metadata-first clause. The distribution page's own per-model
  table (`alphacephei.com/vosk/models`) names `vosk-model-small-en-us-0.15`
  specifically with `License: Apache 2.0` — that is the source of record,
  recorded in the model's `NOTICE`.

### Verification run this session (build-time only, not the Gate)

- `uv run pytest tests/test_challenge.py -q` → 10 passed
- `uv run ruff check .` → clean
- `uv run pytest` → 196 passed (F7 baseline was 186; +10 from this task,
  nothing else regressed)

None of the above substitutes for the fresh-context Gate — recorded here
per the implement skill's step 5 disclosure requirement, not as a
self-verification.

### next_action

**Verifier**: spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 1`, base
`b3be5c6`, head `5e637e1`) — Mode 3 build↔verify cycles run unattended, no
human input needed to proceed.

### Session commits

Base (DOING committed) → head (build committed): `b3be5c6` → `5e637e1`.
Files this session: `pyproject.toml`, `uv.lock`,
`src/voicelock/models/vosk/**` (new), `src/voicelock/challenge.py` (new),
`tests/test_challenge.py` (new), `.harness/plan.md` (DOING → REVIEW +
build notes), `.harness/handoff.md` (this file, committed separately as
bookkeeping — HEAD after this commit is one ahead of what this file
names as "head").

### Open items for whoever picks up Task 2

- `lipsync.py` is next (independent of Task 1, per `plan.md`'s ordering
  rationale) — confirm the exact upper/lower inner-lip landmark indices
  against MediaPipe's published topology before hard-coding them.
- `SYNC_THRESHOLD` and the lag-window width (Task 2) remain
  measured-not-guessed constants per `project.md`'s dry-run-before-pinning
  guardrail — Task 2's own `plan.md` notes say what to measure them
  against.

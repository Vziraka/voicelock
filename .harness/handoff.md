# Handoff

## F8 Task 2 — `lipsync.py` · REVIEW, awaiting verification

**2026-07-28.** Built and committed. Task 2 moved `TODO → DOING → REVIEW`.

### Changed

- `src/voicelock/lipsync.py` (new) — `mouth_aperture()` (normalized
  inner-lip vertical gap), `score()`/`is_live()` (lag-windowed Pearson
  cross-correlation), constants `LAG_WINDOW = 5`, `SYNC_THRESHOLD = 0.5`.
- `tests/test_lipsync.py` (new) — 8 tests: in-phase/shifted/flat scoring
  against a real audio envelope + synthetic mouth series, mismatched-length
  tolerance, constants sanity + docstring disclosure, `mouth_aperture()`
  geometry (synthetic landmarks) + degenerate-zero-reference handling.

### Measured/decided during build (not guessed)

- Inner-lip vertical-centre indices (13/14) confirmed directly from the
  vendored Face Landmarker bundle's own `FACE_LANDMARKS_LIPS` connection
  topology (reconstructed the inner ring's edges and found 13/14 sit
  symmetric between the two inner mouth corners 78/308) — not assumed from
  index naming, same care F7 took confirming SFace's embedding width.
- `LAG_WINDOW`/`SYNC_THRESHOLD` dry-run measured on `speakerA_live.wav`
  (real audio envelope, 58 frames at `facedetect.FRAME_INTERVAL`'s hop)
  before being pinned into the test file: in-phase (affine transform of the
  envelope) scores `1.0`; the same series shifted 15 frames (3x past a
  5-frame lag window, non-circular shift) scores `-0.007`; a flat series
  scores `0.0` by construction (zero variance). `SYNC_THRESHOLD = 0.5` is
  the midpoint. Full numbers in `plan.md` Task 2's build notes.

### Verification run this session (build-time only, not the Gate)

- `uv run pytest tests/test_lipsync.py -q` → 8 passed
- `uv run ruff check .` → clean
- `uv run pytest` → 204 passed (Task 1's end was 196; +8, nothing regressed)

None of the above substitutes for the fresh-context Gate — recorded here
per the implement skill's step 5 disclosure requirement.

### next_action

**Verifier**: spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 2`, base
`bc91244`, head `6959dee`) — Mode 3 build↔verify cycles run unattended.

### Session commits

Base (DOING) → head (build): `bc91244` → `6959dee`. Files this session:
`src/voicelock/lipsync.py` (new), `tests/test_lipsync.py` (new),
`.harness/plan.md` (DOING → REVIEW + build notes), `.harness/handoff.md`
(this file, committed separately as bookkeeping).

### Open items for whoever picks up Task 3

- Task 3 (Booth bridge) needs both Task 1 and Task 2 landed — it imports
  both `challenge.py` and `lipsync.py`.
- `LIVENESS_CAPTURE_CEILING_SECONDS` must be dry-run-measured against
  Task 1's authored phrase pool (read the longest phrase aloud, or a
  documented words-per-second estimate) before being pinned, replacing
  spec §2 Q2's provisional "~6-8 s" — per `plan.md`'s Task 3 notes.
- The audio envelope Task 3 builds for the real unlock flow must use the
  same fixed-hop-at-`FRAME_INTERVAL` construction `test_lipsync.py`'s
  local `_envelope()` helper mirrors (plan.md decision 5) — that test
  helper is not exported by `lipsync.py`, so Task 3 writes its own copy
  in `app.py`, not an import.

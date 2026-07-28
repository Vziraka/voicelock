# Handoff

## F8 Task 3 — Booth bridge: liveness gate before `vault.unlock` · REVIEW, awaiting verification

**2026-07-28.** Built and committed. Task 3 moved `TODO → DOING → REVIEW`.

### Changed

- `src/voicelock/app.py` — `LIVENESS_CAPTURE_CEILING_SECONDS = 10.0` (dry-run
  estimated), `_audio_envelope()` (fixed-hop RMS at `facedetect.FRAME_INTERVAL`),
  new `BoothApi` state (`_retain_landmarks`, `_liveness_mouth_series`,
  `_current_challenge`), `new_challenge()`, `start_unlock_capture()`/
  `stop_unlock_capture()`, `unlock()` reshaped to gate on `_liveness_passes()`
  before any `vault_unlock` call, `_push_face_frame()` retains mouth-aperture
  when armed, and a fix inside `_pump_loop()`'s auto-stop branch (see below).
- `tests/test_booth_api.py` — 8 existing unlock tests updated to bypass the
  new liveness gate via a `_force_liveness_pass()` helper (monkeypatches
  `challenge.check`/`lipsync.is_live`) since they test what happens AFTER
  liveness, not liveness itself; `_StubRecordingCapture` gained a
  `max_seconds` attribute; 17 new tests covering the AV-capture lifecycle,
  retention wiring, `new_challenge()`, and the liveness gate itself.

### A real bug found and fixed during build (not by the verifier)

Writing `test_the_liveness_ceiling_auto_stop_releases_the_camera_too` (spec
§5 cmd 3's "release on every exit path including the fixed-ceiling
auto-stop") found that the fixed-ceiling auto-stop path lives in
`_pump_loop()` — it is what *notices* a take self-ended (via
`capture.pump()`'s own internal `stop()`), and calls `_stop_camera()`
directly, bypassing `stop_unlock_capture()` entirely. The first cut of
`start_unlock_capture()`/`stop_unlock_capture()` only reset
`_retain_landmarks`/`capture.max_seconds` inside the explicit-stop method,
so an auto-stopped liveness take left both fields permanently set —
silently capping the user's *next* enroll take at the shorter liveness
ceiling too. Fixed by repeating the same two-line reset inside
`_pump_loop()`'s auto-stop branch (a no-op for a plain `start_record()`
take, since neither field is ever touched there).

### Measured/decided during build (not guessed)

- `LIVENESS_CAPTURE_CEILING_SECONDS = 10.0`: no live speaker available in
  this environment, so estimated from Task 1's phrase pool's word count
  (6-word longest entries, 1.5 words/sec conservative rate ≈ 4.0 s, doubled
  for hesitation/lead-in margin ≈ 8.0 s, rounded up to 10.0 s), disclosed
  as an estimate (not a stopwatch reading) in both `app.py`'s comment and
  `plan.md`'s build notes. Replaces spec §2 Q2's provisional "~6-8 s".
- Proactively mutation-checked `unlock()`'s liveness gate before
  submitting (applying Task 2's own lesson): collapsed
  `if not self._liveness_passes():` to `if False:`, ran
  `tests/test_booth_api.py`, confirmed exactly the 5 liveness-specific
  tests fail (one unrelated pre-existing timing flake in an F5 test
  reproduced as a false positive under the mutated run and was confirmed
  independent by re-running it alone, standalone, passing), reverted —
  `diff` against a pre-mutation backup showed zero differences.

### Verification run this session (build-time only, not the Gate)

- `uv run pytest tests/test_booth_api.py -q` → 58 passed
- `uv run ruff check .` → clean
- `uv run pytest` → 222 passed (Task 2's end was 205; +17, nothing regressed)

None of the above substitutes for the fresh-context Gate — recorded here
per the implement skill's step 5 disclosure requirement.

### next_action

**Verifier**: spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 3`, base
`08676fa`, head `e571695`) — Mode 3 build↔verify cycles run unattended.

### Session commits

Base (DOING) → head (build): `08676fa` → `e571695`. Files this session:
`src/voicelock/app.py`, `tests/test_booth_api.py`, `.harness/plan.md`
(DOING → REVIEW + build notes), `.harness/handoff.md` (this file,
committed separately as bookkeeping).

### Open items for whoever picks up Task 4 (the LAST task)

- Task 4 (Booth UI) needs Task 3's bridge methods:
  `start_unlock_capture()`/`stop_unlock_capture()` (wired to the Unlock
  panel's Record/Stop instead of the plain pair), `new_challenge()`
  (called when the Unlock panel activates and after each attempt), and the
  `auth_liveness` error code for the fifth reject chip.
- Task 4's done-criteria is the FULL spec Verification list, including the
  required manual 5-outcome check — attested by the human at the
  feature-end checkpoint, not automatable.
- Per the earned Booth-layout guardrail: the challenge-phrase display is
  new visible content in the `main`/`.booth` column — smoke-test it
  manually (open the Unlock panel, watch the phrase render without
  clipping) before calling Task 4 done.

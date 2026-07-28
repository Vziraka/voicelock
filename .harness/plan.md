# Plan — F8 — Lip-sync liveness (challenge-response)

## Active context
- Updated: 2026-07-28
- Feature: Feature 8 from `roadmap.md` · Mode: **Mode 3 — Spec-to-done** ·
  Phase: **BUILDING — Task 4 DOING (LAST task).**
- Spec: `spec.md` holds F8's spec, Grilling `Status: CLEAR` (zero
  `[NEEDS-CLARIFICATION:` hits), both approval boxes checked, `Mode: Mode 3`
  set 2026-07-28 by the human.

### Why this feature exists, in one line
A single AV capture is pulled apart into four checks (challenge words, voice,
face, lip-sync); the first two new signals get their own modules, and the
liveness gate (challenge-match + lip-sync) sits **in front of** the existing
three nested locks — a wrong-liveness attempt never calls `vault.unlock()` at
all (Q6), so `vault.py` itself is untouched this feature.

### The dependency that fixes the task order
Two brand-new, mutually independent signal modules (`challenge.py`,
`lipsync.py` — spec names both, neither imports the other), then one bridge
task that imports both, then the UI. WIP=1 makes the actual order: **Task 1**
(Vosk vendoring + `challenge.py`) and **Task 2** (`lipsync.py`) could run in
either order since neither depends on the other; Task 1 goes first because it
carries the new-dependency TECH-PICK integration (mirrors F5/F6/F7's pattern
of landing the heavier, dependency-carrying module first). **Task 3** (Booth
bridge: AV-capture retention + the liveness gate wired before
`vault.unlock`) needs both Task 1 and Task 2 landed — it imports both
modules. **Task 4** (Booth UI: challenge display + capture UX + fifth reject
chip) needs Task 3's bridge methods to call.

**No `vault.py` touch this feature** — per Q6 and spec §3 non-goals, the
liveness gate wraps `vault.unlock()` from the outside in `app.py`; the three
nested AEAD layers stay exactly as F7 left them. This also means the
`project.md` guardrail about grepping every caller before splitting a vault
signature change **does not apply** here — no vault signature changes at all.

### Named architecture decisions carried into this ledger
These fill the "exact call shape" gaps the spec deliberately left to `/plan`
(same role F7's memory-spine item 1 played) — do not re-derive them mid-build.

1. **`challenge.py`'s phrase pool is a module-level constant
   `CHALLENGE_PHRASES: tuple[str, ...]`**, ~10–20 hand-authored, phonetically
   varied short sentences (Q3) — authored in Task 1, not before, since the
   AV-capture ceiling (decision 6) must be measured against the real pool
   the way `project.md`'s dry-run-before-pinning guardrail requires.
   `pick_challenge(previous: str | None = None, rng: random.Random | None =
   None) -> str` picks uniformly at random from the pool, excluding
   `previous` from the draw (no-immediate-repeat) unless the pool has only
   one entry. `rng` is injectable (mirrors this repo's standing
   injectable-dependency pattern — `open_camera`, `clock`, `landmarker`
   elsewhere) so the no-repeat property is deterministically testable over
   many draws instead of relying on statistical luck.
2. **Vosk model vendored at `src/voicelock/models/vosk/vosk-model-small-en-us-0.15/`**,
   mirroring the existing `models/<name>/` + `LICENSE` + `NOTICE` pattern
   (`models/ecapa/`, `models/face_landmarker/`, `models/sface/`). `LICENSE`
   reuses the same pristine Apache-2.0 text already vendored twice in this
   repo (consistent with the `face_landmarker` precedent); `NOTICE` names
   `vosk-model-small-en-us-0.15` specifically and cites
   `alphacephei.com/vosk/models` as the source establishing *that asset's*
   licence, per `project.md`'s per-asset-licence guardrail. `vosk` (the
   Python package, per the TECH-PICK) is added to `pyproject.toml`
   `dependencies`.
3. **`challenge.py` owns three independent, separately-testable pieces**,
   matching spec §5 cmd 1's three coverage bullets exactly:
   - `matches(recognized: str, challenge: str) -> bool` — pure text
     comparison (normalize case/punctuation, then exact match), **no** Vosk
     involved, so the synthetic table test (exact / case-punct-only /
     different) needs no model load.
   - `_ensure_model()` / a module-level cached loader — mirrors
     `facedetect.load_landmarker()`'s and `faceprint.py`'s lazy
     module-cached pattern, loading `vosk.Model(str(MODEL_PATH))` once, plus
     `vosk.SetLogLevel(-1)` at import or first load (Kaldi logs to stderr by
     default and would spam every Gate run and every live unlock attempt
     otherwise — a real, disclosed gotcha, not architecture).
   - `check(audio: np.ndarray, challenge: str, decoys: Sequence[str] =
     CHALLENGE_PHRASES) -> bool` — builds a `KaldiRecognizer` grammar JSON
     from `challenge` plus `decoys` (Q3's "rest of the pool as decoys"),
     runs `AcceptWaveform`/`FinalResult` against the audio (converted from
     this repo's standard float32 mono PCM to the int16 bytes Vosk's API
     expects — a straightforward `np.clip(...).astype(np.int16).tobytes()`
     conversion, no resampling needed since capture is already 16 kHz mono,
     the rate Vosk's small model expects), and returns `matches(recognized,
     challenge)`. This is the function the Gate's real-Vosk reject-path test
     exercises against `speakerA_take1.wav`.
4. **`lipsync.py` owns two pieces**, matching spec §5 cmd 2:
   - `mouth_aperture(landmarks: list) -> float` — one scalar per frame from
     F5's inner-lip landmark pair (upper/lower inner-lip centre points),
     normalized by a stable face-scale reference (e.g. inter-eye distance)
     from the same landmark set, so aperture does not confound with the
     subject's distance from the camera. Pure numpy, no new dependency,
     consistent with spec §4.
   - `score(mouth_series: np.ndarray, audio_envelope: np.ndarray) -> float`
     — lag-windowed normalized cross-correlation; both inputs are assumed
     **already on the same sample grid, same length** (index *i* in both is
     the same instant) — this matches exactly how spec §5's synthetic Gate
     test constructs its fixtures ("an in-phase mouth-aperture series
     derived directly from the real audio envelope"), so aligning the two
     series onto a common grid is the caller's job (Task 3), not
     `lipsync.py`'s. If the two arrays arrive at slightly different lengths
     (a real capture's frame count is not perfectly deterministic — drop-
     don't-queue pacing under load), `score()` compares over the shorter
     array's length rather than raising. `is_live(score: float) -> bool` —
     `score >= SYNC_THRESHOLD`. `SYNC_THRESHOLD` and the lag-window width
     are named constants, pinned from the synthetic separation this task's
     own Gate test measures — module docstring discloses this explicitly
     (spec §5 item 2's own requirement), mirroring `facelock.py`'s Q2
     disclosure pattern for `CORRECTION_RADIUS`.
5. **No changes to `facedetect.py` or `capture.py`.** Per spec §4's
   constraint that F1–F7 engines are "reused, not modified in their core
   constructions," the AV-capture retention Q2 asks for lives entirely in
   `app.py` (`BoothApi`), which already receives every frame's landmarks
   (`_push_face_frame`, called from `FaceEngine`'s existing callback) and
   already owns the full audio PCM buffer (`capture.pcm_buffer()`) after a
   take. Concretely:
   - `BoothApi._retain_landmarks: bool` (default `False`) and
     `BoothApi._liveness_mouth_series: list[float]` (cleared on each unlock
     capture start). `_push_face_frame` gains one **additive** line: when
     `_retain_landmarks` is set, append
     `lipsync.mouth_aperture(result.landmarks)` to the series — zero change
     to its existing `evaluate_js` call or to `FaceEngine`/`facedetect.py`.
   - The audio envelope is **recomputed post-capture** from the full
     retained `capture.pcm_buffer()` using a fixed hop equal to one video
     frame interval (`int(SAMPLE_RATE * facedetect.FRAME_INTERVAL)`
     samples per envelope value, reusing `facedetect`'s own constant rather
     than duplicating it) — the same fixed-window-RMS technique that already
     produces the Visualizer's levels (spec Q4 calls this "the audio
     envelope already computed for the Visualizer"), just re-run with a hop
     chosen to land naturally on the same per-frame grid as the
     mouth-aperture series, instead of depending on PortAudio's own
     irregular per-callback chunk boundaries. This is a plan-level call
     (spec left the exact construction to `/plan`), disclosed here so
     Task 3 does not re-derive it.
6. **New bridge methods `start_unlock_capture()` / `stop_unlock_capture()`**,
   distinct from the existing `start_record()`/`stop_record()` (which stay
   exactly as-is for enroll voice/enroll face). The unlock pair does what
   the existing pair does (capture + camera start/pump/stop, in the same
   order, releasing on every exit path — inherited for free from the
   existing `_pump_loop` auto-stop-then-release path, since the new pair
   only changes which cap value is armed and arms/disarms
   `_retain_landmarks`) plus: temporarily sets
   `self.capture.max_seconds = LIVENESS_CAPTURE_CEILING_SECONDS` for the
   duration of the capture (restored to `capture.MAX_SECONDS` on stop), so
   the fixed ceiling (Q2) applies **only** to the liveness capture and never
   shortens an enroll take. `LIVENESS_CAPTURE_CEILING_SECONDS` is a new
   constant in `app.py`, **measured, not guessed**: Task 3 dry-runs reading
   the longest phrase in the Task-1-authored pool aloud (or a documented
   words-per-second estimate against its word count) before pinning the
   final value, replacing spec §2 Q2's provisional "~6–8 s" — per
   `project.md`'s dry-run-before-pinning guardrail.
7. **New bridge method `new_challenge()`** returns `{"ok": True, "phrase":
   ...}`, calling `challenge.pick_challenge(previous=self._current_challenge)`
   and storing the result in `self._current_challenge` (Python is
   authoritative for the phrase shown, not JS — consistent with "Python
   owns state; JS renders only"). Called by the UI whenever the Unlock
   panel becomes active and again after each completed attempt, so the
   no-immediate-repeat property (decision 1) holds across real usage, not
   just within one bridge instance's lifetime.
8. **`unlock()`'s new shape** (only method whose body changes; its
   signature and the vault-layer calls inside it are unchanged from F7):
   after the existing `no_vault` check, compute the voice and face
   embeddings exactly as today (`lock_voiceprint`, `faceprint.embed_frame`
   — unchanged, still needed either way once liveness passes), THEN run the
   liveness gate — `challenge.check(capture.pcm_buffer(), self._current_challenge)`
   and `lipsync.is_live(lipsync.score(mouth_series, audio_envelope))`
   (decision 5's construction) — BEFORE any call to `vault_unlock` (Q6). A
   failed liveness check on **either** signal returns `{"ok": False, "error":
   "auth_liveness"}` and makes **zero** calls into `vault_unlock` — the
   assertion spec §5 cmd 3 names explicitly. Only when both liveness checks
   pass does `vault_unlock(passphrase, voiceprint_vector, faceprint_vector,
   path=...)` run, with the existing `auth_outer`/`auth_voice`/`auth_face`
   exception mapping completely unchanged.
9. **No new error codes beyond `auth_liveness`.** Spec §4's "no face/no
   speech detected" and "too-short or silent capture" edge cases are already
   covered by the existing `no_face` (missing/faceless frame) and
   `need_more_audio` (`lock_voiceprint`'s existing floor) paths — a silent
   or wordless capture simply fails `challenge.check` and surfaces as
   `auth_liveness`, not a new code.

### Memory spine
1. **Tasks 1-3 DONE** (2026-07-28; `rejects` 1/1/0) — `challenge.py`,
   `lipsync.py`, and the Booth bridge (`new_challenge()`,
   `start_unlock_capture()`/`stop_unlock_capture()`, the liveness gate in
   `unlock()`) are landed and stable. Task 4 (UI-only) calls these bridge
   methods; it does not revisit their shape or `app.py`'s Python logic.
2. Zero `vault.py` changes this feature (decision, item 3 above; confirmed
   at Task 3) — the `project.md` caller-grep guardrail is
   inherited-and-not-triggered, not inherited-and-applied.
3. `facedetect.py`/`capture.py` stay byte-for-byte unchanged (decision 5,
   confirmed at Task 3) — all new retention state lives in `app.py`,
   additive only.
4. Task 4 wires the Unlock panel's Record/Stop to
   `start_unlock_capture()`/`stop_unlock_capture()` (NOT the plain
   `start_record()`/`stop_record()` pair enroll keeps using), calls
   `new_challenge()` when the panel activates and after each attempt, and
   adds the `auth_liveness` branch + `chip-liveness-failed` per plan.md's
   Task 4 notes — the bridge surface it needs already exists and is
   stable.

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — Vendor Vosk + `challenge.py`: phrase pool, grammar-constrained match
  - state: DONE
  - rejects: 1
  - feedback log:
    - **REJECT 1 (2026-07-28, verifier subagent, base `b3be5c6`..head `5e637e1`).**
      Gate: PASS (all three commands exit 0, scope check clean). Review:
      Spec axis APPROVE, Standards axis REJECT. Finding: `ChallengeError` at
      `src/voicelock/challenge.py:72-73` is dead code — zero raises, zero
      catches, zero test references anywhere in the repo; neither `plan.md`'s
      Task 1 decisions nor spec §5 cmd 1 call for a custom exception type
      (`check()`/`matches()` both return plain `bool`, never raise). Violates
      `project.md`'s earned no-unexercised-surface guardrail (three prior F4
      REJECTs on this identical pattern) and `topics/code-quality.md`'s
      no-speculative-anything floor. Feedback: delete the unused class;
      introduce it only in the task that actually needs it, with a caller and
      a test.
  - files: `pyproject.toml`, `src/voicelock/models/vosk/` (new, vendored
    `vosk-model-small-en-us-0.15` + `LICENSE` + `NOTICE`),
    `src/voicelock/challenge.py` (new), `tests/test_challenge.py` (new)
  - notes: Apply decisions 1–3 verbatim. Author `CHALLENGE_PHRASES` as
    ~10–20 short, phonetically varied sentences (own words — this is a
    hand-authored constant per Q3, not sourced from copyrighted text, same
    spirit as F4/F7's own hand-picked literal constants). Download and
    vendor `vosk-model-small-en-us-0.15` from `alphacephei.com/vosk/models`
    (Apache-2.0, ~40 MB) offline beside the other three `models/<name>/`
    dirs; write `LICENSE` (reuse the pristine Apache-2.0 text already in
    this repo) and `NOTICE` naming the exact model file/version and its
    distribution-page source, per the per-asset-licence guardrail. Add
    `vosk` to `pyproject.toml` `dependencies` (per the TECH-PICK — no
    version pin stricter than what `memory/decisions.md` already recorded
    as live). Call `vosk.SetLogLevel(-1)` before/at first model load to
    silence Kaldi's default stderr chatter. `matches()` normalizes by
    lowercasing and stripping punctuation only (no stemming/fuzzy edit
    distance — Q3/Q4 both describe exact-pool matching, and spec §5's own
    synthetic table only requires case/punctuation tolerance).
  - build notes (2026-07-28): downloaded `vosk-model-small-en-us-0.15.zip`
    directly from `alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip`
    (41,205,931 bytes, sha256 `30f26242c4eb449f948e42cb302dd7a686cb29a
    3423a8367f99ff41780942498`), matching the `Content-Length` the
    distribution page served — verified before vendoring. The archive's own
    bundled `README` carries no licence text (only "Copyright 2020 Alpha
    Cephei Inc"), so per the metadata-first clause of the per-asset-licence
    guardrail, the distribution page's own table was read next: the row for
    `vosk-model-small-en-us-0.15` states `License: Apache 2.0`, naming this
    exact asset. `uv sync` resolved `vosk==0.3.45` (matching the TECH-PICK)
    with zero changes to any other pinned package (numpy/torch/mediapipe
    etc. all unmoved — `uv.lock` diff is additions only). Vosk's real API
    was confirmed by reading its installed source (no published
    type-stub/docs beyond the GitHub issue already cited at spec time):
    `vosk.KaldiRecognizer(model, sample_rate, grammar_json_str)` for the
    grammar-constrained constructor, `AcceptWaveform`/`FinalResult` return a
    JSON `{"text": ...}` string. `check()`'s reject-path test was dry-run
    against `speakerA_take1.wav` before being pinned (recognized text was
    `"the [unk]"` against the full 12-phrase grammar — genuinely does not
    match any challenge phrase), per the dry-run-before-pinning guardrail.
  - done-criteria:
    - §5 cmd 1 — verbatim, exit 0:
      ```
      uv run pytest tests/test_challenge.py -q
      ```
      Must cover (per spec §5 item 1, decision 3): the phrase pool is a
      fixed, non-empty constant, and `pick_challenge` never repeats the
      immediately-previous phrase across enough consecutive draws to make a
      false failure statistically negligible; a real (unmocked) Vosk
      grammar-constrained recognition run against
      `tests/fixtures/voiceprint/speakerA_take1.wav` (or another existing
      voice fixture) constrained to a specific challenge phrase's grammar
      asserts **reject**, with the test's docstring stating explicitly that
      this fixture cannot prove an accept (Q5's disclosed limitation); the
      `matches()` function unit-tested against a synthetic table covering
      an exact match, a case/punctuation-only difference (must still
      accept), and a genuinely different phrase (must reject) — no model
      load required for this part.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count rises from F7's 186)

- [x] **Task 2** — `lipsync.py`: lag-windowed cross-correlation scorer
  - state: DONE
  - rejects: 1
  - feedback log:
    - **REJECT 1 (2026-07-28, verifier subagent, base `bc91244`..head
      `6959dee`).** Gate: PASS (all three commands exit 0, scope check
      clean). Review: Spec axis APPROVE, Standards axis REJECT. Finding:
      `project.md`'s mutation-sensitivity guardrail is violated — no test
      exercises the lag-search loop itself (`lipsync.py:110`,
      `for lag in range(-lag_window, lag_window + 1)`), the module's whole
      reason for being lag-windowed rather than fixed-lag (spec Q4). Every
      existing test uses shift=0 or shift=15 (already scores below
      threshold at lag 0 too), so collapsing the loop to lag-0-only leaves
      all 8 tests passing — verified empirically by the verifier (shift 3/4/5
      at lag-0-only score 0.221/-0.058/-0.228, all below `SYNC_THRESHOLD`,
      while the real windowed `score()` correctly returns 1.0 via the
      search). Feedback: add a test with a small shift (2-5 frames, inside
      `LAG_WINDOW`) asserting `is_live() is True`, and confirm by mutating
      (collapse the loop to lag=0, watch the new test fail, revert).
  - files: `src/voicelock/lipsync.py` (new), `tests/test_lipsync.py` (new)
  - notes: Apply decision 4 verbatim. `mouth_aperture()` reads two inner-lip
    landmark indices from `facedetect.LIP_POINTS`'s index space (confirm
    the exact upper/lower inner-lip indices against MediaPipe's published
    topology before hard-coding them — same care F7 took confirming
    `faceprint.py`'s embedding width before importing it) and normalizes by
    a stable reference distance from the same frame's landmarks. Pin
    `SYNC_THRESHOLD` and the lag-window width from THIS task's own
    synthetic separation (mirrors how `facelock.py` measured
    `CORRECTION_RADIUS` from real fixture residuals) — pick the threshold
    as the midpoint between the in-phase synthetic score and the
    shifted/flat synthetic score's ceiling, and say so in the module
    docstring, plus the explicit disclosure that neither constant is
    measured against real human lip-sync data (spec §5 item 2's own
    requirement).
  - build notes (2026-07-28): confirmed 13/14 as the inner-lip vertical-
    centre indices directly from the vendored bundle's own topology (the
    `FACE_LANDMARKS_LIPS` connection edges reconstruct into an inner ring
    78-95-88-178-87-14-317-402-318-324-308-415-310-311-312-13-82-81-80-191-78,
    with 13/14 sitting symmetric between the two inner corners 78/308 —
    not assumed from index naming). Face-scale reference reuses
    `faceprint.py`'s own eye-corner indices (33/133, 263/362) for
    consistency. `SYNC_THRESHOLD`/`LAG_WINDOW` dry-run measured (per the
    dry-run-before-pinning guardrail) on `speakerA_live.wav` (58 envelope
    frames at `facedetect.FRAME_INTERVAL`'s hop): in-phase (affine
    transform of the real envelope) scores 1.0; the same series shifted
    15 frames (3x past a 5-frame lag window, non-circular shift) scores
    -0.007; a flat series scores 0.0 by construction. `LAG_WINDOW = 5`,
    `SYNC_THRESHOLD = 0.5` (midpoint of 1.0 and the ~0.0 negative-class
    ceiling), both disclosed in the module docstring per spec §5 item 2.
  - done-criteria:
    - §5 cmd 2 — verbatim, exit 0:
      ```
      uv run pytest tests/test_lipsync.py -q
      ```
      Must cover (per spec §5 item 2): a real audio envelope from an
      existing voice fixture paired with a synthetic in-phase
      mouth-aperture series (a monotonic function of that same envelope)
      scores **above** `SYNC_THRESHOLD`; the same series shifted outside
      the lag window, and a flat (non-moving) series, both score **below**
      `SYNC_THRESHOLD` (the flat case is the direct analog of a still photo
      or a muted video in production); `SYNC_THRESHOLD` and the lag-window
      width are named constants, and the module docstring discloses the
      synthetic-only provenance.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count rises further from Task 1's end)

- [x] **Task 3** — Booth bridge: AV-capture retention, liveness gate before `vault.unlock`, `auth_liveness` reject
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Apply decisions 5–9 verbatim. Before pinning
    `LIVENESS_CAPTURE_CEILING_SECONDS`, dry-run: read Task 1's longest
    authored phrase aloud (or estimate from its word count at a
    conservative words-per-second rate) and pick a ceiling with real
    margin — record the measurement (or the estimate and its basis) in this
    task's notes when done, replacing spec §2 Q2's provisional "~6–8 s".
    `start_unlock_capture()`/`stop_unlock_capture()` mirror
    `start_record()`/`stop_record()`'s existing camera-then-pump /
    pump-then-camera ordering and mic-failure-must-not-cost-the-take
    behavior exactly, adding only: arm/disarm `_retain_landmarks` + clear
    `_liveness_mouth_series`, and temporarily override/restore
    `capture.max_seconds`. `new_challenge()` per decision 7. `unlock()`'s
    body reshaped per decision 8 — the embeddings are computed once and
    reused for both the liveness gate (which never sees the vault) and the
    eventual `vault_unlock` call, so nothing is embedded twice.
  - build notes (2026-07-28): `LIVENESS_CAPTURE_CEILING_SECONDS = 10.0` —
    no live speaker available in this environment, so estimated (not
    guessed) from Task 1's phrase-pool word count rather than a stopwatch
    reading, disclosed as such in `app.py`'s own comment: longest entries
    are 6 words; at a slow, deliberate 1.5 words/sec that is ~4.0 s of pure
    speech, doubled to ~8.0 s for hesitation/lead-in margin, rounded up to
    a comfortable 10.0 s. Replaces spec §2 Q2's provisional "~6–8 s".
    **Real bug found and fixed by this task's own mutation-checked Gate
    test** (`test_the_liveness_ceiling_auto_stop_releases_the_camera_too`):
    the fixed-ceiling auto-stop path lives in `_pump_loop()` (it is what
    *notices* a take self-ended via `capture.pump()`'s own internal
    `stop()`), which calls `_stop_camera()` directly and bypasses
    `stop_unlock_capture()` entirely — so the first implementation left
    `_retain_landmarks` armed and `capture.max_seconds` at the liveness
    ceiling forever after an auto-stopped take, silently capping the
    user's NEXT enroll take too. Fixed by repeating the same two-line
    reset inside `_pump_loop()`'s auto-stop branch (harmless no-op for a
    plain `start_record()` take, since both fields are already at rest
    there). Caught by writing the test FIRST from spec's own "every
    exit path must release" language, not by the verifier — the
    `project.md` acquisition/release guardrail doing its job pre-emptively.
    Proactively mutation-checked the liveness gate itself before
    submitting (collapsed `unlock()`'s `if not self._liveness_passes():`
    to `if False:` — exactly the 5 liveness-specific tests failed, one
    unrelated pre-existing timing flake in an F5 test reproduced as a
    false positive and confirmed independent by re-running it alone;
    reverted, `diff` against a pre-mutation backup showed zero
    differences) — applying Task 2's own lesson (run the mutation check
    before review, not only after a REJECT).
  - done-criteria:
    - §5 cmd 3 — verbatim, exit 0:
      ```
      uv run pytest tests/test_booth_api.py -q
      ```
      Must cover (per spec §5 item 3): the new AV-capture flow (start/stop,
      retention, release-on-every-exit-path including the fixed-ceiling
      auto-stop) via the existing fake `FaceEngine`/fake capture stream
      patterns (no real camera or mic); the liveness gate running before
      `vault.unlock` is ever called — assert a failed-liveness attempt
      makes **zero** calls into the vault layer (e.g. inject a spy/fake
      `vault_unlock` and assert it was never invoked on a liveness-fail
      case); the fifth reject reason (`auth_liveness`) alongside the
      existing `auth_outer`/`auth_voice`/`auth_face`, none leaking the
      display name.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count rises further from Task 2's end)

- [ ] **Task 4** — Booth UI: challenge display + AV capture UX + fifth reject chip *(LAST task — full spec Verification)*
  - state: DOING
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Challenge phrase shown on the Unlock panel BEFORE Record is
    pressed and stays visible through the capture (Q2/Q3) — call
    `new_challenge()` when the Unlock panel becomes active and again after
    each completed attempt (decision 7). Wire the Unlock panel's Record/Stop
    to the new `start_unlock_capture()`/`stop_unlock_capture()` bridge pair
    (decision 6) instead of the plain `start_record()`/`stop_record()` the
    enroll panels keep using — same visual button, same Record/Stop
    interaction (Q2 — "no new interaction pattern"), different bridge call
    underneath, gated on which panel is active (mirrors the existing
    per-panel branching already in `btnRecord`'s handler). Add
    `<span class="chip mono hidden" id="chip-liveness-failed">Didn't look or
    sound live</span>` to `#result-chips`; a `showLivenessFailed()` function
    mirroring `showWrongFace()` exactly (status text
    `"REJECT · LIVENESS CHECK FAILED"`, sub-text naming that passphrase,
    voice, and face all already passed — per spec §1); `hideResultChips()`'s
    chip list gains this chip; `btnUnlock`'s handler gains an
    `auth_liveness` branch calling it, alongside the existing
    `auth_outer`/`auth_voice`/`auth_face` branches. Per the earned Booth-
    layout guardrail (`project.md`): the challenge-phrase display is new
    visible content in the `main`/`.booth` column (the guardrail's specific
    clipping hazard) — smoke-test it manually (open the Unlock panel, watch
    the phrase render without clipping) before calling this task done, same
    caution F6/F7 already had to apply there.
  - done-criteria: **the FULL list from `spec.md`'s Verification section**, namely —
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, ≥186 passing, count risen by Tasks 1–3's new tests — Task 4 is UI-only, no new Python tests)
    - §5 cmd 1 — `uv run pytest tests/test_challenge.py -q` → exit 0 (part of the full-suite run)
    - §5 cmd 2 — `uv run pytest tests/test_lipsync.py -q` → exit 0 (part of the full-suite run)
    - §5 cmd 3 — `uv run pytest tests/test_booth_api.py -q` → exit 0 (part of the full-suite run)
    - §5 cmd 4 — **manual check, required.** Human runs `uv run voicelock`:
      enroll (name + passphrase + voice + face) → unlock with all four
      correct (passphrase, voice, face, live spoken challenge) →
      **unlocked** (name shown); **wrong passphrase** → outer REJECT; right
      passphrase + **wrong voice** → middle REJECT; right passphrase +
      right voice + **wrong face** → inner REJECT; right passphrase + right
      voice + right face but **liveness fails** — tried at least two ways
      per §1 (e.g. speaking the wrong words, and one of: holding up a
      photo, playing a silent/muted video, or replaying a separate
      audio-only recording) → **liveness REJECT**. Each reject names its
      distinct cause. Attested by the human at the feature-end checkpoint.
      **PENDING — this is what remains after Task 4.**

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in spec §1 gets recorded in `.out-of-scope/` and is never built.

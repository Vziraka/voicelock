# Plan — F9 — Demo reliability

## Active context
- Updated: 2026-07-29
- Feature: Feature 9 from `roadmap.md` · Mode: **Mode 3 — Spec-to-done** ·
  Phase: **PLANNED.** Ledger written, all tasks TODO. Next: `/implement`
  Task 1 (the Mode-3 standing go covers it — no further human "go" needed
  inside the feature).
- Spec: `spec.md` holds F9's spec, Grilling `Status: CLEAR` (zero
  `[NEEDS-CLARIFICATION:` hits — re-verified mechanically at plan time,
  after this session executed the spec session's missed §6 write; see
  `memory/deviations.md` 2026-07-29 F9 pre-plan entry), both approval boxes
  checked (box 2 typed by the human), `Mode: Mode 3` set 2026-07-29.

### Why this feature exists, in one line
F8 completed the five-outcome demo arc; F9 makes it reliable and presentable —
refuse bad enrollments with a named reason, let the runner see and dial
strictness, name every failure cause (including the mislabeled camera error),
warn live when the camera can't see you, and manage the profile after unlock.

### The dependency shape that fixes the task order
The mouth-occlusion research (Task 1) runs FIRST because its go/no-go verdict
decides whether Task 5 builds the mouth tier — and nothing else ever blocks
on it (spec pillar 4). The Q4 test fold-in (Task 2) is independent and lands
early. Then two engine foundations: settings + runtime tolerances (Task 3)
before the knob bridge (Task 6); the quality-gate engine (Task 4) before both
the enroll refusal and the management re-enrolls (Task 8). Vault re-seal
surface (Task 7) before the management bridge (Task 8). UI lands last, split
in two: diagnostics/knobs/warnings (Task 9), then management + the feature's
full Verification as the LAST task (Task 10).

### Caller grep — executed at plan time (the `project.md` guardrail)
Every shared surface F9 touches was grepped for in-repo callers BEFORE the
`files:` lines below were assigned. Results, so no task's scope and its
"green full suite" criterion can be mutually unsatisfiable:

- `vault.enroll` / `vault.unlock` callers: `src/voicelock/app.py`,
  `tests/test_middlelock.py`, `tests/test_vault.py`, `tests/test_outer_lock.py`.
- `middlelock.reconcile` / `facelock.reconcile` callers: `src/voicelock/vault.py`,
  `tests/test_middlelock.py`, `tests/test_facelock.py`.
- `lipsync.is_live` callers: `src/voicelock/app.py`, `tests/test_lipsync.py`.

**Resolution: every F9 signature change is additive-optional** (keyword args
defaulting to `None` → module constant; brand-new vault functions), so NO
existing caller breaks and no task is forced to edit files outside its
`files:` line. Any build-time discovery that a change cannot stay
additive-optional is a plan contradiction → STOP per the universal [Modes]
rule (the F4-T3/F7-T2 precedent), not a silent widening.

### Named architecture decisions carried into this ledger
Fill the "exact call shape" gaps the spec left to `/plan` — do not re-derive
mid-build.

1. **`settings.py` is a new engine module** owning
   `~/.voicelock/settings.json`: `load()` → dict of the three knob values
   (`voice_radius`, `face_radius`, `sync_threshold`), `save()`, `reset()`,
   `defaults()` — defaults READ FROM the owning modules
   (`middlelock.CORRECTION_RADIUS`, `facelock.CORRECTION_RADIUS`,
   `lipsync.SYNC_THRESHOLD`), never duplicated as literals (spec §3: no
   default re-pins). A missing/corrupt/out-of-range file loads as defaults
   plus a `"degraded": <reason>` flag the bridge surfaces visibly — never a
   crash. Validation bounds: radii in `(0, RELIABLE_BITS)` exclusive,
   threshold in `(0.0, 1.0)` exclusive.
2. **Runtime tolerances are additive-optional parameters, decode-time only:**
   `middlelock.reconcile(helper, embedding, radius=None)` and
   `facelock.reconcile(helper, embedding, radius=None)` (None → the module
   constant — verified feasible in code at spec time: both bound acceptance
   by `residual > CORRECTION_RADIUS` at decode, `middlelock.py:161` /
   `facelock.py:166`, so radius never touches enrolled helper data);
   `lipsync.is_live(score, threshold=None)`;
   `vault.unlock(..., voice_radius=None, face_radius=None)` threading them
   into the two `reconcile` calls. `commit()` is untouched everywhere.
3. **`enrollquality.py` is a new engine module** (Python owns thresholds —
   not bridge code): `check_voice(voiceprints) -> QualityVerdict` and
   `check_face(faceprints) -> QualityVerdict`, where `QualityVerdict` names
   ok/refused, the factor, a machine reason code, the worst take index, and
   actionable Booth copy. Signals reuse what enrollment already computes:
   voice — leave-one-out `middlelock.residual_bits` spread across the 5
   takes vs `CORRECTION_RADIUS` headroom; face — the same construction via
   `facelock.residual_bits` (and/or pairwise SFace distance) across the 3
   banked embeddings vs its budget. **Refuse thresholds are MEASURED at
   Task 4 build time** against the real fixtures (`speakerA_enroll1..5.wav`
   embeddings; `personA_1/personA_2/personB.jpg`), dry-run before pinning,
   provenance disclosed beside the pinned values — never guessed.
4. **`enroll()` refusal shape:** quality checks run AFTER the existing
   count/validation guards and BEFORE `vault_enroll`; refusal returns
   `{"ok": False, "error": "quality_voice"|"quality_face", "message": ...,
   "worst_take": ...}` and makes ZERO calls into `vault_enroll` (the F8
   liveness-gate assertion pattern, spec Verification item 1). Banked takes
   are NOT cleared on refusal — only the weak material needs redoing, and
   the copy says which.
5. **Camera error surface (fix site `app.py:720`):** new
   `_push_camera_error(message)` → JS `showCameraError`; `_start_camera`'s
   failure branch calls it instead of `_push_mic_error`. Python tracks
   `_camera_error_active`; the next delivered frame in `_push_face_frame`
   pushes `hideCameraError` once and clears the flag. The mic banner
   auto-clears symmetrically: a successful `capture.start()` in
   `start_record()`/`start_unlock_capture()` pushes `hideMicError`. No
   manual dismiss (spec Q3 — banners reflect live device state). Bridge
   pushes land before the JS functions exist (Task 5 before Task 9); that
   is safe by construction — every `_eval` script guards with
   `window.voicelockBooth && window.voicelockBooth.<fn> &&`.
6. **Live face-visibility warning lives in `_push_face_frame`:** when
   `_retain_landmarks` is armed, a frame with empty `result.landmarks`
   increments a consecutive-faceless counter; at ≥ N consecutive it pushes
   `showCaptureWarning` once; a face-bearing frame resets the counter and
   pushes `hideCaptureWarning`. N is dry-run measured at Task 5 (start from
   ~1 s of nominal delivery, but measure against the fake-engine cadence
   and say so). The warning NEVER touches the take's stop/release path.
   Mouth tier: built in Task 5 ONLY if Task 1's verdict is GO, same shape
   against the found signal; on NO-GO it is skipped and re-parks at wrap-up
   WITH the evidence file (spec §3 forbids a guess-based heuristic).
7. **Knob bridge:** `get_knobs()` (values + defaults + degraded note),
   `set_knob(payload)` (validated via `settings.py`, out-of-range refused
   visibly), `reset_knobs()`. The unlock path consumes knobs at its two
   decision points: `vault_unlock(..., voice_radius=..., face_radius=...)`
   and `_liveness_passes()` → `lipsync.is_live(score, threshold=...)`.
   Python reads the settings file; JS renders values only.
8. **Vault management functions re-verify, never bypass** (new surface in
   `vault.py`, names final at build): `change_passphrase(old_passphrase,
   new_passphrase, path)` — peels the OUTER layer only, re-seals with a
   fresh salt around the byte-identical `{helper_data_voice,
   middle_ciphertext}`; `reseal_voice(passphrase, current_voiceprint,
   new_voiceprints, path)` — peels outer+middle, new `middlelock.commit`,
   re-seals middle around the byte-identical `{helper_data_face,
   inner_ciphertext}` and outer above it; `reseal_face(passphrase,
   current_voiceprint, current_faceprint, new_faceprints, path)` — full
   peel to the profile JSON, new `facelock.commit`, re-seals all three.
   Each op takes the same credentials `unlock` takes and re-peels
   internally — self-contained, independently testable, and structurally
   incapable of the "reset a factor without unlocking" bypass spec §3
   forbids. All management writes go through a new
   `_write_vault_atomic(path, blob)` (write `<name>.tmp` in the same dir,
   then `os.replace`); `enroll()`'s own write path is deliberately
   untouched (spec scopes atomicity to management ops).
9. **The bridge holds the unlocked session's credentials, not the human:**
   on a successful `unlock()`, `BoothApi` retains
   `{passphrase, voiceprint_vector, faceprint_vector, name}` in a private
   `_unlocked_session` (this is the "key material the unlocked session
   already holds" — spec pillar 5); a new bridge `lock()` clears it (and
   F8's UI-only Lock button now also calls it). Management methods
   (`change_passphrase`, `reenroll_voice`, `reenroll_face`) are refused
   with `{"ok": False, "error": "locked"}` when no session is held.
   Re-enrolls reuse the EXISTING take-banking flows
   (`enroll_take`/`enroll_face_take` + resets) and run the SAME
   `enrollquality` gate as first enrollment (one bar, enforced
   everywhere); a refused re-enroll leaves the on-disk vault
   byte-identical. A completed management op clears the session — the
   Booth returns to the locked state (spec pillar 5).
10. **UI lands in two tasks, engine-first order preserved:** Task 9 renders
   surfaces Tasks 4–6 already push/serve (refusal copy, camera banner +
   chip + statuses, live warning, knobs panel with defaults + one reset +
   honesty copy); Task 10 adds the unlocked-state management controls and
   carries the feature's FULL Verification list as the last task. Every
   new visible Booth element gets the manual layout smoke test
   (`project.md` earned guardrail — headless-Chromium screenshots at the
   app's real 1100×740, the F8 Task 4 method).

### Memory spine
1. Five pillars (quality gate · knobs · camera-error fix · visibility
   warning · profile management) + the Q4 fixture-test fold-in; the
   mouth-tier research task runs first and nothing blocks on it.
2. Caller grep done at plan time (section above): all F9 shared-surface
   changes are additive-optional, so no F4-T3/F7-T2-shaped contradiction is
   planted in this ledger.
3. Knobs are decode-time only and persisted in `~/.voicelock/settings.json`
   (a demo aid, not a secret); pinned defaults never change (spec §3).
4. Management = per-layer re-seal composing existing constructions
   (vault stays v3, no new crypto), atomic write-new-then-swap, same
   quality gate as first enrollment, credentials retained by the bridge
   only while unlocked.
5. The camera mislabel's fix site is `app.py:720`; the face-visibility
   warning is real data today via `_push_face_frame`'s empty-landmarks
   frames — no engine (`facedetect.py`/`capture.py`) changes anywhere in
   this feature.

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [ ] **Task 1** — Research: a usable "mouth not visible" signal (go/no-go)
  - state: TODO
  - rejects: 0
  - files: `.harness/memory/research/2026-07-29-mouth-occlusion-signal.md` (new)
  - notes: Run the `research` skill, bounded to spec pillar 4's mouth tier.
    Question: does the vendored MediaPipe Face Landmarker path expose any
    usable per-landmark confidence/visibility/presence signal — or is there
    a sound geometric cue — that distinguishes "mouth occluded" from "mouth
    simply not moving" on real frames? Primary sources: the installed
    `mediapipe` package's own API surface (read the source — the F8 Vosk
    precedent), the model card / official docs for the vendored bundle, and
    an empirical dry-run against this repo's committed face fixtures
    (occlusion simulated by masking the mouth region of `personA_1.jpg`
    programmatically — no new fixtures). Findings file must carry a
    top-level `Verdict: GO` or `Verdict: NO-GO` line, the evidence for it,
    and ≥2 cited primary sources with dates. NO-GO is a complete, valid
    outcome (spec §3): the mouth tier then re-parks at wrap-up with this
    file attached. No production code in this task.
  - done-criteria:
    - Findings file exists with a mechanical verdict + citations — exit 0
      (dry-run verified at plan time, positive and negative cases):
      ```
      uv run python -c "import pathlib, re, sys; t = pathlib.Path('.harness/memory/research/2026-07-29-mouth-occlusion-signal.md').read_text(encoding='utf-8'); m = re.search(r'^Verdict:\s+(GO|NO-GO)\b', t, re.M); sys.exit(0 if (m and len(re.findall(r'https?://', t)) >= 2) else 1)"
      ```
    - `uv run ruff check .` → exit 0 (no code changes)
    - `uv run pytest` → exit 0 (count unchanged from F8's 229 — this task
      adds no tests)

- [ ] **Task 2** — Q4 fold-in: byte-disjoint same-speaker test + subarray guard + cutoff caveat
  - state: TODO
  - rejects: 0
  - files: `tests/test_voiceprint.py`, `src/voicelock/voiceprint.py`
    (comment beside `ACCEPT_CUTOFF` only — no behavior change)
  - notes: Rewrite the same-speaker assertion so it can actually fail:
    reference from `speakerA_enroll1..3.wav`, probe `speakerA_enroll5.wav`
    (the byte-disjoint pair the fixtures README guarantees — verify that
    guarantee mechanically in the new subarray test, don't trust prose),
    assert accept band. Keep `test_compare_pipeline_runs_end_to_end`'s
    honest docstring lineage — the new test replaces its vacuous accept
    claim, not its pipeline coverage. Add the Gate check: for every pair of
    distinct `tests/fixtures/voiceprint/*.wav` files, the probe's raw
    sample bytes are NOT a contiguous subarray of the reference's (a
    straightforward bytes-`in`-bytes check over the decoded PCM). Disclose
    the calibration caveat in a comment beside `ACCEPT_CUTOFF = 0.45`
    (`voiceprint.py:35`): measured against a same-recording probe, not
    cross-validated (spec §3 — disclosed, not re-tuned). The caveat's
    presence is asserted by a test using a REGEX on the source text (the
    earned source-text-meaning rule — never `str.count` on one spelling).
    No new fixtures, no constant changes.
  - done-criteria:
    - `uv run pytest tests/test_voiceprint.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises from 229 — new subarray +
      caveat tests; nothing falls)

- [ ] **Task 3** — `settings.py` + runtime tolerances threaded through the engine
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/settings.py` (new), `src/voicelock/middlelock.py`,
    `src/voicelock/facelock.py`, `src/voicelock/lipsync.py`,
    `src/voicelock/vault.py`, `tests/test_settings.py` (new),
    `tests/test_vault.py`, `tests/test_lipsync.py`
  - notes: Apply decisions 1–2 verbatim. All parameter additions are
    additive-optional (caller grep, section above) — every existing test
    stays green untouched. New coverage: settings round-trip; missing /
    corrupt / out-of-range file → defaults + degraded flag, never a crash;
    engine-level proof that a dialed radius flips an outcome — construct a
    synthetic embedding pair whose residual lands between the default
    radius and a dialed one (`commit`/`reconcile` are pure numpy — no
    model load, seeded rng), assert default rejects and dialed accepts, for
    BOTH locks; `is_live` with an explicit threshold likewise; `vault.unlock`
    passes the kwargs through (spy on `reconcile` or use the synthetic
    construction end-to-end). Per the mutation-sensitivity rule: verify the
    new tests fail when the kwarg-threading is neutered (e.g. `radius`
    ignored) before claiming coverage.
  - done-criteria:
    - `uv run pytest tests/test_settings.py tests/test_vault.py tests/test_middlelock.py tests/test_facelock.py tests/test_lipsync.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 4** — Enrollment-quality gate: `enrollquality.py` + enroll refusal
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/enrollquality.py` (new), `src/voicelock/app.py`,
    `tests/test_enroll_quality.py` (new), `tests/test_booth_api.py`
  - notes: Apply decisions 3–4 verbatim. Measure the refuse thresholds
    against the real fixtures BEFORE pinning (dry-run-before-pinning
    guardrail): embed `speakerA_enroll1..5.wav` via `lock_voiceprint` and
    record the leave-one-out residual spread a CONSISTENT enrollment
    produces; construct the inconsistent case from the fixtures themselves
    (e.g. swapping `speakerB.wav` in for one take, or synthetic
    perturbation — say which); face likewise via `personA_1/personA_2` vs
    `personB`. Pin thresholds with disclosed provenance beside them.
    Refusal copy is actionable and per-factor (spec pillar 1: "voice takes
    too inconsistent — re-record take N in a quieter room" shape).
    Existing floors (`need_more_audio`, `no_face`) stay untouched.
    `tests/test_enroll_quality.py`: inconsistent enrollment refused with
    the per-factor reason code; consistent accepted; refusal makes ZERO
    calls into `vault_enroll` (spy — the F8 pattern at
    `test_booth_api.py:990`); banked takes survive refusal.
  - done-criteria:
    - `uv run pytest tests/test_enroll_quality.py -q` → exit 0
    - `uv run pytest tests/test_booth_api.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 5** — Camera-error surface + auto-clear + live visibility warning (bridge)
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Apply decisions 5–6 verbatim. Read Task 1's verdict first: GO →
    build the mouth tier in the same counter shape against the found
    signal; NO-GO → face tier only, and note the re-park for wrap-up.
    Dry-run the faceless-frame threshold N against the fake engine's
    cadence before pinning it, and disclose the basis. Tests (existing fake
    `FaceEngine` / fake-capture patterns, no real devices): camera failure
    pushes its OWN error code — asserted DISTINCT from the mic error's
    push; a delivered frame auto-clears it exactly once; successful capture
    start pushes the mic-banner clear; N consecutive faceless frames while
    capturing push the warning, face-bearing frames do not and reset;
    warning fires at most once per dropout episode; the take's
    stop/release path is byte-for-byte the F8 behavior (release on every
    exit path — the earned guardrail's standing test shape). Per the
    mutation-sensitivity rule, neuter the counter and watch the new tests
    fail before claiming coverage.
  - done-criteria:
    - `uv run pytest tests/test_booth_api.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 6** — Knob bridge surface + unlock-path consumption
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Apply decision 7 verbatim (depends on Task 3's `settings.py` and
    threaded parameters). Tests: `get_knobs` returns values + defaults +
    degraded note (corrupt/missing file cases); `set_knob` persists and
    out-of-range is refused visibly, never a crash; `reset_knobs` restores
    defaults; the unlock path consumes the stored values — assert
    `vault_unlock` receives the dialed radii (spy on kwargs) AND a dialed
    `sync_threshold` provably flips an unlock outcome the pinned default
    rejects (a sync score constructed between default and dialed threshold
    — deterministic, the fake/spy patterns the suite already uses; spec
    Verification item 2's flip requirement).
  - done-criteria:
    - `uv run pytest tests/test_booth_api.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 7** — Vault per-layer re-seal + atomic swap (engine)
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/vault.py`, `tests/test_vault.py`
  - notes: Apply decision 8 verbatim. All-new surface — `unlock`/`enroll`
    signatures untouched beyond Task 3's optional kwargs (caller grep
    holds). Byte-identity is the load-bearing property and is asserted
    DIRECTLY, not inferred: after `change_passphrase`, decrypt the new
    outer with the new passphrase and assert `middle_ciphertext` bytes are
    identical to before (and old passphrase raises `AuthError`, new one
    unlocks); after `reseal_voice`, assert `helper_data_face` +
    `inner_ciphertext` bytes identical and the vault unlocks with the NEW
    voice material (and not the old); after `reseal_face`, the name
    survives and the vault unlocks with the new face material. Atomic swap:
    simulate a failure mid-write (monkeypatch `os.replace` or the tmp-file
    write to raise) and assert the on-disk vault is byte-identical to
    before and still unlocks. Wrong-credential management attempts raise
    the same named errors `unlock` raises (no bypass). Pure-numpy synthetic
    embeddings via `commit` keep these tests model-free like
    `test_vault.py`'s existing style.
  - done-criteria:
    - `uv run pytest tests/test_vault.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 8** — Management bridge: unlocked session, re-enrolls through the quality gate
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Apply decision 9 verbatim (depends on Tasks 4 and 7). Tests:
    every management method refused with `"locked"` before a successful
    unlock and after `lock()`; successful unlock retains the session and
    `lock()` clears it; `change_passphrase` via the bridge → old passphrase
    rejects, new unlocks; `reenroll_voice`/`reenroll_face` consume freshly
    banked takes, run the SAME quality gate (a deliberately inconsistent
    re-enroll is refused with the per-factor code and the on-disk vault
    stays byte-identical — read the file before/after), and a completed op
    clears the session; no management path ever returns vault plaintext
    beyond what `unlock` already returned. Reuse the existing fake
    capture/face patterns; no real devices.
  - done-criteria:
    - `uv run pytest tests/test_booth_api.py tests/test_vault.py -q` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises further; nothing falls)

- [ ] **Task 9** — Booth UI: refusal copy, camera banner/chip, live warning, knobs panel
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Apply decision 10's first half. Add: `showCameraError`/
    `hideCameraError` (distinct "LOCKED · CAMERA ERROR" status + its own
    banner/chip, visibly not the mic's) and `hideMicError`, exported on
    `window.voicelockBooth` so Task 5's pushes connect; enroll refusal copy
    rendering `quality_voice`/`quality_face` messages per-factor and
    showing that banked takes survived; the live capture warning
    (`showCaptureWarning`/`hideCaptureWarning`, "can't see your face" copy,
    shown only while recording; mouth-tier copy only if Task 5 built it);
    the knobs panel — three knobs, each labeled with its pinned default,
    one reset control, honest copy that loosening weakens the demo's
    strictness — wired to `get_knobs`/`set_knob`/`reset_knobs`. JS renders
    Python's values only — no mirrored state (earned UI-state guardrail).
    Layout smoke test EVERY new element (earned guardrail): headless-
    Chromium screenshots at 1100×740 — default state, knobs open, camera-
    error state, warning visible, refusal copy visible, scrolled-to-bottom.
  - done-criteria:
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count unchanged from Task 8's end — UI-only)
    - Layout smoke-test screenshots taken and reviewed for all six listed
      states, no clipping (recorded in build notes with the method, per the
      F8 Task 4 precedent — the Gate cannot see layout; this line is the
      auditable record that the manual step ran)

- [ ] **Task 10** — Booth UI: profile management panel *(LAST task — full spec Verification)*
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Apply decision 10's second half. Unlocked state offers: change
    passphrase (new passphrase entry + confirm), re-enroll voice (reuses
    the 5-take capture UX), re-enroll face (reuses the 3-take burst UX) —
    all calling Task 8's bridge; refusals render the same quality copy as
    Task 9; a completed op or the Lock button returns the Booth to the
    locked state (Lock now also calls the bridge `lock()`). Layout smoke
    test on the management panel states (unlocked view, each flow open,
    refusal shown). Then run the feature's FULL Verification.
  - done-criteria: **the FULL list from `spec.md`'s Verification section**, namely —
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count risen from 229 by Tasks 2–8's
      new tests)
    - Quality gate — `uv run pytest tests/test_enroll_quality.py -q` → exit 0
    - Knobs + error surfaces + visibility warning —
      `uv run pytest tests/test_booth_api.py -q` → exit 0
    - Profile management — `uv run pytest tests/test_vault.py tests/test_booth_api.py -q` → exit 0
    - Fixture-test strengthening — `uv run pytest tests/test_voiceprint.py -q` → exit 0
    - Manual (required, human-attested at the feature-end checkpoint): run
      `uv run voicelock` and walk spec §1's full demo — bad enrollment per
      factor refused with its named reason; good enrollment proceeds; a
      borderline reject flips to accept when its knob is loosened and back
      on reset; the five-outcome F8 arc holds verbatim; camera
      unplugged/blocked shows the camera-named error and clears on
      recovery; covering/turning away mid-capture warns live; unlock →
      change passphrase → old rejects, new unlocks; re-enroll voice and
      face → next unlock works; deliberately bad re-enrollment refused.
      Layout smoke on every new Booth element.

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in spec §1 gets recorded in `.out-of-scope/` and is never built.

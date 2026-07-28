# Handoff

## F8 — Lip-sync liveness (challenge-response) · PLANNED, ready to build

**2026-07-28.** `spec.md` approved (both boxes checked, Mode 3) and
`/plan` broke it into a 4-task ledger in `plan.md`. All tasks `TODO`.

### Task order and why
1. **Task 1** — vendor `vosk-model-small-en-us-0.15` + `challenge.py`
   (phrase pool, grammar-constrained match). New-dependency TECH-PICK
   integration lands first, mirroring F5/F6/F7's own vendor-first pattern.
2. **Task 2** — `lipsync.py` (lag-windowed cross-correlation scorer).
   Independent of Task 1; ordered second only because Task 1 carries the
   dependency work.
3. **Task 3** — Booth bridge (`app.py`): AV-capture retention (all new
   state lives here — `facedetect.py`/`capture.py` stay untouched), the
   liveness gate wired **before** `vault.unlock` is ever called (Q6), new
   `auth_liveness` reject. Depends on both Task 1 and Task 2.
4. **Task 4** (LAST) — Booth UI: challenge display + capture UX + fifth
   reject chip. Full spec Verification is this task's done-criteria,
   including the required manual 5-outcome check.

### Key decisions already made at `/plan` (full detail in `plan.md`'s
"Named architecture decisions" section — do not re-derive):
- **No `vault.py` changes this feature** — liveness gates in front of the
  existing three nested locks entirely from `app.py`; the vault-signature
  caller-grep guardrail doesn't trigger.
- **`facedetect.py`/`capture.py` stay byte-for-byte unchanged** — retention
  (a per-frame mouth-aperture list) lives in new `BoothApi` state, filled
  additively from the existing `_push_face_frame` callback.
- **Audio envelope for lip-sync is recomputed post-capture** from the full
  retained PCM buffer at a fixed hop equal to one video frame interval, so
  it naturally lands on the same per-frame grid as the mouth-aperture
  series — not the live, irregularly-chunked Visualizer levels list.
- **New `start_unlock_capture()`/`stop_unlock_capture()` bridge pair**,
  separate from the existing `start_record()`/`stop_record()` (which enroll
  flows keep using unmodified), so the new fixed AV-capture ceiling never
  shortens an enroll take.
- **`LIVENESS_CAPTURE_CEILING_SECONDS` must be dry-run-measured** at Task 3
  against the real authored phrase pool (Task 1's output) before being
  pinned — replaces spec §2 Q2's provisional "~6–8 s".

### next_action

**Human**: on "go" (Mode 3's standing approval covers task-to-task
progression inside this feature), a fresh `/implement` session starts
Task 1 — vendoring Vosk's small English model and building `challenge.py`.
No further human input needed to start; Mode 3 build↔verify cycles run
unattended until the feature-end checkpoint.

### Session commits

Base → head: `49c3850` (prior HEAD, F8 spec session) → *(this session's
state-file commit, hash recorded once created)*. Files this session:
`spec.md` (box 2 checked — human approval), `plan.md` (new 4-task ledger),
`handoff.md` (this file). Not pushed.

### Open items for whoever picks up Task 1

- Author `CHALLENGE_PHRASES` in own words (own-authored sentences, not
  sourced text) — ~10–20 short, phonetically varied.
- Confirm the exact upper/lower inner-lip landmark indices against
  MediaPipe's published topology before hard-coding them in `lipsync.py`
  (Task 2) — same care F7 took confirming SFace's embedding width before
  importing it.
- `SYNC_THRESHOLD` and the lag-window width (Task 2) and
  `LIVENESS_CAPTURE_CEILING_SECONDS` (Task 3) are all measured-not-guessed
  constants per `project.md`'s dry-run-before-pinning guardrail — each
  task's own notes in `plan.md` say what to measure them against.

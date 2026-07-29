# Spec: F9 — Demo reliability

Feature: Feature 9 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [x] Approved by human

- **Mode: Mode 3 — Spec-to-done.** Set by the human 2026-07-29. Build↔verify
cycles and the feature-end wrap-up run unattended within this feature; the
human is checked in with at the feature-end checkpoint (final-verdict review

- commit/push approval). Same mode as F4 through F8. Mode 4 was mechanically
unlocked (F5.5 completed cleanly at Mode 4) but not chosen — F9's expanded
size argues for a human pause before whatever comes next.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Make the full F1–F8 demo **reliable and presentable**. F8 completed the demo
arc (five visibly distinct outcomes); F9 removes the ways that arc fails or
confuses when a real human runs it: a bad enrollment that produces flaky
unlocks, no way to see or adjust how strict the matching is, and one
mislabeled, stuck error state inherited from F5.

Five pillars. Pillars 1–3 are `roadmap.md`'s F9 entry; pillar 4 pulls in
F8's parked capture-visibility ask (Q5a); pillar 5 absorbs roadmap **F11**
(Q5b) — both human-decided expansions beyond the original roadmap entry:

1. **Enrollment-quality gate (voice AND face).** A low-quality enrollment is
  the main source of "it worked yesterday" flakiness — the fuzzy locks seal
   whatever takes they are given, and inconsistent takes produce a key that
   natural day-to-day variation cannot reliably reproduce. F9 measures
   enrollment quality at enroll time and **refuses a bad enrollment with a
   visible, named reason** (which factor, and what to do about it) instead of
   sealing it. **RESOLVED (2026-07-29, human-approved, Q1): cross-take
   spread vs. the correction budget.** Reuse the signals already computed at
   enroll time — voice: spread across the 5 enroll takes measured against
   `middlelock`'s correction budget (default radius 110); face: pairwise
   SFace distance across the 3 banked frames against `facelock`'s budget
   (default 95). Refuse when the cross-take spread leaves no headroom for
   natural day-to-day variation. Refusal names the factor with actionable
   Booth copy (e.g. "voice takes too inconsistent — re-record take N in a
   quieter room"); already-banked takes stay banked so only the weak
   material needs redoing. Existing floors (`need_more_audio`, `no_face`)
   stay as-is. The exact refuse thresholds are **measured at `/plan`–build
   time** against the real fixtures/signals per `project.md`'s
   dry-run-before-pinning guardrail — never guessed in this spec.
2. **Visible tolerance knobs.** The demo's strictness is currently five
  invisible constants (`middlelock.CORRECTION_RADIUS = 110`,
   `facelock.CORRECTION_RADIUS = 95`, `lipsync.SYNC_THRESHOLD = 0.5`, plus
   the two diagnostic-panel cutoffs). F9 surfaces tolerance as something the
   demo runner can **see and dial**, so a borderline reject can be
   demonstrated and resolved live. **RESOLVED (2026-07-29, human-approved,
   Q2): real-path knobs, persisted.** Three knobs — voice radius (default
   110), face radius (default 95), lip-sync threshold (default 0.5) —
   affecting the **real unlock path**. Feasible without re-enrollment
   (verified in code before asking: both `reconcile()` functions bound
   acceptance by `residual > CORRECTION_RADIUS` at decode time —
   `middlelock.py:161`, `facelock.py:166` — so the radius never touches
   enrolled helper data). Values persist in `~/.voicelock/settings.json`
   (a demo aid, not a secret); each knob shows its pinned default; one
   reset control; honest Booth copy that loosening a knob weakens the
   demo's strictness. Threading a tolerance through `vault.unlock` is a
   shared-signature change — the `project.md` caller-grep guardrail
   applies at `/plan`.
3. **Per-rejection cause clarity — the camera-error fix.** The five unlock
  outcomes already reject distinctly (F7/F8 built the four reject chips);
   the remaining mislabel is inherited from F5 and recorded in `roadmap.md`:
   a **camera** failure is pushed through `_push_mic_error`, so a machine
   with no webcam shows "No camera available" under a **"LOCKED · MIC
   ERROR"** status, and with no `hideMicError` path the banner **persists
   for the whole session** while the mic works fine. F9 gives the camera
   its own named error surface and a way for it to clear.
   **RESOLVED (2026-07-29, human-approved, Q3): auto-clear on recovery.**
   A distinct "CAMERA ERROR" status + chip via a new `_push_camera_error`
   (the message already exists — `facedetect.py` produces
   `_camera_error_message`; only the bridge surface at `app.py:720`
   mislabels it), cleared automatically the next time the camera delivers
   a frame; the mic banner likewise clears on the next successful capture
   start. No manual dismiss button — each banner reflects live device
   state, consistent with "Python owns state, JS renders only."
4. **Live capture-visibility warning.** **RESOLVED (2026-07-29,
  human-decided, Q5a — pulled INTO F9, against the agent's initial
   recommendation, then shaped by two follow-ups):** during the unlock AV
   capture, the Booth warns **live** — while recording, not only after —
   when the camera can't usably see the user. Two tiers, split by
   feasibility:
  - **Face not visible at all** (absent, turned away, fully covered) —
  **firm deliverable**. Buildable with existing signals: the landmarker
  already reports zero faces per frame and the bridge already receives
  every frame's result (`_push_face_frame`), so "no face for the last N
  frames while capturing" is real data today. Visible live Booth copy
  (e.g. "can't see your face"), never a crash, capture still ends
  cleanly per the release guardrail.
  - **Mouth-only occlusion** (face tracks, but the mouth specifically is
  blocked, e.g. by a hand) — **research-first, go/no-go**
  (human-approved shape): F9 opens with a bounded `research`-skill task
  hunting for a usable "mouth not visible" signal (per-landmark
  confidence/score if the vendored library exposes one, geometric
  cues), findings written to a cited file in `memory/research/`. Signal
  found → build the mouth-tier warning; no signal → F9 is complete
  without it, and the item re-parks on the roadmap WITH the evidence
  file (so the next revisit starts from findings, not from zero). The
  rest of F9 never blocks on this task.
5. **Profile management from inside the vault (absorbs roadmap F11).**
  **RESOLVED (2026-07-29, human-decided, Q5b — bundled INTO F9 against
   the agent's recommendation, accepting the larger feature):** after a
   successful unlock — and only then — the Booth offers per-factor
   management: **change passphrase**, **re-enroll voice**, **re-enroll
   face**. Mechanics compose the existing constructions; no new crypto,
   no format change (vault stays v3):
  - *Change passphrase* — re-seal the **outer** layer only with the new
  passphrase-derived key; the middle/inner ciphertexts and both helper
  datas are byte-untouched.
  - *Re-enroll voice* — 5 fresh takes → new `middlelock.commit` → new
  voice key + helper data; re-seal middle (and outer above it). The
  inner face layer is untouched.
  - *Re-enroll face* — 3 fresh takes → new `facelock.commit` → new face
  key + helper data; re-seal inner (and the layers above it).
   Each re-enrollment path runs **the same quality gate as pillar 1** —
   one bar for good enrollment, enforced everywhere. The vault file is
   replaced **atomically** (write-new-then-swap), so a failed or abandoned
   management operation never corrupts the existing vault. These
   operations necessarily use key material the unlocked session already
   holds (unlock derived it); the Booth returns to the locked state after
   a management operation completes or the user locks (F8's Lock button).
   Exact bridge/UI call shapes are `/plan`'s, as with every prior feature.

Housekeeping item, routed here by the 2026-07-26 calibration runs
(`.out-of-scope/2026-07-26-calibration-findings-run2.md`, item 2) —
**RESOLVED (2026-07-29, human-approved, Q4): included in F9.** The existing
same-speaker test passes even with no speaker model at all, because the
probe is a byte-level sub-window of the reference audio. F9 rewrites the
same-speaker assertion to use the byte-disjoint pair the fixture README
already guarantees (`enroll1` vs `enroll5`, zero shared audio) so it can
actually fail, and adds a Gate check that no probe fixture is a subarray of
any reference fixture. Test-only; no constant re-pinning; no new fixtures.
The calibration caveat (voice `ACCEPT_CUTOFF = 0.45` was measured against a
same-recording probe, not cross-validated) is disclosed in a comment beside
the constant as part of this item.

Demo (what the human sees):

- **Bad enrollment refused:** deliberately inconsistent enroll takes (voice
or face) → Enroll refuses with a per-factor named reason; consistent takes
→ enrollment proceeds exactly as today.
- **Dial tolerance:** a borderline unlock rejects; the runner opens the
knobs, loosens the relevant factor, retries, and it accepts — then resets
to defaults and the reject returns. Each knob shows its default.
- **Each reject names its cause:** the existing five-outcome arc still holds
verbatim (wrong passphrase / voice / face / liveness, each distinct), and
additionally a missing/blocked **camera** now shows a camera-named error —
not "MIC ERROR" — which clears when the camera comes back.
- **Live visibility warning:** during an unlock capture, turn away or cover
your face → the Booth warns "can't see your face" **while recording**
(and, if the mouth-tier research lands, covering just the mouth warns
too); the take still ends cleanly and the end-of-take reject is unchanged.
- **Manage the profile:** unlock, then change the passphrase → the old
passphrase now rejects and the new one unlocks; re-enroll voice (or face)
→ the next unlock works with the new material, and a deliberately bad
re-enrollment is refused by the same quality gate as first enrollment.

## 2. Grilling record — ambiguity scan

**Status: CLEAR.** All content questions (Q1–Q5b) resolved interactively
with the human (2026-07-29) — a search for the `NEEDS-CLARIFICATION` token
in its colon form returns zero hits in this file. (The Mode line in §0 and
the §6 blind-spot answer are set at the mode step, per the `spec` skill —
not ambiguity markers.)


| Category                           | Verdict      | State                                                                                                                                                                                             |
| ---------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Functional scope & behavior        | **Resolved** | Five pillars (§1): quality gate (Q1), real-path knobs (Q2), camera-error fix (Q3), two-tier visibility warning (Q5a), profile management absorbing F11 (Q5b). Fixture-test fold-in included (Q4). |
| Domain & data model                | **Resolved** | Q2 — `~/.voicelock/settings.json` for knob values. Q5b — vault stays v3; management is per-layer re-seal, atomic replace.                                                                         |
| Interaction & UX flow              | **Resolved** | Q2 (knobs with defaults + reset + honesty copy), Q3 (auto-clear banners), Q5a (live warning copy), Q5b (management only in unlocked state).                                                       |
| Non-functional (perf, security)    | **Resolved** | Q2's real-path knobs signed off with honesty copy; Q5b's no-bypass rule (§3); offline-only inherited.                                                                                             |
| Integration & dependencies         | **Resolved** | No new dependency anticipated — numpy/UI/vault-composition work on existing modules. Any surprise → TECH-PICK.                                                                                    |
| Edge cases & failure modes         | **Resolved** | Q3 (recovery); §4's edge list (corrupt settings, refused re-enrollment leaves vault intact, atomic swap, release-on-every-exit).                                                                  |
| Completion signals                 | **Resolved** | §5 — automatable per pillar + the required live manual check; the mouth-tier's go/no-go is completion-by-evidence either way.                                                                     |
| Terminology (matches `CONTEXT.md`) | **Clear**    | Uses **Enroll**, **Booth**, **Vault**, **Impostor**, **Liveness** as defined. "Tolerance knob" is plain English, not new jargon.                                                                  |


### The questions (all resolved 2026-07-29, answers written into §1/§3)

**Q1 — quality gate:** cross-take spread vs. the correction budget; refuse
with per-factor actionable copy. *(§1 pillar 1)*
**Q2 — tolerance knobs:** three real-path knobs, persisted, defaults +
reset + honesty copy. *(§1 pillar 2)*
**Q3 — error recovery:** distinct camera surface, auto-clear on device
recovery. *(§1 pillar 3)*
**Q4 — fixture-test fold-in:** yes — byte-disjoint pair + subarray guard +
cutoff caveat disclosure. *(§1 housekeeping item)*
**Q5a — capture visibility:** pulled INTO F9 (human-decided): face tier
firm, mouth tier research-first go/no-go. *(§1 pillar 4)*
**Q5b — F11:** bundled INTO F9 (human-decided): profile management after
unlock. *(§1 pillar 5)*

## 3. Non-goals

- **Occluded-mouth detection is scoped exactly as §1 pillar 4 says — no
further.** The face-visibility tier is a firm deliverable; the mouth-only
tier ships ONLY if its research task finds a real signal (go/no-go). If
the research says no, building a weak guess-based heuristic anyway is a
non-goal — the item re-parks with evidence. Today's end-of-take liveness
REJECT stays the correct fallback either way.
- **Profile management is scoped exactly as §1 pillar 5 says — no
further.** No multi-profile, no account recovery, no "reset a factor
without unlocking first" (that would be a bypass), no changing the
display name, no partial re-enrollment (fewer takes than first
enrollment requires).
- **No re-pinning of measured constants as constants.** `ACCEPT_CUTOFF`,
both `CORRECTION_RADIUS` values, `SYNC_THRESHOLD` keep their pinned
defaults; F9 may make some of them *adjustable at runtime* (Q2) but does
not change any default, and the calibration caveat (the voice 0.45 was
measured against a same-recording probe, not cross-validated) gets
disclosed beside the constant, not "fixed" by tuning.
- **No change to the lock constructions or the vault format** —
`outerlock`, `middlelock`, `facelock` and vault format **v3** stay as
F7/F8 left them. The quality gate refuses *before* sealing; knobs adjust
*decode-time* bounds; profile management (pillar 5) **composes** the
existing constructions into per-layer re-seal operations — new `vault.py`
surface, but no new AEAD construction, no fourth layer, no version bump.
- **No new impostor classes, no deepfake resistance** — unchanged standing
non-goals.
- Out-of-scope discoveries during build: record in `.out-of-scope/`, never
build.

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv; engine in
`src/voicelock/`, UI in `src/voicelock/ui/`, tests in `tests/`; **Python
owns state and thresholds, JS renders only**; **offline-only**.
- **No new dependencies expected.** Quality metrics reuse embeddings/
distances already computed at enroll time; knobs are UI + a settings file;
the camera-error fix is bridge + UI plumbing. Any exception → TECH-PICK.
- F1–F8 engines are reused, not restructured. Anticipated touch points (exact
shapes left to `/plan`): `app.py` (quality checks at enroll, knob
plumbing, `_push_camera_error`, capture-visibility watch, management
bridge methods), `ui/index.html` (refusal copy, knobs panel, camera
chip/banner, live warning, unlocked-state management controls),
`vault.py` (additive per-layer re-seal operations for pillar 5 — a
shared-surface change, so the `project.md` caller-grep guardrail applies
at `/plan`), possibly small additive surface on
`middlelock`/`facelock`/`lipsync` to accept a runtime tolerance argument
where today a module constant is read directly, and the `research` task's
findings file in `memory/research/` (pillar 4's mouth tier).
- Per the earned Booth-layout guardrail: every new visible Booth element
(refusal copy, knobs panel, camera banner/chip) gets a manual layout smoke
test — this repo's Gate cannot see CSS/layout regressions.
- Edge cases (visible, no crash): knob file missing/corrupt → defaults +
visible note, never a crash; quality gate refusal never discards already-
banked takes without saying so; camera error during an unlock capture
still ends the take cleanly (release-on-every-exit-path guardrail); a
management operation that fails or is abandoned mid-way leaves the
on-disk vault byte-identical (atomic write-new-then-swap) and the Booth
in a coherent state; a re-enrollment refused by the quality gate leaves
the existing enrollment fully intact and unlockable.

## 5. Verification — definition of done (runnable)

Fixtures: existing committed fixtures only (`tests/fixtures/voiceprint/*.wav`,
`tests/fixtures/face/*.jpg`) — no new fixtures anticipated; sourcing one is a
scope escalation, not a silent add. Exact test-file names may be finalized at
`/plan`; the coverage obligations below are the contract.

**Standing** (the regression net — `project.md`'s Gate commands):

- `uv run ruff check .` → exit 0.
- `uv run pytest` → exit 0. Reference: **229 passing** at the end of F8; the
count rises by F9's tests and must not fall.

**Feature-specific:**

1. **Quality gate** — `uv run pytest tests/test_enroll_quality.py -q` (name
  indicative) → exit 0. Must cover, per factor: an inconsistent
   enrollment (constructed from the existing fixtures/synthetic spread) is
   **refused** with the per-factor reason code, a consistent one is
   accepted, and refusal makes **zero** calls into `vault.enroll` (mirror
   of F8's liveness-gate assertion). The refuse thresholds' provenance
   (measured, per the dry-run-before-pinning rule) is disclosed where they
   are pinned.
2. **Knobs** — `uv run pytest tests/test_booth_api.py -q` → exit 0,
  extended to cover: the knob bridge surface (read values + defaults, set,
   reset; out-of-range/corrupt/missing settings file → defaults, refused
   visibly, never a crash), and a dialed tolerance provably changing an
   unlock outcome that the pinned default rejects (same fake/spy patterns
   the suite already uses).
3. **Error surfaces** — same suite: the camera-error path pushes its
  **own** error code, asserted distinct from the mic error's, and each
   banner's auto-clear condition fires (camera frame delivered / capture
   start succeeded).
4. **Visibility warning** — same suite: a capture whose fake frames report
  no face for N consecutive frames pushes the live warning; frames with a
   face do not; the warning never aborts the take's release path. (Mouth
   tier, only if its research task lands a signal: the same shape against
   that signal.)
5. **Profile management** — `uv run pytest tests/test_vault.py -q` and
  `tests/test_booth_api.py` → exit 0, extended to cover: passphrase
   change → old passphrase raises `AuthError`, new one unlocks, middle/
   inner ciphertexts byte-unchanged; voice re-enroll → unlockable with the
   new material, face layer byte-unchanged; face re-enroll likewise;
   management methods refused in locked state; a re-enrollment refused by
   the quality gate leaves the on-disk vault byte-identical; the atomic
   swap (a simulated failure mid-write leaves the original vault intact).
6. **Fixture-test strengthening (Q4)** — the same-speaker assertion runs
  on the byte-disjoint pair (`enroll1` vs `enroll5`), and a Gate check
   asserts no probe fixture is a byte-subarray of any reference fixture →
   both exit 0. The `ACCEPT_CUTOFF` calibration caveat is disclosed beside
   the constant (source-text check, regex not literal, per the earned
   rule).
7. **Manual (required)** — run `uv run voicelock` and walk the full §1
  demo: bad enrollment (each factor) refused with its named reason; good
   enrollment proceeds; a borderline reject flips to accept when its knob
   is loosened and back on reset; the five-outcome F8 arc still holds
   verbatim; camera unplugged/blocked shows the camera-named error and
   clears on recovery; covering/turning away the face mid-capture warns
   live; unlock → change passphrase → old rejects/new unlocks; re-enroll
   voice and face → next unlock works. Attested by the human at the
   feature-end checkpoint. Layout smoke test on every new Booth element
   (earned guardrail — this feature adds several).

**Out-of-scope default (Mode 2+):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

*(Asked with the mode question at approval; answer recorded here.)*

**"If every gate in this spec passed but the feature were still wrong, what
would be wrong?"** **Answered by the human at the mode step (2026-07-29;
approved in chat and recorded in `handoff.md`; written here 2026-07-29 by
the `/plan` session per the write-before-proceed rule — see
`memory/deviations.md`):** the quality gate's thresholds and the knobs'
useful ranges are both picked from this repo's tiny fixture set and the
developer's own single voice/face — the gate could refuse enrollments that
are actually fine (or pass ones that flake) for a body of users this repo
has never measured. Same structural shape as F4/F7/F8's disclosed gaps: the
Gate proves the mechanism, only live use proves the calibration. **Accepted
risk:** disclosed at each pinning site and covered by the required live
manual check (§5's manual item), not "fixed" by tuning.

## 7. What F9 inherits (recorded so it survives the next handoff rewrite)

- **From F5 (via `roadmap.md`):** the camera-error-through-`_push_mic_error`
mislabel and its stuck banner — F9 owns the fix (pillar 3).
- **From F8's checkpoint:** the occluded-mouth ask — now §1 pillar 4
(human-decided): the face-visibility tier builds on existing signals; the
mouth tier is research-first go/no-go, because MediaPipe's landmark
output has no known "occluded" signal — the research task either finds
one or documents that it does not exist.
- **From `roadmap.md`'s parked list:** F11 (profile management), absorbed
whole as §1 pillar 5 (human-decided) — `roadmap.md`'s F11 entry is
updated to point here.
- **From the 2026-07-26 calibration runs:** the same-speaker test's
vacuity (Q4) and the disclosure that voice `ACCEPT_CUTOFF = 0.45` was
measured against a same-recording probe (§3 — disclose beside the
constant, do not re-tune).
- **From F4/F7/F8:** thresholds are measured or explicitly-estimated and
disclosed, never tuned until the demo "looks right" — F9's quality gate
and knob defaults follow the same discipline.
- **From `project.md`:** the no-unexercised-surface rule, the
mutation-sensitivity rule, the source-text-meaning rule, the
dry-run-before-pinning rule, the acquisition/release rule, the
Booth-layout manual-smoke-test rule, and the caller-grep rule if any
shared signature changes (e.g. threading a tolerance argument through
`reconcile`).


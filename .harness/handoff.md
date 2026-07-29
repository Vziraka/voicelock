# Handoff

## F9 — Demo reliability · SPEC DRAFTED, PARKED AT THE APPROVAL GATE

**2026-07-29.** `/spec` ran interactively for F9. All grilling questions
resolved with the human (Q1–Q5b + mode + blind-spot); the Grilling record is
`Status: CLEAR` (mechanically verified — zero `[NEEDS-CLARIFICATION:` hits);
box 1 is checked; **box 2 awaits the human's own `x`**. Mode line set:
**Mode 3 — Spec-to-done** (human-chosen 2026-07-29).

### next_action

1. **Human:** in `spec.md`, read §1 Outcome + §5 Verification, confirm the
   Mode line, and type the `x` in approval box 2 yourself.
2. Then run `/plan` in a **fresh session**.

### What F9 became at grilling (larger than the roadmap entry)

Five pillars — the human expanded scope twice, both against the agent's
initial recommendation (recorded as human decisions, not drift):

1. **Enrollment-quality gate** (Q1) — cross-take spread vs. the lock's
   correction budget, per factor; refuse with actionable per-factor copy;
   thresholds measured at build time, never guessed.
2. **Tolerance knobs** (Q2) — three real-path knobs (voice radius 110,
   face radius 95, lip-sync threshold 0.5 as defaults), persisted in
   `~/.voicelock/settings.json`, defaults shown + reset + honesty copy.
   Feasible without re-enrollment: both `reconcile()`s bound acceptance at
   decode time (`middlelock.py:161`, `facelock.py:166`).
3. **Camera-error fix** (Q3) — distinct CAMERA ERROR surface via a new
   `_push_camera_error` (mislabel lives at `app.py:720`), auto-clear on
   device recovery; mic banner auto-clears likewise.
4. **Live capture-visibility warning** (Q5a — pulled in from F8's parked
   ask) — face-not-visible tier is a FIRM deliverable (existing no-face
   signal); mouth-only-occlusion tier is **research-first go/no-go** (a
   bounded `research` task opens the feature; no signal → item re-parks
   WITH the evidence file, F9 still completes).
5. **Profile management** (Q5b — absorbs roadmap F11 whole) — after
   unlock only: change passphrase / re-enroll voice / re-enroll face as
   per-layer re-seals (vault stays v3, no new construction), atomic
   write-new-then-swap, re-enrollment runs the same quality gate.

Plus the Q4 housekeeping fold-in: rewrite the vacuous same-speaker test to
the byte-disjoint `enroll1`/`enroll5` pair + a no-probe-is-a-subarray Gate
check + the `ACCEPT_CUTOFF = 0.45` calibration caveat disclosed beside the
constant.

Blind-spot answer (human-approved): the calibration gap (thresholds/ranges
from a tiny fixture set + one person's biometrics) is **accepted risk**,
disclosed at pinning sites + covered by the live manual check.

### Notes for `/plan`

- `vault.py` gains per-layer re-seal surface → **the caller-grep guardrail
  applies** (F4-T3/F7-T2 both BLOCKED on exactly this shape).
- Threading runtime tolerances through `vault.unlock` is also a
  shared-signature change — same guardrail.
- Several new visible Booth elements → the Booth-layout manual-smoke-test
  guardrail applies to each.
- Pillar 4's research task should run FIRST or in parallel — the rest of
  F9 never blocks on it.
- Verification contract: spec §5 — 7 items; test-file names indicative,
  coverage obligations fixed.

### State-file conflict resolved this session (before the spec ran)

`handoff.md`'s previous content still showed F8's checkpoint as pending
while `plan.md`/`roadmap.md`/git (`adc7fed`, F8 complete commit) all said
DONE. Adjudicated via git history per the universal [State] precedence
rule; logged in `memory/deviations.md` (2026-07-29 entry). F8 is closed;
this file's previous content is superseded by exactly that resolution.

### Session writes (this session)

- `spec.md` — rewritten for F9 (was F8's spec, which lives in git history).
- `roadmap.md` — F9 entry records the two scope expansions; F11 parked
  entry marked ABSORBED INTO F9.
- `memory/deviations.md` — one appended entry (the F8 handoff staleness
  conflict + resolution).
- `handoff.md` — this file.
- `plan.md` — NOT touched: still F8's completed ledger; `/plan` rewrites it
  for F9 after box 2 is checked.

### Session commits

Base: `adc7fed` (F8 complete). Head: `1e02169` (this spec session's state
commit, human-approved, pushed to origin/main). The base→head hash pair in
this file was amended after the checkpoint commit; if a follow-up state
commit exists on top of `1e02169`, it contains only this amendment.

# Handoff

## F9 — Demo reliability · PLANNED — READY TO BUILD

**2026-07-29.** `/plan` ran for F9. The ledger is in `plan.md`: **10 tasks,
all `TODO`, `rejects: 0`**, dependency-ordered, every done-criterion
runnable. Mode 3 — Spec-to-done (human-set in `spec.md` §0).

### next_action

**The approved Mode 3 is the standing go: `/implement` starts Task 1
(the mouth-occlusion research go/no-go) in a fresh session.** No further
human "go" is needed inside the feature; the human is next consulted at the
feature-end checkpoint (or on an escalation/amendment).

### Gate incident resolved at session start (before planning)

The spec's §6 blind-spot answer still carried the live `[NEEDS-CLARIFICATION:`
token on disk — the spec session resolved it with the human in chat
(recorded in the previous handoff) but never wrote it into §6, so the
mechanical zero-hits scan FAILED despite the human's genuine box-2 approval
(their `x` was the only substantive uncommitted spec edit). Executed the
missed write-before-proceed: §6 now carries the human-approved answer
(calibration gap = accepted risk, disclosed at pinning sites + covered by
the live manual check), the scan returns zero hits, and the conflict +
resolution is logged as the 2026-07-29 "F9 (pre-plan gate check)" entry in
`memory/deviations.md`.

### Shape of the plan (details in `plan.md` — do not re-derive)

1. **Task 1** research: mouth-occlusion signal, go/no-go — verdict decides
   Task 5's mouth tier; nothing else blocks on it.
2. **Task 2** Q4 fold-in (byte-disjoint same-speaker test + subarray guard
   + `ACCEPT_CUTOFF` caveat comment).
3. **Task 3** `settings.py` + additive-optional tolerance params through
   `reconcile`×2 / `is_live` / `vault.unlock`.
4. **Task 4** `enrollquality.py` + enroll refusal (thresholds MEASURED at
   build, zero `vault_enroll` calls on refusal).
5. **Task 5** camera-error surface (fix site `app.py:720`) + auto-clear +
   live face-visibility warning (+ mouth tier iff Task 1 says GO).
6. **Task 6** knob bridge + unlock-path consumption (threshold flip test).
7. **Task 7** vault per-layer re-seal (`change_passphrase` /
   `reseal_voice` / `reseal_face`) + atomic write-new-then-swap,
   byte-identity asserted directly.
8. **Task 8** management bridge (unlocked session held by `BoothApi`,
   `lock()` clears; re-enrolls run the SAME quality gate).
9. **Task 9** UI: refusal copy, camera banner/chip, live warning, knobs
   panel (+ layout smoke per element, earned guardrail).
10. **Task 10** UI: management panel — LAST task, full spec Verification
   incl. the required human-attested live demo.

### Standing cautions for the implementor

- **Caller grep already executed at plan time** (`plan.md` has the results):
  every shared-surface change is additive-optional. If any change turns out
  NOT to stay additive-optional mid-build, that is a plan contradiction —
  STOP per the universal [Modes] rule (F4-T3/F7-T2 precedent).
- Thresholds (quality gate, faceless-frame N) are measured/dry-run before
  pinning, provenance disclosed — never guessed (earned guardrail; the
  novel Task 1 done-criterion command was itself dry-run at plan time,
  positive and negative cases).
- Every new visible Booth element needs the manual layout smoke test — the
  Gate cannot see CSS/layout regressions (earned guardrail).
- No default constant changes anywhere (spec §3); knobs are decode-time
  runtime values only.

### Session writes (this session)

- `spec.md` — §6 token replaced with the human-approved blind-spot answer
  (the gate incident above); no other content touched.
- `memory/deviations.md` — one appended entry (the pre-plan gate conflict +
  resolution).
- `plan.md` — rewritten: F9 ledger (was F8's completed ledger, which lives
  in git history).
- `handoff.md` — this file.

### Session commits

Base: `957b908` (F8 handoff bookkeeping, last commit before this session).
Head: recorded after the commit checkpoint below.

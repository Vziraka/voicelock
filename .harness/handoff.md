# F7 — Face as the inner lock (innermost) · AT APPROVAL GATE

**Spec drafted and grilled 2026-07-27.** All four must-answer clarification
markers resolved interactively with the human; the Mode 2+ mandatory
blind-spot question resolved; Mode set to **Mode 3 — Spec-to-done**. Grilling
record is `CLEAR` (box 1 checked). Box 2 (human approval) is the only thing
outstanding.

## What F7 does
Fuzzy-reconciles the F6 faceprint into a stable key and seals a third,
innermost AEAD layer (vault v3) around F4's voice middle lock, around F2's
passphrase outer lock. Unlock now peels passphrase → voice → face, each
impostor class failing at its own named layer.

## Key decisions from grilling (2026-07-27, all human-approved)
1. **Face-data scarcity (Q1, the hardest question).** This repo has only one
   genuine same-person face pair (Douglass A1/A2, from F6). Rather than
   commissioning new `research` for more fixtures, F7 reuses what exists:
   live enrollment reuses F6's `REFERENCE_TAKES = 3` burst pattern; the
   automated Gate test enrolls on A1 alone (the reliability mask's own
   documented margin-ranking fallback handles a single take), reconciles
   against A2 for the accept case and B for the reject case. Disclosed as a
   thinner test than production (1 fixture take vs. 3 live frames).
2. **Sizing knobs (Q2).** `CANDIDATE_BITS`/`RELIABLE_BITS`/`KEY_BITS`/
   `REPETITION` reused unchanged from `middlelock.py` (4096/512/32/16) — they
   size the ECC bit-budget, not the embedding width, so no ratio-scaling.
   `CORRECTION_RADIUS` is the one knob actually measured, from the thin (n=1
   genuine, n=2 impostor) A1/A2/B data — disclosed as weaker evidence than
   F4's 200-commit measurement.
3. **Vault v3 (Q3).** `FORMAT_VERSION = 3`; both v1 and v2 vaults refused via
   `LegacyVaultError` (message names the missing layer), re-enroll required,
   no bypass — mirrors F4's v1 handling exactly.
4. **Booth UX (Q4).** F6's diagnostic faceprint panel stays untouched and
   independent. F7 adds a new, separate enroll-face capture step (after the
   existing enroll-voice step) feeding only `facelock.commit`/`reconcile` —
   never `faceprint.ref`.
5. **Mode 2+ blind spot.** Accepted risk: the automated test only proves
   separation on one genuine pair, not real cross-session generalization —
   mitigated by the required live manual check (§5 cmd 4), same shape F4 used
   for the identical voice-side gap.

## next_action
**Human checks box 2 in `spec.md`** (§0 Approval gate) — everything else is
resolved. Once checked, the next session runs `/plan` to break this into a
task ledger (expect a `facelock.py` sibling module to `middlelock.py`, a
`vault.py` v3 update, `app.py` bridge additions, and Booth UI additions,
mirroring F4's Task 1–5 shape).

## Commits this session
Base: `ae93c4d` (F6 feature-end checkpoint, guardrails written). This
session's write: `spec.md` (F7 draft, fully grilled) + this `handoff.md`.
Not yet committed — proposing the commit next, pending your go-ahead.

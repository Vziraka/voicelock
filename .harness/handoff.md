# F6 — Faceprint on screen · SPEC GRILLING SESSION

**Session date: 2026-07-26/27.** F5.5's Mode 4 tail drafted F6's spec
unattended and parked it at the approval gate with ten embedded clarification
markers. This session resolved all ten interactively with the human, two
(Q1, Q7) backed by dedicated `research` runs rather than the drafted
recommendation alone.

## What happened this session

- **Q1 (fixtures — hardest question).** `research` located a genuine,
  independent same-person pair: two 19th-century photographs of Frederick
  Douglass from different sittings, different photographers, different
  archival custodians (Library of Congress 1870; National Archives c.1879),
  both `Public domain` per Wikimedia Commons' per-file metadata. Confirmed
  faces=1/landmarks=478 against the vendored bundle. Not a derived probe —
  F5.5's failure mode does not apply. Different-person B carries over from
  F5's research (CC0 MET daguerreotype). Written up:
  `memory/research/2026-07-26-f6-same-person-fixture-pair.md`.
- **Q7 (architecture — MediaPipe→SFace alignment).** A must-verify question
  under the universal [Uncertainty] rule, so it was tested, not just
  recommended: downloaded SFace ONNX weights to the session scratchpad
  (never committed), built a 5-point YuNet-shaped row from MediaPipe's
  existing 478 landmarks, empirically confirmed point order via visual
  inspection of the aligned crop, then ran real embeddings on the Q1
  fixtures — same-person scored cosine 0.7325/L2 0.7314, different-person
  scored cosine 0.10–0.14/L2 1.31–1.34, cleanly separated against OpenCV's
  own thresholds. No YuNet vendoring needed. Written up:
  `memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md`.
- **Q2–Q6, Q8, Q9, §6** resolved via the `grilling` skill, one question at a
  time, each with a plain-language explanation (the human asked for that
  framing) and the drafted recommendation — all resolved as the drafted spec
  recommended.
- **Mode: set to Mode 3 — Spec-to-done** (human's explicit choice, offered
  alongside Mode 2 and Mode 1; Mode 4 was available but not chosen).
- `spec.md` updated throughout: every marker replaced with its resolution
  inline, all Grilling-record table rows now `Resolved`/`Clear`, §1's outcome
  point 2 corrected (originally said "measured cutoffs", contradicting Q5's
  resolution to adopt OpenCV's published thresholds — fixed), §4's Q7
  conditional removed, §5 Verification section rewritten with concrete pinned
  commands (fixture filenames `personA_1.jpg`/`personA_2.jpg`/`personB.jpg`,
  a real same/diff-face assertion, a convert-not-refuse resolution test, a
  mutation-sensitivity test, and a liveness-honesty UI-copy test), §0's
  Grilling-record box now checked.
- **Grilling record: `Status: CLEAR`.** The bracketed clarification marker
  (colon form) appears nowhere in `spec.md` — verified by grep.

## next_action

**Box 2 is open — the human must type the `x` in `spec.md`'s Approval gate
themselves** (the agent never checks it, per the universal rule). Once
checked, run `/plan` in a fresh session to break F6 into tasks. No planning or
building happens before that box is checked.

## Commits

*(this session's changes are staged for the commit checkpoint below; hashes
recorded here once the human approves the commit)*

Files touched: `spec.md`, `memory/research/2026-07-26-f6-same-person-fixture-pair.md`,
`memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md`, this file.
No source code changed — this was a spec-grilling session only, per WIP=1 and
the universal rule against planning/building before the Grilling record is
`CLEAR` and box 2 is checked.

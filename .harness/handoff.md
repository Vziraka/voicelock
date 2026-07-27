# F6 — Faceprint on screen · PLAN SESSION

**Session date: 2026-07-27.** Previous session (F6 spec grilling, 2026-07-26/27)
left both approval-gate boxes for the human to check; the human checked box 2
this session. This session ran `/plan` and wrote F6's task ledger.

## What happened this session

- Verified the entry gate mechanically: Grilling record `Status: CLEAR`,
  `NEEDS-CLARIFICATION` marker grep → 0 hits, both approval boxes checked,
  `Mode: Mode 3` set.
- Read the approved spec, the universal + project constitution,
  `memory/codebase-map.md`, and the current code (`voiceprint.py`,
  `facedetect.py`, `app.py`, `index.html`) plus both F6 research files
  (`2026-07-26-f6-same-person-fixture-pair.md`,
  `2026-07-26-f6-mediapipe-to-sface-alignment.md`) as the pattern to mirror
  and the evidence already in hand.
- **Found a genuine plan-time design gap the spec deliberately left open**
  (§5 cmd 3's note: "exact call shape... set at `/plan`"): OpenCV's two
  published SFace thresholds (cosine ≥ 0.363, L2 ≤ 1.128) turn out to be the
  *same* operating point in two metrics (L2² = 2(1−cosine) for unit vectors),
  not two independent bars — so there is exactly one vendor number, and F3's
  three-band meter needs two (`ACCEPT_CUTOFF`/`REJECT_CUTOFF`). Q5 explicitly
  forbids deriving a second, repo-measured cutoff. Put to the human with a
  recommended default and one alternative; **the human chose
  `REJECT_CUTOFF = ACCEPT_CUTOFF = 1.128`** (no invented number; the meter's
  borderline band has zero width in practice). Written to
  `memory/decisions.md` (2026-07-27 entry) before the plan was finalized, per
  the write-before-proceed rule.
- Wrote `plan.md`: 5 tasks — (1) vendor + licence the SFace ONNX weights,
  (2) commit the three face fixtures + README, (3) `faceprint.py` itself
  (alignment, embed/compare, cutoffs, convert-not-refuse, mutation-sensitive
  test), (4) Booth bridge wiring (`app.py` + a small additive `FaceEngine.last_frame`),
  (5) Booth UI panel + liveness-honesty copy (LAST task, full spec
  Verification + required manual check). All `TODO`, `rejects: 0`.
- Two other architecture notes recorded in `plan.md`'s "Named architecture
  decisions" section (not put to the human — read as low-risk, additive,
  spec-compatible implementation details rather than genuine forks): (a)
  `faceprint.py`'s `embed_frame`/`embed_file` run their own `IMAGE`-mode
  `FaceLandmarker` instance (same vendored bundle, no new model) rather than
  reusing `facedetect.py`'s `VIDEO`-mode one — matches §5 cmd 4's pinned
  call shape (`embed_frame(img)`, no landmarks argument) exactly; (b) the
  live Booth path needs `FaceEngine` to expose its last raw frame — a small
  additive field, not a change to the composite/lifecycle the non-goals
  protect.

## next_action

**Mode 3 — the approved spec's Mode line is the standing "go."** A fresh
`/implement` session starts **Task 1** (vendor SFace + establish its licence)
without waiting for a further human "go." If Task 1's licence check does not
clear cleanly, that session sets Task 1 `BLOCKED` and stops for the human —
per the Mode 3 rule on rules that cannot be followed unsupervised.

## Commits

Session base → head: `c7150f2` → `1acb613` (one commit, human-approved
2026-07-27). State files only: `spec.md` (box 2 checked, one editor-reflow
corruption on line 38 found and fixed), `plan.md` (new F6 task ledger),
`handoff.md` (this file), `memory/decisions.md` (the REJECT_CUTOFF entry).

**Nothing pushed.** `origin` exists (private) — push was not requested this
session.

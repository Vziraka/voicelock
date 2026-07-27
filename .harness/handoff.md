# F7 — Face as the inner lock (innermost) · PLANNED, READY TO BUILD

**Spec approved 2026-07-27** (both boxes checked, Mode 3). This session ran
`/plan`: read `spec.md`, `constitution/universal.md` + `project.md`,
`memory/codebase-map.md`, and the current `middlelock.py`/`vault.py`/
`faceprint.py`/`app.py`/`index.html` to ground the ledger in the real code
shape rather than guessing it.

## What F7 does
Fuzzy-reconciles the F6 faceprint into a stable key and seals a third,
innermost AEAD layer (vault v3) around F4's voice middle lock, around F2's
passphrase outer lock. Unlock peels passphrase → voice → face, each impostor
class failing at its own named layer.

## Task ledger (plan.md)
4 tasks, no new model/fixture vendoring needed (F7 reuses F6's SFace model and
A1/A2/B fixtures):
1. `facelock.py` — the face fuzzy-commitment module (commit/reconcile/
   derive_key), `CORRECTION_RADIUS` measured from A1/A2/B residuals.
2. `vault.py` — bump to v3, nest the face inner lock, refuse v1 **and** v2.
3. `app.py` (Booth bridge) — enroll-face capture step, `unlock`'s third
   layer, distinct `auth_face`.
4. `ui/index.html` — enroll-face capture step + third reject chip *(LAST
   task — full spec Verification, including the required live manual check)*.

## Named architecture decisions this session made (recorded in `plan.md`)
The spec deliberately left "exact call shape" to `/plan` (same as F6's Q8).
Six decisions recorded, the two most load-bearing:
- `facelock.commit()` takes a **variable-length** embedding list (≥1), not a
  fixed exact count like `middlelock.commit()`'s hard `== 5` assert — this is
  what lets the Gate test enroll on A1 alone while production enrolls on 3
  live frames, with zero extra code (the reliability mask's own cross-take-
  unanimity filter is already vacuously true at n=1).
- New bridge methods `enroll_face_take()`/`reset_enroll_face_takes()`,
  distinctly named from F6's diagnostic `set_face_reference()`/
  `compare_face()`/`reset_face_reference()` — two independent flows reading
  the same camera, never sharing state.

Full detail (vault v3 layout, key renames, error classes, version bytes): see
`plan.md`'s "Named architecture decisions" section.

## next_action
Mode 3 is the standing "go" — the next session runs `/implement` for Task 1
(`facelock.py`) without waiting for a further human prompt. No blockers.

## Commits this session
Base: `96806ba` (F7 spec grilled, parked at approval gate). This session:
human checked spec.md's box 2 (approval); `/plan` wrote `plan.md` (F7 task
ledger, superseding F6's completed one) and this `handoff.md`. Proposing the
commit next, pending your go-ahead.

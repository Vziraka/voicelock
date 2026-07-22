# Handoff — Roadmap pivoted (voice + face + lips); next: /spec F3

## Session
- Date: 2026-07-22
- Feature: none active — `/design` session (idea → roadmap), not a feature build
- Phase: design complete, roadmap approved by human
- Mode: n/a until F3's spec sets one (Mode 2 default unless human states otherwise)

## Done this session
- Tidy: removed untracked `harness-v1/`; confirmed `Notes on testing V5.md` already gone.
  Working tree clean of clutter. Confirmed session-start git snapshot was stale
  (HEAD is `4b2391a`, F2 wrap-up); F1-T5 verdict is legit committed F1 history.
- Ran `/design` for the human's pivot: **augment to three biometric factors —
  voice + face + lip-liveness** on top of the typed passphrase.
- Grilling decisions (all human-approved, logged in `memory/decisions.md`):
  1. Augment (not replace voice) → 3 factors.
  2. **Three nested locks**: passphrase (outer) → voice (middle) → face (inner).
  3. Passphrase stays **typed** (exact secret; F2 untouched).
  4. Liveness = **audio-visual lip-sync** to a spoken random challenge.
  5. Build **Order A**: voice fully, then face, then liveness, then reliability.
- Rewrote `roadmap.md` (idea in user's words · Approach B′ · new diagram ·
  F1–F9 features + parked F10 · out-of-scope). Seeded `CONTEXT.md` (Middle/Inner
  lock, Faceprint, FaceView, Lip-sync, AV capture) and the `codebase-map.md`
  diagram (planned camera/face/lip boxes). New `adr/0002-three-nested-locks.md`
  supersedes 0001.

## Next action
1. Run `/spec` on **F3 — Voiceprint on screen** (blocked-by F1 only; F1+F2 done).
   Fresh session; grilling gate must reach `CLEAR`; human sets the Mode + checks box 2.
2. F5 will need a **TECH-PICK** for the offline face detect/landmark/embedding
   stack — research + human approval when that feature is specced. Not now.
3. Open nice-to-have: product **rename** from "VoiceLock" (parked in roadmap
   out-of-scope) — human decides if/when.

## Roadmap at a glance (build order)
F1 ✅ booth · F2 ✅ outer lock · F3 voiceprint · F4 voice middle lock ·
F5 camera booth · F6 faceprint · F7 face inner lock · F8 lip-sync liveness ·
F9 demo reliability · (F10 parked robotic heuristic).
Full impostor arc (wrong passphrase / voice / face / replay) reachable at F8.

## Commit checkpoint
- Base (session start): `4b2391a`
- Head: `60d1d33` (design commit) + this bookkeeping commit
- Remote: none — local history only, no push
- Files: `roadmap.md`, `CONTEXT.md`, `memory/codebase-map.md`,
  `memory/decisions.md`, `adr/0002-three-nested-locks.md`, `handoff.md`
- `spec.md` / `plan.md` intentionally untouched — stay F2-complete until `/spec` F3.

## Pending
- Human: start `/spec F3` in a fresh session when ready.

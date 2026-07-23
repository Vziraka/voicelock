# Handoff — F3 spec drafted (CLEAR, Mode 3); awaits human box 2 → /plan

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: spec complete — Grilling record `CLEAR`, box 1 checked, **box 2 (human) open**
- Mode: **Mode 3** (set in the spec Approval gate; human confirms by checking box 2)

## Done this session
- Ran `/design` (earlier) → pivot roadmap committed (`60d1d33`, `76c40c5`).
- Ran `/spec` on F3. Full ambiguity scan → all rows Clear. Grilling decisions
  (human-approved, one at a time):
  1. **Voiceprint method = SpeechBrain ECAPA** (`spkrec-ecapa-voxceleb`) —
     human-approved TECH-PICK. Research: `memory/research/2026-07-22-f3-voiceprint-embedding.md`.
     Rejected Resemblyzer (liveness FAIL/abandoned) + librosa DIY (muddier).
  2. **Model provisioning = vendored in-repo** at `src/voicelock/models/ecapa/`
     (Apache-2.0, redistribution OK) + `HF_HUB_OFFLINE` → offline runtime + hermetic Gate.
  3. **Reference voiceprint** = Booth "Set reference" records **3 sentences**,
     embeds each, **averages** (L2-norm mean) → `~/.voicelock/voiceprint.ref`
     (plaintext vector, not in vault; F4 supersedes). Multi-sample averaging
     deliberately overlaps F9; full quality gate stays F9.
  4. **Meter = cosine distance, 3-band** (accept/borderline/reject); cutoffs tuned
     on fixtures during build, pinned via deterministic fixture assertions.
  5. **Blind spot → required manual Booth demo** (real mic Set reference + real
     same-vs-different separation), not accepted risk. Mirrors F1/F2.
- Wrote runnable Verification (§5): standing ruff+pytest exit 0; `tests/test_voiceprint.py`
  on fixtures + vendored offline model; required manual Booth line. Budget within 10-min default.

## Next action
1. **Human:** in `spec.md`, read Outcome (§1) + Verification (§5), confirm the
   `Mode: Mode 3` line, and type the `x` in **box 2** of the Approval gate.
2. Then run `/plan` (fresh session) to break F3 into small ordered tasks. Likely
   task shape: (a) add ECAPA deps + vendor model offline; (b) voiceprint engine
   (embed + average + cosine + cutoffs) with fixtures; (c) Booth Set-reference +
   live 3-band meter wiring; (d) end-to-end + manual Booth demo.
3. Do NOT plan or build until box 2 is checked (universal [Startup]/[Approval]).

## Commit checkpoint
- Base (spec session): `76c40c5`
- Head: this spec commit (hash recorded in the follow-up bookkeeping commit)
- Remote: none — local history only, no push
- Files: `spec.md`, `memory/decisions.md`, `memory/research/2026-07-22-f3-voiceprint-embedding.md`
- `plan.md` intentionally still F2-complete — rewritten by `/plan` after box 2.

## Pending
- Human: check box 2, then start `/plan` for F3 in a fresh session.

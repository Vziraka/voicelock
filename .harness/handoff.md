# Handoff — F3 planned (4 tasks, all TODO); next: /implement Task 1

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: plan complete — `plan.md` holds 4 ordered tasks, all `TODO`, `rejects: 0`
- Mode: **Mode 3** (spec Approval gate, box 2 checked)

## Done this session
- Entry gate re-checked and PASSED (quoted): §2 `**Status: CLEAR**`; token scan for
  `[NEEDS-CLARIFICATION:` → zero hits; approval boxes 1 & 2 both `[x]`; `Mode: Mode 3`.
- Note on the gate: an earlier uncommitted edit to `spec.md` had bundled box-2
  approval with an accidental revert of §2 to `DRAFT` (plus stripped indents).
  Flagged it; the human restored `**Status: CLEAR**` before this /plan run.
- Broke F3 into 4 tracer-bullet tasks (each names its files + a runnable done):
  1. ECAPA deps (`speechbrain`/`torch`/`torchaudio`) + vendor model offline at
     `src/voicelock/models/ecapa/` (Apache-2.0, one-time build download, committed).
  2. Voiceprint engine (`src/voicelock/voiceprint.py`) — embed · L2-avg reference
     (injectable path) · cosine · `ACCEPT/REJECT_CUTOFF` 3-band · offline load —
     plus fixtures + `tests/test_voiceprint.py` covering spec §5 cases (1)–(5).
  3. Booth chrome (`ui/index.html`) — Set reference + live 3-band meter + distance
     readout + "need more audio"/"set reference first" states; JS renders only.
  4. Bridge (`app.py` BoothApi) + wire JS + `tests/test_booth_api.py`; LAST task →
     done-criterion is the FULL spec §5 Verification incl. the required manual demo.
- Refreshed the memory spine in `plan.md`.

## Next action
1. `/implement` **Task 1** in a **fresh session**. Mode 3: the approved spec's
   `Mode:` line is the standing "go" for tasks inside F3 — no further human "go"
   needed to start. Implement builds ONE task (commits `DOING` first), then hands
   to a clean-context verifier.
2. Watch-outs for Task 1: `uv add` (never bare pip); the model download is the
   only network step and is a build-time developer action (runtime stays offline);
   commit the ~20 MB model files plainly (no LFS); keep LICENSE/NOTICE alongside.

## Commit checkpoint
- Base (this /plan session): `616e543`
- Head: this planning commit (see git log after commit)
- Remote: none — local history only, no push
- Files: `plan.md`, `handoff.md`, `spec.md` (human's box-2 + status-restore edit)

## Pending
- None blocking. F3 ready to build at Task 1.

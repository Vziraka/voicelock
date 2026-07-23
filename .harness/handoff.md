# Handoff — F3 Task 5 (Reset) built (REVIEW, LAST task); next: verify + human manual demo

## Session
- Date: 2026-07-23
- Feature: F3 — Voiceprint on screen (`spec.md`, amended 2026-07-23)
- Phase: implement — Task 5 (Reset, LAST task) built, now `REVIEW`; Tasks 1–4 DONE
- Mode: **Mode 3**

## Changed (Task 5 — Reset control)
- `src/voicelock/app.py` — `BoothApi.reset_reference()`: clears `_reference_takes`
  and `self.ref_path.unlink(missing_ok=True)`, returns `{ok: true}`.
- `src/voicelock/ui/index.html` — a **Reset** button (`btn-reset-reference`) next
  to Set reference → calls the bridge → `setReferenceProgress(0)` +
  `showSetReferenceFirst()`. No confirm prompt; JS renders only. Everything else
  (Set reference, Record/Stop/Play, Enroll/Unlock) unchanged.
- `tests/test_booth_api.py` — +2 tests: (a) reset clears a set reference →
  `compare` returns `no_reference` and the file is gone; (b) reset is a no-op on a
  missing file and clears an in-progress take (progress restarts at 1). 10 booth
  tests pass locally.

## Measurement disclosure (step-5 exception)
- Ran `uv run ruff check .` (clean) and `uv run pytest tests/test_booth_api.py -q`
  (10 passed) locally as build sanity. Did NOT run the full `uv run pytest`,
  `tests/test_voiceprint.py`, or the manual demo as the authoritative Gate —
  reserved for fresh eyes.

## Next action — verify (LAST task → FULL amended §5)
1. **Fresh-eyes verify** Task 5 (clean context — subagent via
   `formats/VERIFIER-PROMPT.md` verbatim, or a fresh session).
   - Gate base..head: **`55ff22a..ec9dc6b`** (DOING .. build; a bookkeeping commit
     for this handoff is one ahead of the build commit).
   - Task 5 done-criteria = the FULL amended `spec.md` **Verification** list:
     - `uv run ruff check .` → 0
     - `uv run pytest` → 0
     - `uv run pytest tests/test_voiceprint.py -q` → 0 (spec §5 cases 1–5)
     - `uv run pytest tests/test_booth_api.py -q` → 0 (incl. the reset test)
     - **Manual (required, human-attested):** `uv run voicelock` → Set reference
       (3 sentences) → same person → accept/green → different person → reject/red
       → **Reset** → meter returns to "set reference first", fresh reference
       can be set again.
2. **The manual line needs a HUMAN** (real mic + observing the meter) — expect the
   verifier to PASS the automated Gate + APPROVE the automated axes and
   **ESCALATE_HUMAN for the manual demo**. On the human's attestation → wrap-up
   marks Task 5 DONE and writes the **Mode-3 completion report**, completing F3.

## Manual demo steps for the human (one combined run)
- `uv run voicelock` → record a sentence, **Set reference** (dot 1); repeat ×2
  (dots 2, 3) → "reference set".
- Same person records a sentence → **accept (green)**, small distance.
- Different person → **reject (red)**, large distance.
- Click **Reset** → dots clear, meter shows "set reference first"; set a new
  reference to confirm it works again.

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md` (amended). Deviations:
  `memory/deviations.md`. Roadmap F11 parked (vault-side enrollment management).

## Commits
- DOING: `55ff22a` · build (REVIEW): `ec9dc6b` · bookkeeping: this commit.
- Remote: none — local history only, no push. (Mode-3 feature-end checkpoint is
  the human's: completion report + commit approval.)

## Pending guardrail
- None.

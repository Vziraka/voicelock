# Handoff — F3 Task 4 built (REVIEW, LAST task); next: fresh-eyes verify + human manual demo

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: implement — Task 4 (the feature's LAST task) built, now `REVIEW`;
  Tasks 1–3 DONE
- Mode: **Mode 3**

## Changed (Task 4 — bridge + end-to-end)
- `src/voicelock/app.py` — `BoothApi` gained an injectable `ref_path` and two
  methods calling the Task-2 engine:
  - `set_reference()` — banks the last captured take; validates it via
    `voiceprint.embed` (rejects too-short/silent with `{"error":"need_more_audio"}`,
    not added); after 3 valid takes calls `voiceprint.set_reference` → persists the
    averaged reference; returns `{ok, done, progress}`.
  - `compare()` — `voiceprint.compare(buffer)` → `{ok, distance, band}`, or
    `{"error":"no_reference"|"need_more_audio"}`.
- `src/voicelock/ui/index.html` — Set-reference handler now handles the
  progressive `{progress, done}` response; new `updateVoiceprintMeter()` runs
  after each Stop (record branch) → `renderDistance` / `showSetReferenceFirst` /
  `showNeedMoreAudio`. Enroll/Unlock + Record/Stop/Play unchanged.
- `tests/test_booth_api.py` — +3 tests (stub capture fed the real fixtures,
  temp ref path): reference→same-speaker accept / different-speaker reject;
  short take rejected with `need_more_audio` (progress 0, no file); compare with
  no reference → `no_reference`. 8 booth tests pass locally.
- Packaging: confirmed `uv run voicelock` is an **editable** install (resolves to
  `src/voicelock/`), so the vendored `models/ecapa/` is found at runtime — no
  wheel `force-include` change needed for the demo (kept the diff surgical;
  a future real wheel build would still need the force-include).

## Measurement disclosure (step-5 exception)
- Ran `uv run ruff check .` (clean) and `uv run pytest tests/test_booth_api.py -q`
  (8 passed) locally as build sanity. Did NOT run the full `uv run pytest`,
  `tests/test_voiceprint.py`, or the manual demo as the authoritative Gate —
  reserved for fresh eyes.

## Next action — verify (this is the LAST task → FULL spec §5 Verification)
1. **Fresh-eyes verify** Task 4 (clean context — subagent via
   `formats/VERIFIER-PROMPT.md` verbatim, or a fresh session).
   - Gate base..head: **`fb248ec..1f59982`** (DOING .. build; a bookkeeping
     commit for this handoff is one ahead of the build commit).
   - Task 4 done-criteria = the FULL `spec.md` **Verification** list:
     - `uv run ruff check .` → 0
     - `uv run pytest` → 0
     - `uv run pytest tests/test_voiceprint.py -q` → 0 (spec §5 cases 1–5)
     - **Manual (required, human-attested):** `uv run voicelock` → Set reference
       (speak 3 sentences) → same person reads → meter small / **accept (green)**
       → different person reads → meter large / **reject (red)**.
2. **The manual line needs a HUMAN** — a subagent/CI cannot drive a real mic or
   observe the meter. Expect the verifier to PASS the automated Gate + APPROVE
   the automated axes and **ESCALATE_HUMAN for the manual demo** (same pattern as
   F2-T4: "human attested manual Booth PASS after prior ESCALATE_HUMAN"). The
   task is NOT DONE — and F3 is not complete — until a human runs the manual demo
   and attests it. On that attestation → wrap-up marks Task 4 DONE and writes the
   Mode-3 completion report.

## Manual demo steps for the human
- `uv run voicelock` → record a short sentence, click **Set reference** (dot 1),
  repeat twice more (dots 2, 3) → hint shows "reference set".
- Same person: record a sentence → the meter needle + readout should land
  **accept (green)**, small distance.
- Different person: record a sentence → **reject (red)**, large distance.
- Edge checks (optional): click Set reference on a <0.4 s clip → "need more
  audio"; compare before any reference → "set reference first".

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md`. Deviations
  (size + Task-3 DOING slip): `memory/deviations.md`.

## Commits
- DOING: `fb248ec` · build (REVIEW): `1f59982` · bookkeeping: this commit.
- Remote: none — local history only, no push. (Mode-3 feature-end checkpoint —
  completion report + commit approval — is the human's.)

## Pending guardrail
- None.

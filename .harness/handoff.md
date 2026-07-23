# Handoff — F3 Task 3 built (REVIEW); next: fresh-eyes verify

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: implement — Task 3 built, now `REVIEW`; Tasks 1–2 DONE; Task 4 `TODO`
- Mode: **Mode 3**

## ⚠ Process deviation this task (please read)
- I **skipped the standalone committed `DOING` checkpoint** for Task 3. Its
  `plan.md` state moved TODO → REVIEW inside the single build commit (`e020198`)
  instead of a committed DOING before building (implement skill step 3 / BUILD
  gate). The build is intact and the diff base is unambiguous, but the
  crash-safety marker is missing. I did NOT rewrite history to fake a DOING
  commit. Logged in `memory/deviations.md` (entry F3-T3). Verifier: please weigh
  this — the code diff itself is a normal single-commit change.

## Changed (Task 3 — Booth voiceprint chrome)
- `src/voicelock/ui/index.html` only:
  - New `.voiceprint` panel in the booth: "VOICEPRINT · LIVE MATCH" header, a
    numeric **distance** readout, a decorative **3-band meter** (accept green /
    borderline amber / reject red) with a needle, a **Set reference** button + 3
    take-dots, and a hint line carrying the **"set reference first"** and
    **"need more audio"** edge states.
  - JS **renders only** — `renderDistance`, `setVoiceprintHint`,
    `showNeedMoreAudio`, `showSetReferenceFirst`, `setReferenceProgress`,
    `showReferenceReady` exposed on `window.voicelockBooth`; `btn-set-reference`
    calls the **stubbed** `set_reference` bridge (wired in Task 4). The match
    band is decided in Python and applied via the readout color — JS never judges.
  - F1 Record/Stop/Play and F2 Enroll/Unlock chrome untouched; no network asset
    refs (offline).

## Measurement disclosure (step-5 exception)
- Ran the Task 3 done-criterion assertion (DOM/asset check) → OK, and
  `uv run ruff check .` → clean, as local sanity. Did NOT run the full
  `uv run pytest` as the Gate — reserved for fresh eyes. No test asserts on the
  HTML DOM (booth tests exercise the Python API), so the suite is unaffected.

## Next action
1. **Fresh-eyes verify** Task 3 (clean context — subagent via
   `formats/VERIFIER-PROMPT.md` verbatim, or a fresh session).
   - Gate base..head: **`e47c8b6..e020198`** (Task 2 wrap-up commit .. Task 3
     build commit; there is NO separate DOING commit — see the deviation above.
     A bookkeeping commit for this handoff is one ahead of the build commit).
   - Task 3 done-criteria (`plan.md`): the `index.html` DOM/asset assertion → 0;
     `uv run ruff check .` → 0; `uv run pytest` → 0.
2. On APPROVE → wrap-up marks Task 3 DONE, then (Mode 3) chain to `/implement`
   Task 4 (the feature's LAST task → done-criterion is the FULL spec §5
   Verification incl. the human-attested manual Booth demo). **(curate due)**

## Watch-outs for Task 4
- **Runtime packaging:** wheel `force-include` ships only `ui/index.html`; the
  `models/ecapa/` dir must be force-included (or the project installed editable)
  so `uv run voicelock` finds the model at runtime.
- Bridge methods to add on `BoothApi` (`app.py`): `set_reference` (capture 3
  takes via the F1 mic path → `voiceprint.set_reference` at the injectable ref
  path) and a live `compare` returning `(distance, band)`; wire them to the
  Task-3 JS hooks (`renderDistance`, `showNeedMoreAudio`, `showReferenceReady`,
  `showSetReferenceFirst`). Bridge tests use a temp ref path (no real mic).
- Task 4 is the LAST task: its done-criterion is the FULL spec §5 Verification,
  including the **required human-attested manual Booth demo** (real mic, real
  same-vs-different speaker separating into accept vs reject).

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md`. Deviations (size +
  the Task-3 DOING slip): `memory/deviations.md`.

## Commits
- Build (Task 3 REVIEW): `e020198` (base `e47c8b6`) · bookkeeping: this commit.
- Remote: none — local history only, no push.

## Pending guardrail
- None. (But see the deviation note — a repeat of the DOING-skip would be a
  candidate for a project.md process guardrail.)

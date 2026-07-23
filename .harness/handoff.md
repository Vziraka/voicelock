# Handoff — F3 Task 3 DONE; next: /implement Task 4 (bridge + end-to-end + manual demo)

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: Task 3 DONE (Gate PASS + Reviewer APPROVE, subagent path); Tasks 1–2 DONE;
  Task 4 `TODO` (the feature's LAST task)
- Mode: **Mode 3**

## Changed (Task 3 — Booth voiceprint chrome)
- `src/voicelock/ui/index.html` only: `.voiceprint` panel (distance readout,
  3-band meter + needle, Set reference button + take-dots, "set reference first"
  / "need more audio" edge states). JS renders only; hooks on
  `window.voicelockBooth` (`renderDistance`, `showNeedMoreAudio`,
  `showSetReferenceFirst`, `setReferenceProgress`, `showReferenceReady`);
  `btn-set-reference` calls the stubbed `set_reference` bridge. F1/F2 untouched.
- Verdict: `memory/verdicts/2026-07-22-F3-T3.json` (APPROVE, lesson none).

## Failed + lesson
- No build failures. Process slip: skipped the standalone committed `DOING` for
  Task 3 (state TODO→REVIEW inside build commit `e020198`); disclosed, logged in
  `memory/deviations.md` (F3-T3), and the verifier judged it a non-defect. Learn
  scan: no new guardrail — it overlaps the existing universal BUILD-gate rule; a
  repeat will be caught by `curate` via the deviation log. **Discipline reminder
  for Task 4: commit the DOING state as its own commit before editing code.**

## next_action
- `/implement` **Task 4** — bridge + end-to-end + manual Booth demo. This is the
  feature's LAST task, so its done-criterion is the FULL spec §5 Verification
  (standing + feature-specific + the human-attested manual demo). **(curate due — 12 verdicts)**
- Add to `BoothApi` in `src/voicelock/app.py`:
  - `set_reference` — capture 3 takes via the F1 mic path → `voiceprint.set_reference`
    at the injectable ref path (default `~/.voicelock/voiceprint.ref`). Surface
    "need more audio" for a short/silent take (re-record that take only).
  - a live `compare` → `voiceprint.compare(live)` → return `{distance, band}` to
    the meter; surface "set reference first" when no reference exists.
  - Wire these to the Task-3 JS hooks (`renderDistance`, `showNeedMoreAudio`,
    `showReferenceReady`, `showSetReferenceFirst`). Enroll/Unlock + Record/Stop/Play
    stay unchanged.
- `tests/test_booth_api.py` — extend with the new bridge methods using a **temp
  ref path** (no real mic in the Gate; follow the existing injectable-path +
  fake-stream patterns).

## ⚠ Watch-out that WILL bite Task 4 (runtime packaging)
- The wheel `force-include` in `pyproject.toml` currently ships only
  `ui/index.html`. When the bridge loads the model at runtime from the installed
  package, `src/voicelock/models/ecapa/` must ALSO be force-included, **or** the
  project installed editable, or `uv run voicelock` won't find the vendored model
  and the manual demo will fail. The engine resolves the model via
  `Path(__file__).parent / "models" / "ecapa"`, so an editable/development install
  already works; a packaged wheel needs the force-include. Confirm which install
  `uv run voicelock` uses and fix packaging if needed (that is in Task-4 scope —
  the manual demo is a done-criterion).

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md`. Deviations (size + the
  Task-3 DOING slip): `memory/deviations.md`. Cutoffs/offline-load notes:
  `voiceprint.py` + Task-2 build-notes in `plan.md`.

## Commits
- Build (Task 3 REVIEW): `e020198` (base `e47c8b6`) · bookkeeping: `581a8e4` ·
  wrap-up: this commit.
- Remote: none — local history only, no push.

## Pending guardrail
- None written. (Repeat of the DOING-skip → curate will surface it from the
  deviation log.)

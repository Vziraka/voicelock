# Handoff — F3 Task 2 DONE; next: /implement Task 3 (Booth chrome)

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: Task 2 DONE (Gate PASS + Reviewer APPROVE, subagent path); Task 1 DONE;
  Tasks 3–4 `TODO`
- Mode: **Mode 3**

## Changed (Task 2 — voiceprint engine + fixtures + tests)
- `src/voicelock/voiceprint.py`: `embed` (offline vendored ECAPA), `set_reference`
  (L2-avg of 3 takes, reject short/silent, injectable persist path), `cosine_distance`,
  `compare` → (distance, band) with pinned `ACCEPT_CUTOFF=0.45` / `REJECT_CUTOFF=0.65`,
  `load_reference`/`NoReferenceError`, `load_wav`. Offline load = `pretrained_path`
  override + `LocalStrategy.NO_LINK` under `HF_HUB_OFFLINE=1`.
- `tests/test_voiceprint.py` (spec §5 cases 1–5, 9 tests) + `tests/fixtures/voiceprint/*`
  (model-repo Apache-2.0 example clips) + `.gitignore` exception for the fixtures.
- Verdict: `memory/verdicts/2026-07-22-F3-T2.json` (APPROVE, lesson none).

## Failed + lesson
- No failures. Build friction: SpeechBrain's default fetch symlinks the vendored
  files into savedir → Windows WinError 1314; solved with `NO_LINK` + a
  `pretrained_path` override so the pretrainer reads ckpts from the local dir.
  Learn scan: no guardrail — the fix is encapsulated in `_load_classifier` (F4
  reuses it; F6 is a different stack), so it will not recur.

## next_action
- `/implement` **Task 3** — Booth chrome (`src/voicelock/ui/index.html`): a
  **Set reference** control (records 3 sentences) + a live **3-band meter**
  (green/amber/red) with a numeric **distance** readout, plus visible
  "need more audio" and "set reference first" states. **JS renders only** — no
  embedding math in JS; it calls the bridge (stubbed until Task 4). Keep
  Record/Stop/Play and F2 Enroll/Unlock unchanged. No network font/asset refs.
  Mode 3: standing go. **(curate due — 11 verdicts)**

## Watch-outs still open (Task 4)
- **Runtime packaging:** wheel `force-include` ships only `ui/index.html`; the
  `models/ecapa/` dir must be force-included (or the project installed editable)
  so `uv run voicelock` finds the model at runtime. Tests use the source-tree
  path, so they pass regardless.
- Task 3 done-criterion is a DOM/asset assertion on `index.html` (see `plan.md`);
  the live bridge + real model wiring + manual Booth demo are Task 4.

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md`. Size deviation
  (~85 MB model): `memory/deviations.md`.

## Commits
- DOING: `c6a1176` · build (REVIEW): `ab8b4c0` · bookkeeping: `3960847`
- Remote: none — local history only, no push.

## Pending guardrail
- None.

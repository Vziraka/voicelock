# Handoff — F3 Task 1 DONE; next: /implement Task 2 (voiceprint engine + tests)

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: Task 1 DONE (Gate PASS + Reviewer APPROVE, subagent path); Tasks 2–4 `TODO`
- Mode: **Mode 3**

## Changed (Task 1 — ECAPA deps + vendor model offline)
- `pyproject.toml` + `uv.lock`: added `speechbrain`, `torch`, `torchaudio` (CPU
  builds: torch 2.13.0+cpu, torchaudio 2.11.0+cpu, speechbrain 1.1.0) via `uv add`.
- `src/voicelock/models/ecapa/`: vendored official SpeechBrain
  `spkrec-ecapa-voxceleb` (Apache-2.0, rev `0f99f2d0…`) — `hyperparams.yaml`,
  `embedding_model.ckpt`, `mean_var_norm_emb.ckpt`, `classifier.ckpt`,
  `label_encoder.txt`, `config.json` + `LICENSE` + `NOTICE`.
- Verdict: `memory/verdicts/2026-07-22-F3-T1.json` (APPROVE, lesson none).

## Failed + lesson
- No failures. Build wrinkle: `uv add` rolled back once when a stale
  `voicelock.exe` (PID 59276) locked the venv; killed it and retried — resolved.
  Learn scan: no lesson met the bar (situational, self-resolved, cheap).

## next_action
- `/implement` **Task 2** — Voiceprint engine (`src/voicelock/voiceprint.py`):
  embed · L2-avg reference (injectable path) · cosine · `ACCEPT/REJECT_CUTOFF`
  3-band · offline load — plus fixtures + `tests/test_voiceprint.py` (spec §5
  cases 1–5). Mode 3: standing go, no further human "go" needed. **(curate due)**

## Watch-outs for Task 2 (from the Task 1 build)
- **Fixtures vs `.gitignore`:** `*.wav`/`*.flac` are gitignored — the audio
  fixtures under `tests/fixtures/voiceprint/` need a gitignore exception or
  `git add -f`, else the Gate fails on a clean checkout.
- **Offline load:** prove `EncoderClassifier.from_hparams` loads from the local
  vendored dir with `HF_HUB_OFFLINE=1` and no network (spec §5 case 5). The
  pretrainer resolves loadables by basename into the source dir — all four
  referenced ckpt/txt files are already vendored.
- **Runtime packaging (Task 4, not 2):** wheel `force-include` currently ships
  only `ui/index.html`; the `models/ecapa/` dir must be force-included or the
  project installed editable for `uv run voicelock` to find the model at runtime.
  Tests can point at the source-tree path directly.

## Where the rest lives
- Task ledger + memory spine: `plan.md`. Full requirements: `spec.md`.
- Size deviation (~85 MB vs spec "~20 MB"): `memory/deviations.md` (human-only
  spec-text fix).

## Commits
- DOING: `d93654f` · build (REVIEW): `2a6f19d` · bookkeeping: `e2596d3`
- Remote: none — local history only, no push.

## Pending guardrail
- None.

## For the human (spec amendment is human-only)
- The spec's "~20 MB" model-size estimate is wrong (actual ~85 MB). Correct the
  `spec.md` §4 / `plan.md` Task 1 wording if you want it accurate — I can't edit
  the spec (amendments are human-only).

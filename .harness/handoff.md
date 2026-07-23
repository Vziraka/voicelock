# Handoff — F3 Task 1 built (REVIEW); next: fresh-eyes verify

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: implement — Task 1 built, now `REVIEW`; Tasks 2–4 still `TODO`
- Mode: **Mode 3** (spec Approval gate, box 2 checked)

## Done this session (Task 1 — ECAPA deps + vendor model offline)
- Entry gate re-checked and PASSED: §2 `**Status: CLEAR**`; token scan for
  `[NEEDS-CLARIFICATION:` → zero hits; approval boxes 1 & 2 `[x]`; `Mode: Mode 3`.
  No `DONE`-without-verdict tasks in `plan.md`.
- Committed `DOING` (`d93654f`) BEFORE building — the Gate's diff base.
- Added `speechbrain`, `torch`, `torchaudio` via `uv add` (no bare pip;
  human-approved TECH-PICK). Resolved to CPU builds: torch 2.13.0+cpu,
  torchaudio 2.11.0+cpu, speechbrain 1.1.0. `pyproject.toml` + `uv.lock` updated.
  Import check `import speechbrain, torch, torchaudio` → ok.
- Vendored the official SpeechBrain `spkrec-ecapa-voxceleb` model (Apache-2.0,
  verified from the model card `license: apache-2.0`), pinned to revision
  `0f99f2d0ebe89ac095bcc5903c4dd8f72b367286`, at `src/voicelock/models/ecapa/`:
  `hyperparams.yaml`, `embedding_model.ckpt`, `mean_var_norm_emb.ckpt`,
  `classifier.ckpt`, `label_encoder.txt`, `config.json` — the files the official
  hyperparams pretrainer loads. Added `LICENSE` (Apache-2.0 text) + `NOTICE`
  (provenance). Removed the `.cache/` metadata `snapshot_download` left behind.
- Quick local checks (not the Gate): `uv run ruff check .` → All checks passed;
  vendored-dir criterion assertion → OK.

## Measurement disclosure (step-5 exception)
- I ran only `ruff check .` and the vendored-dir existence assertion as local
  sanity. I did NOT run `uv run pytest` or the deps `uv sync`/import as the
  authoritative Gate — those stay reserved for fresh eyes. (The import check I
  ran was a build sanity, not the graded Gate run.)

## Flag for the human (spec amendment is human-only)
- **Size:** the vendored model is **~85 MB** (`embedding_model.ckpt` = 83 MB),
  ~4× the spec's "~20 MB" estimate (`spec.md` §4 / `plan.md` Task 1 notes). The
  actionable constraints hold (committed, plain git, no LFS, offline). Logged in
  `memory/deviations.md`. If you want the spec's "~20 MB" text corrected, that is
  a human-only spec edit.

## Next action
1. **Fresh-eyes verify** Task 1 (clean context — subagent via
   `formats/VERIFIER-PROMPT.md` verbatim, or a fresh session).
   - Gate base..head: **`d93654f..2a6f19d`**  (DOING commit .. build commit;
     bookkeeping commit for this handoff is one ahead of the build commit).
   - Task 1 done-criteria (from `plan.md`): `uv sync` → 0; deps import → 0;
     vendored-dir + LICENSE/NOTICE assertion → 0; `uv run ruff check .` → 0;
     `uv run pytest` → 0 (existing suite still green).
2. On APPROVE → wrap-up writes the verdict + marks Task 1 DONE, then (Mode 3)
   chain to `/implement` Task 2.

## Watch-outs for later tasks (not Task 1's scope — do NOT act now)
- **Task 2 fixtures:** `.gitignore` excludes `*.wav` and `*.flac`. The audio
  fixtures under `tests/fixtures/voiceprint/` will need a gitignore exception or
  `git add -f`, or they won't be committed and the Gate will fail on a clean
  checkout.
- **Runtime packaging:** the wheel `force-include` currently ships only
  `ui/index.html`. When Task 2/4 loads the model at runtime from the installed
  package, the `models/ecapa/` dir must either be force-included in the wheel or
  the project installed editable — otherwise `uv run voicelock` won't find the
  vendored files. (Tests can point at the source-tree path directly.)
- **Offline load:** Task 2 must prove `EncoderClassifier.from_hparams` loads
  from the local vendored dir with `HF_HUB_OFFLINE=1` and makes no network call
  (spec §5 case 5). The pretrainer resolves loadables by basename into the
  source dir, which is why all four referenced ckpt/txt files were vendored.
- I killed a leftover `voicelock.exe` (PID 59276) that was locking the venv
  during `uv add` — it was a stale Booth window; relaunch with `uv run voicelock`
  if you need it.

## Commit checkpoint
- Base (DOING): `d93654f`
- Build (Task 1 REVIEW): `2a6f19d`
- Bookkeeping (this handoff): one commit after `2a6f19d` (see git log)
- Remote: none — local history only, no push

## Pending
- None blocking. Task 1 is REVIEW, awaiting the fresh-eyes Gate + Reviewer.

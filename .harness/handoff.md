# Handoff — F3 Task 2 built (REVIEW); next: fresh-eyes verify

## Session
- Date: 2026-07-22
- Feature: F3 — Voiceprint on screen (`spec.md`)
- Phase: implement — Task 2 built, now `REVIEW`; Task 1 DONE; Tasks 3–4 `TODO`
- Mode: **Mode 3**

## Changed (Task 2 — voiceprint engine + fixtures + tests)
- `src/voicelock/voiceprint.py` (new engine, Python owns DSP):
  - `embed(audio, sr)` → L2-normalized ECAPA embedding; raises `NeedMoreAudioError`
    if the clip is < `MIN_SPEECH_SECONDS` (0.4 s) or near-silent (`MIN_RMS`).
  - `set_reference(takes, path=)` → embeds exactly 3 takes, re-normalizes the
    mean, persists to an **injectable** path (default `~/.voicelock/voiceprint.ref`,
    plaintext `np.save`, not the vault). A short/silent take raises before any
    save, so it is never averaged in.
  - `cosine_distance`, `band_for`, `compare(live, path=)` → `(distance, band)`.
  - `ACCEPT_CUTOFF=0.45` / `REJECT_CUTOFF=0.65` pinned module constants (the
    single source tests + app import). `load_reference` raises `NoReferenceError`;
    `load_wav` decodes offline via soundfile.
  - Offline model load: `EncoderClassifier.from_hparams(source=<vendored>,
    overrides={"pretrained_path": <vendored>}, local_strategy=NO_LINK)` with
    `HF_HUB_OFFLINE=1`; cached module-level. NO_LINK avoids the Windows symlink
    privilege error; the pretrained_path override makes the pretrainer read the
    ckpts from the local dir instead of the HF repo id.
- `tests/test_voiceprint.py` — spec §5 cases (1)-(5) + band-boundary test. 9 tests.
- `tests/fixtures/voiceprint/*.wav` + `README.md` — fixed fixtures from the model
  repo's Apache-2.0 example clips (example1→speaker A split into 3 take-thirds +
  a central live window; example2→speaker B; `too_short.wav` = 0.15 s of A).
- `.gitignore` — added `!tests/fixtures/voiceprint/*.wav` so fixtures commit
  despite the blanket `*.wav` ignore.

## Cutoff derivation (empirical, pinned)
- Measured with the vendored model on the fixtures: same-speaker distances
  0.17–0.29 (cluster max ~0.29), different-speaker (B) ~0.83. Cutoffs chosen in
  the gap with margin: accept ≤ 0.45, reject ≥ 0.65, borderline between. ECAPA
  eval inference is deterministic, so the assertions are stable.

## Measurement disclosure (step-5 exception)
- I ran `uv run ruff check .` (clean) and `uv run pytest tests/test_voiceprint.py -q`
  (9 passed, 4.28 s) locally — the cutoff pinning is a measurement, so I confirmed
  it. I did **not** run the full `uv run pytest` as the authoritative Gate; that
  and the feature-specific command stay reserved for fresh eyes.

## Next action
1. **Fresh-eyes verify** Task 2 (clean context — subagent via
   `formats/VERIFIER-PROMPT.md` verbatim, or a fresh session).
   - Gate base..head: **`c6a1176..ab8b4c0`** (DOING .. build; a bookkeeping
     commit for this handoff is one ahead of the build commit).
   - Task 2 done-criteria (`plan.md`): `uv run pytest tests/test_voiceprint.py -q`
     → 0 (spec §5 cases 1–5); `uv run ruff check .` → 0; `uv run pytest` → 0.
   - Note: first `pytest` run loads torch + ECAPA (offline) — budget is the
     10-minute default; observed suite is fast.
2. On APPROVE → wrap-up marks Task 2 DONE, then (Mode 3) chain to `/implement`
   Task 3 (Booth chrome). **(curate due — 10 verdicts as of Task 1)**

## Watch-outs still open for Tasks 3–4
- **Runtime packaging (Task 4):** wheel `force-include` ships only
  `ui/index.html`; the `models/ecapa/` dir must be force-included (or the project
  installed editable) so `uv run voicelock` finds the model at runtime. Tests use
  the source-tree path directly, so they pass regardless.

## Where the rest lives
- Task ledger + spine: `plan.md`. Requirements: `spec.md`. Size deviation
  (~85 MB model): `memory/deviations.md`.

## Commits
- DOING: `c6a1176` · build (REVIEW): `ab8b4c0` · bookkeeping: this commit.
- Remote: none — local history only, no push.

## Pending guardrail
- None.

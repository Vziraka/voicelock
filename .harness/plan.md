# Plan — F3 — Voiceprint on screen

## Active context
- Updated: 2026-07-23
- Spec: `spec.md` · Feature: Feature 3 from `roadmap.md` · Mode: Mode 3 · Phase: implementing
  (Amendment approved 2026-07-23. Tasks 1–4 DONE; Task 5 DOING — Reset control,
  the LAST task; its done = FULL amended §5 incl. the human-attested manual demo.)
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only when the Gate exited 0 **and** the Reviewer approved.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — Add ECAPA dependency stack + vendor the model offline
  - state: DONE
  - rejects: 0
  - files: `pyproject.toml`, `uv.lock`, `src/voicelock/models/ecapa/` (vendored model files + `LICENSE`/`NOTICE`)
  - notes: Human-approved TECH-PICK — SpeechBrain ECAPA-TDNN (`spkrec-ecapa-voxceleb`),
    Apache-2.0 (redistribution OK). Add `speechbrain`, `torch`, `torchaudio` via
    `uv add` (no bare pip). One-time build-time action: download the official
    model files once and commit them (~20 MB, plain git, no LFS) into
    `src/voicelock/models/ecapa/` with LICENSE/NOTICE retained. This is the only
    step that touches the network, and it is a developer action at build time —
    the app and Gate stay offline (`HF_HUB_OFFLINE=1`, local path). Full offline
    model-load is proven by Task 2's tests; here we only prove deps import + the
    vendored files are present.
  - done-criteria:
    - `uv sync` → exit 0
    - `uv run python -c "import speechbrain, torch, torchaudio; print('ok')"` → exit 0
    - `uv run python -c "import pathlib; d = pathlib.Path('src/voicelock/models/ecapa'); assert d.is_dir(); assert any(d.iterdir()), 'model dir empty'; assert (d / 'LICENSE').exists() or (d / 'NOTICE').exists(), 'license/notice missing'"` → exit 0
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed — existing suite still green)
  - feedback: (none)

- [x] **Task 2** — Voiceprint engine (embed · average · cosine · 3-band cutoffs · persist) + fixtures + tests
  - state: DONE
  - rejects: 0
  - build-notes: Cutoffs pinned `ACCEPT_CUTOFF=0.45` / `REJECT_CUTOFF=0.65` from measured fixture distances (same-speaker max ~0.29, different ~0.83). Fixtures = model-repo example clips (Apache-2.0, rev 0f99f2d): example1→speaker A (3 take-thirds + central live window), example2→speaker B; too_short = 0.15s of A. Offline load via `overrides={pretrained_path: <vendored dir>}` + `LocalStrategy.NO_LINK` (Windows symlink blocked). `.gitignore` given a `!tests/fixtures/voiceprint/*.wav` exception so fixtures commit.
  - files: `src/voicelock/voiceprint.py`, `tests/test_voiceprint.py`, `tests/fixtures/voiceprint/` (fixed audio fixtures)
  - notes: Engine owns all voiceprint DSP; JS never computes. Functions: `embed(audio)`
    → ECAPA embedding loaded from the **vendored** local path with `HF_HUB_OFFLINE=1`
    (no network); `set_reference([take1, take2, take3])` → mean of the three
    **L2-normalized** per-utterance embeddings, re-normalized, with a too-short/silent
    take rejected via a "need more audio" signal (that take only, not averaged in);
    persist/load the averaged vector to `~/.voicelock/voiceprint.ref` (plaintext
    sibling file, **not** in the vault; **injectable `path=` for tests** like F2's
    vault); `cosine_distance(a, b)`; `compare(live)` → (distance, band) using
    module-level `ACCEPT_CUTOFF` / `REJECT_CUTOFF` constants → accept (green) /
    borderline (amber) / reject (red); a no-reference-file path surfaces a
    set-reference-first signal (no crash). Cutoffs are **tuned empirically on the
    fixtures during build** and pinned as those module constants (the single source
    the test imports — deterministic, not judgment). Fixtures: commit short WAVs —
    ≥2 same-speaker utterances and ≥1 different-speaker utterance — decoded offline
    (torchaudio/soundfile). Fixture sourcing is a build decision; record the choice
    in the task notes at build time. Spec §5's `test_voiceprint.py` cases (1)–(5)
    are fully implemented here; the Booth/manual surface is Tasks 3–4.
  - done-criteria:
    - `uv run pytest tests/test_voiceprint.py -q` → exit 0; final summary reports 0 failed. Covers, on fixed fixtures + the vendored ECAPA model loaded fully offline (`HF_HUB_OFFLINE`, no network): (1) same-speaker fixtures → cosine distance ≤ `ACCEPT_CUTOFF` (accept band); (2) different-speaker fixtures → cosine distance ≥ `REJECT_CUTOFF` (reject band), the test importing the same cutoff constants the app uses; (3) `set_reference` averages 3 per-utterance embeddings into one L2-normalized vector, and a too-short/silent take is rejected with the "need more audio" signal (not averaged in); (4) with no reference file present, the compare path surfaces a set-reference-first signal (no crash); (5) the model loads from the vendored local path with no network call.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed — full suite still green)
  - feedback: (none)

- [x] **Task 3** — Booth chrome: "Set reference" action + live 3-band meter + distance readout (DOM + JS render only)
  - state: DONE
  - rejects: 0
  - build-notes: Added `.voiceprint` panel to `ui/index.html` — VOICEPRINT·LIVE MATCH header + numeric `distance` readout, a decorative 3-band meter (green/amber/red) with a needle, a **Set reference** button + 3 take-dots, and a hint line carrying the "set reference first" / "need more audio" edge states. JS renders only (no embedding math): `renderDistance`, `showNeedMoreAudio`, `showSetReferenceFirst`, `setReferenceProgress`, `showReferenceReady` exposed on `window.voicelockBooth`; `btn-set-reference` calls the stubbed `set_reference` bridge (wired in Task 4). F1/F2 controls untouched; no network asset refs. Match band decided in Python, applied via readout color — JS never judges.
  - files: `src/voicelock/ui/index.html`
  - notes: Reuse the existing mock chrome. Add a **Set reference** control (records
    3 sentences) and a live **3-band meter** (green/amber/red) with a numeric
    distance readout, plus the visible edge states: "need more audio" and
    "set reference first". JS **renders only** — no embedding math in JS; it calls
    the bridge (stubbed until Task 4). Keep Record/Stop/Play and F2 Enroll/Unlock
    unchanged. No network font/asset refs (offline). Mirrors F2's Task 3
    (DOM-hooks-only) shape.
  - done-criteria:
    - `uv run python -c "from pathlib import Path; t = Path('src/voicelock/ui/index.html').read_text(encoding='utf-8').lower(); assert 'set reference' in t or 'set-reference' in t; assert 'meter' in t or 'band' in t; assert 'distance' in t; assert 'need more audio' in t; assert 'set reference first' in t or 'no reference' in t; assert 'record' in t and 'unlock' in t; assert 'fonts.googleapis.com' not in t; assert 'fonts.gstatic.com' not in t"` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [x] **Task 4** — Bridge Set-reference + live compare to the engine; `uv run voicelock` end-to-end
  - state: DONE
  - rejects: 0
  - verify: 2026-07-22 verifier (subagent) → GATE automated all exit 0 (`ruff`; `pytest` 33 passed; `test_voiceprint` 9 passed); REVIEW both axes APPROVE; overall ESCALATE_HUMAN on the manual demo only. The 2026-07-23 Reset amendment moved the FULL-§5 manual demo to **Task 5** (new last task), so Task 4 is now **intermediate** and closed DONE on its passed automated criteria (verdict `memory/verdicts/2026-07-22-F3-T4.json`, APPROVE). Human approved this closure path 2026-07-23.
  - build-notes: `BoothApi` gained injectable `ref_path` + `set_reference` (banks the last captured take; validates via `voiceprint.embed`, rejects short/silent with `need_more_audio`, averages+persists on the 3rd via `voiceprint.set_reference`) and `compare` (→ `{distance, band}`; `no_reference`/`need_more_audio` errors). JS: Set-reference handler handles progressive `{progress,done}`; `updateVoiceprintMeter` runs after each Stop (record branch) → `renderDistance` / `showSetReferenceFirst` / `showNeedMoreAudio`. Enroll/Unlock + Record/Stop/Play unchanged. `tests/test_booth_api.py` +3 (stub capture + real fixtures): same→accept, different→reject, short-take rejected, no-reference. Packaging: `uv run voicelock` uses the EDITABLE install (resolves to `src/voicelock/`), so the vendored `models/ecapa/` is found at runtime — no wheel force-include needed for the demo (noted for any future wheel build).
  - files: `src/voicelock/app.py`, `src/voicelock/ui/index.html`, `tests/test_booth_api.py`
  - notes: Add `BoothApi` methods that call the Task-2 engine: `set_reference`
    (captures 3 takes via the F1 mic path → averaged reference at the injectable
    ref path, default `~/.voicelock/voiceprint.ref`) and a live `compare` that
    returns distance + band to the meter. Wire the Task-3 JS to these calls;
    surface "need more audio" and "set reference first" states. Enroll/Unlock and
    Record/Stop/Play stay unchanged. Bridge tests use a temp ref path (no real mic
    in the Gate). This is the feature's LAST task — its done-criterion is the FULL
    Verification list from `spec.md` (standing + feature-specific + the required
    manual Booth demo line).
  - done-criteria: (was the FULL §5 when T4 was the last task) — the automated
    subset ran green in verification (`ruff`; `pytest` 33 passed; `test_voiceprint`
    9 passed); the FULL-§5 manual demo moved to Task 5 by the 2026-07-23 amendment.
  - feedback: (none)

- [ ] **Task 5** — Reset control: clear the stored reference + restart the 3-take flow (LAST task, F3 amendment 2026-07-23)
  - state: DOING
  - rejects: 0
  - files: `src/voicelock/app.py`, `src/voicelock/ui/index.html`, `tests/test_booth_api.py`
  - notes: Add a `BoothApi.reset_reference()` bridge method that **deletes**
    `~/.voicelock/voiceprint.ref` (the injectable `ref_path`; no-op if absent)
    **and** clears any in-progress `_reference_takes`, returning `{ok: true}`.
    Add a **Reset** button to the `.voiceprint` panel in `ui/index.html` that
    calls it and renders the reset state (`showSetReferenceFirst` + empty the
    3 take-dots via `setReferenceProgress(0)`). **No confirm prompt.** Python
    owns the clear; JS renders only. Keep Set reference / Record/Stop/Play /
    Enroll/Unlock unchanged. This is the feature's LAST task — its done-criterion
    is the FULL `spec.md` **Verification** list (incl. the reset automated test +
    the human-attested manual demo, now with the reset step).
  - done-criteria: FULL list from `spec.md` **Verification** section (amended):
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed)
    - `uv run pytest tests/test_voiceprint.py -q` → exit 0 (spec §5 cases 1–5)
    - `uv run pytest tests/test_booth_api.py -q` → exit 0; must cover: after a
      reference is set, `reset_reference` clears it so a subsequent `compare`
      surfaces `no_reference` again and the ref file no longer exists.
    - **Manual (required, human-attested):** `uv run voicelock` → Set reference
      (3 sentences) → same person → **accept (green)** → different person →
      **reject (red)** → **Reset** → meter returns to "set reference first" and a
      fresh reference can be set again.
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-23 — F3 Tasks 1–4 DONE (Mode 3). T1 deps+model · T2 engine+tests · T3 chrome · T4 bridge+end-to-end. T4 closed as intermediate on its passed automated verification (verifier: ruff/pytest 33/test_voiceprint 9 all 0, both Review axes APPROVE).
2. Amendment approved 2026-07-23: added a **Reset** control. Task 5 (Reset) is the new LAST task — `BoothApi.reset_reference` (delete injectable `ref_path` + clear in-progress takes) + a Reset button (JS renders reset state) + a `test_booth_api` reset test. No confirm prompt.
3. NEXT: `/implement` Task 5 (commit DOING first). Its done = FULL amended §5 incl. the human-attested manual demo (set reference · same→accept · different→reject · reset).
4. Diagnostic only — no lock/key derivation (F4). Reference = 3-take averaged ECAPA vector at `~/.voicelock/voiceprint.ref` (plaintext, injectable, not the vault). Cutoffs `ACCEPT=0.45`/`REJECT=0.65`. Offline load = `pretrained_path` override + `NO_LINK`.
5. `uv run voicelock` is an EDITABLE install → vendored `models/ecapa/` resolves at runtime (no wheel force-include needed for the demo). Roadmap F11 parked (manage enrollment from inside the vault, post-F7).

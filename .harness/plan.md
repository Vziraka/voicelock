# Plan — F3 — Voiceprint on screen

## Active context
- Updated: 2026-07-22
- Spec: `spec.md` · Feature: Feature 3 from `roadmap.md` · Mode: Mode 3 · Phase: implementing
  (Tasks 1–2 DONE — Gate PASS + Reviewer APPROVE; next: `/implement` Task 3; Task 4 TODO)
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

- [ ] **Task 3** — Booth chrome: "Set reference" action + live 3-band meter + distance readout (DOM + JS render only)
  - state: TODO
  - rejects: 0
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

- [ ] **Task 4** — Bridge Set-reference + live compare to the engine; `uv run voicelock` end-to-end + manual Booth demo
  - state: TODO
  - rejects: 0
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
  - done-criteria: FULL list from `spec.md` **Verification** section:
    - `uv run ruff check .` → exit 0 (no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
    - `uv run pytest tests/test_voiceprint.py -q` → exit 0; final summary reports 0 failed (spec §5 cases 1–5)
    - **Manual (required, human-attested):** run `uv run voicelock` → **Set reference** and speak 3 sentences to store a reference → the same person reads a sentence → live meter shows a small distance / **accept (green)** → a **different** person reads → meter shows a large distance / **reject (red)**. Observable: real-mic Set reference works, the live 3-band meter updates, and a real same-vs-different speaker separates into accept vs reject.
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-22 — F3 Tasks 1–2 DONE (Mode 3). T1: ECAPA stack + vendored Apache-2.0 model. T2: `voiceprint.py` engine + fixtures + tests (spec §5 cases 1–5), full suite 30 passed, Reviewer APPROVE.
2. Next: `/implement` Task 3 — Booth chrome in `ui/index.html` (Set-reference control + live 3-band meter + distance readout + edge states); JS renders only, bridge stubbed. Then T4 bridge + end-to-end + manual demo.
3. Diagnostic only — no lock/key derivation (that is F4). Reference = 3-take averaged ECAPA vector at `~/.voicelock/voiceprint.ref` (plaintext sibling, injectable path, not the vault). Cutoffs pinned `ACCEPT=0.45`/`REJECT=0.65` (module constants tests import).
4. Offline load solved: `pretrained_path` override + `LocalStrategy.NO_LINK` under `HF_HUB_OFFLINE` (Windows symlink blocked); encapsulated in `voiceprint._load_classifier`.
5. Open watch-out (Task 4): runtime wheel `force-include` currently only ships `ui/index.html` → `models/ecapa/` must be force-included (or editable install) for `uv run voicelock`.

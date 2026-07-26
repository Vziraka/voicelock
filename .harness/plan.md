# Plan — F4 — Voice as the middle lock (stacked)

## Active context
- Updated: 2026-07-25
- Spec: `spec.md` · Feature: Feature 4 from `roadmap.md` · Mode: Mode 3 · Phase: PLANNED
  (F4 spec APPROVED 2026-07-23 — both boxes checked, Grilling CLEAR, Mode 3.
  Ledger written 2026-07-25; all 5 tasks `TODO`. Next: `/implement` Task 1 —
  the approved Mode 3 is the standing "go", no further human go needed inside
  the feature.)
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only when the Gate exited 0 **and** the Reviewer approved.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [ ] **Task 1** — 5-take speaker-A enrollment fixtures + measured same/different separation
  - state: TODO
  - rejects: 0
  - files: `tests/fixtures/voiceprint/speakerA_enroll1..5.wav`, `tests/fixtures/voiceprint/README.md`
  - notes: F4's enrollment is a **5-sentence averaged capture** (spec §4 Accuracy
    levers) but the F3 fixture set only has 3 speaker-A takes. Derive **five** new
    fixed WAVs from the SAME committed speaker-A audio (`speakerA_take1/2/3.wav`
    are consecutive thirds of the model repo's `example1.wav`, Apache-2.0 rev
    `0f99f2d`) — reassemble those thirds and cut five ~1.0 s windows (overlap is
    fine and expected; each window must clear `MIN_SPEECH_SECONDS` = 0.4 s and
    `MIN_RMS`). Mono 16 kHz PCM_16, committed via the existing `.gitignore`
    exception (`!tests/fixtures/voiceprint/*.wav`). **Do not touch or rename the
    F3 fixtures** — `test_voiceprint.py` and `test_booth_api.py` still use them.
    Probes stay `speakerA_live.wav` (same speaker) and `speakerB.wav` (impostor).
    Update the fixtures README with the derivation and the honest caveat, carried
    from F3 and re-stated in spec §5: the same-speaker probe **overlaps** the
    enrollment audio, so these fixtures prove the math separates same-vs-different
    — they do **not** prove cross-session generalization (that is what the
    required manual demo covers). This task exists first because Task 2's whole
    tolerance calibration depends on a 5-take enrollment vector existing.
  - done-criteria:
    - `uv run python -c "from pathlib import Path; import numpy as np; from voicelock import voiceprint as vp; d = Path('tests/fixtures/voiceprint'); takes = [vp.load_wav(d / f'speakerA_enroll{i}.wav') for i in range(1, 6)]; assert all(t.size >= int(vp.MIN_SPEECH_SECONDS * vp.SAMPLE_RATE) for t in takes), 'a take is too short'; embs = [vp.embed(t) for t in takes]; ref = np.mean(embs, axis=0); same = vp.cosine_distance(ref, vp.embed(vp.load_wav(d / 'speakerA_live.wav'))); diff = vp.cosine_distance(ref, vp.embed(vp.load_wav(d / 'speakerB.wav'))); print('same', same, 'diff', diff); assert same <= vp.ACCEPT_CUTOFF; assert diff >= vp.REJECT_CUTOFF"` → exit 0 (5 takes embed with no "need more audio", their average lands the same speaker in the accept band and the impostor in the reject band)
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed — F3 suite still green on its untouched fixtures)
  - feedback: (none)

- [ ] **Task 2** — `middlelock.py`: LSH binarize + reliability mask + repetition ECC + commit/reconcile + key derive
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/middlelock.py`, `tests/test_middlelock.py`
  - notes: The spec's keystone (§4), hand-rolled in **pure numpy — NO new
    dependency**. Code-offset fuzzy commitment (Juels–Wattenberg), Python-owned:
    `commit(enrollment_embeddings) -> (secret, helper_data)` — seeded
    random-hyperplane **LSH** projection of the L2-normalized 192-dim ECAPA
    average to ~512 bits (seed = non-secret helper), a **reliability mask** keeping
    the largest-margin / most-stable bits across the 5 takes (mask = non-secret
    helper), a random secret `s` encoded by a **repetition/majority-vote** inner
    code to codeword `c`, helper `P = b XOR c`, plus `H(s)`;
    `reconcile(helper_data, live_embedding) -> secret` — recompute `b'`, apply the
    mask, `b' XOR P`, majority-decode, verify `H(s)`, else raise `ReconcileError`;
    `derive_key(secret, salt) -> 32 bytes` for a PyNaCl SecretBox (Argon2id or
    HKDF-style stretch per spec §4 — pick one at build time, keep the whole-suite
    runtime inside spec §5's budget, and record the choice + cost params in
    build-notes). Helper data must serialize to JSON-safe values (base64 the byte
    arrays) because Task 3 stores it inside the outer box.
    **Tolerance is pinned empirically here** (spec §4 "Reconcile tolerance"):
    bit count, mask size, repetition factor and correction radius are
    module-level constants the tests import — measure genuine vs impostor bit-error
    on the Task-1 fixtures and pin values that separate them **with a margin**.
    Research (`memory/research/2026-07-23-f4-fuzzy-reconcile.md`) warns raw
    192 sign-bits give ~25 % genuine BER, so masking + expansion are required, not
    optional; if the two clusters will not separate with a margin after a genuine
    tuning attempt, that is a `BLOCKED` report, not a silently loosened radius.
    This task is engine-only — no vault, no bridge, no UI.
  - done-criteria:
    - `uv run pytest tests/test_middlelock.py -q` → exit 0; final summary reports 0 failed. Must cover, on the Task-1 fixtures + the vendored ECAPA model loaded fully offline (`HF_HUB_OFFLINE`, no network): (a) `commit` on the 5-take enrollment returns a secret plus helper data carrying the LSH seed, reliability mask, XOR offset `P` and `H(s)`, all JSON-serializable; (b) the **same-speaker** probe reconciles to the **identical** secret; (c) the **different-speaker** probe raises `ReconcileError` (no secret returned); (d) the tolerance knobs are module-level constants the test **imports** (not literals in the test), and the measured genuine error count sits below the correction radius while the impostor's sits above it — asserted with an explicit margin; (e) `derive_key` returns 32 deterministic bytes for a given (secret, salt) and different bytes for a different secret or salt
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed — full suite still green)
  - feedback: (none)

- [ ] **Task 3** — `vault.py` v2: nested outer(passphrase) → middle(voice) layout + v1 refusal
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/vault.py`, `tests/test_middlelock.py`, `tests/test_vault.py`
  - notes: Bump `FORMAT_VERSION` 1 → 2 and nest, exactly as spec §4 pins:
    innermost plaintext = the profile JSON (`{name, schema_version}`) sealed with
    the **voice-derived middle key** → middle ciphertext; outer plaintext = JSON
    `{helper_data, middle_ciphertext}` sealed with the **passphrase-derived outer
    key** (F2's Argon2id + SecretBox, unchanged); file = `VLCK` + version byte **2**
    + opslimit + memlimit + salt + outer ciphertext. API takes **embeddings, not
    audio** (voiceprint DSP stays in `voiceprint.py`): `enroll(name, passphrase,
    voiceprints, path=None)` where `voiceprints` is the 5 enrollment embeddings, and
    `unlock(passphrase, voiceprint, path=None)` returning the display name. Peel
    order is **outer first, then middle** — a wrong passphrase must raise before
    the voice is ever consulted. New errors beside the existing `AuthError`
    (outer): `VoiceAuthError` (middle — reconcile or middle decrypt failed) and
    `LegacyVaultError` (version byte 1 → re-enroll prompt, **no passphrase-only
    bypass**). Neither reject path returns a name or any plaintext. `enroll`
    always writes v2. Existing `test_vault.py` calls the old two-arg signature —
    update it in this task (that is a required change, not scope creep).
  - done-criteria:
    - `uv run pytest tests/test_middlelock.py -q` → exit 0; final summary reports 0 failed. Adds spec §5's vault cases on a temp vault path: (1) `enroll` binds a middle key from the 5-take averaged enrollment voiceprint, emits helper data (LSH seed + reliability mask + XOR offset `P` + `H(s)`) and seals a nested vault whose raw bytes start with `VLCK` and whose version byte is **2**; (2) same-speaker unlock reconciles → the middle lock opens → the enrolled display name is returned; (3) different-speaker → `VoiceAuthError` (middle REJECT) and **no name/plaintext**; (4) wrong passphrase → `AuthError` (outer REJECT) raised **before** the voice is consulted, and no name; (6) a pre-existing **v1** vault raises `LegacyVaultError` (re-enroll signal, no passphrase-only open); (7) no-leak: the raw v2 file bytes contain neither the reference embedding nor the middle plaintext (helper data sits inside the outer ciphertext)
    - `uv run pytest tests/test_vault.py -q` → exit 0; final summary reports 0 failed (F2's format/validation/no-vault cases still hold on the v2 signature)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [ ] **Task 4** — Bridge: `BoothApi` 5-take voice enroll + voice unlock with distinct reject reasons
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Mirror the proven F3 `set_reference` shape so the stub-capture tests
    keep working: `enroll_take()` banks the last captured buffer as one of the
    **5** enrollment sentences (validate via `voiceprint.embed`; a too-short/silent
    take returns `need_more_audio` and does **not** advance progress), and
    `enroll({name, passphrase, overwrite})` seals the v2 vault from the 5 banked
    takes (keep F2's `needs_confirm` overwrite handshake and the `validation`
    error). `unlock({passphrase})` embeds the last captured take and calls
    `vault.unlock`, mapping errors to **distinct** strings: `auth_outer` (wrong
    passphrase) · `auth_voice` (voice didn't match) · `no_vault` · `legacy_vault`
    (v1) · `need_more_audio`. **No failure path may include a `name`.** Keep the
    F3 diagnostic bridge (`set_reference` / `compare` / `reset_reference`) and
    Record/Stop/Play unchanged; tests use a temp vault path + stub capture, never a
    real mic. Note for build: F2's `unlock` returned `error: "auth"` — that string
    is replaced by `auth_outer`, so update the existing booth test that asserts it.
  - done-criteria:
    - `uv run pytest tests/test_booth_api.py -q` → exit 0; final summary reports 0 failed. Must cover, with a temp vault path + stub capture (no real mic) and the Task-1 fixtures: (a) five `enroll_take()` calls then `enroll` seals a vault whose bytes start with `VLCK` and whose version byte is 2; (b) a too-short take returns `need_more_audio` and leaves progress unchanged; (c) right passphrase + same-speaker take → `ok: True` with the enrolled name; (d) **wrong passphrase** → `ok: False`, `error == "auth_outer"`, and no `name` key; (e) right passphrase + **different speaker** → `ok: False`, `error == "auth_voice"`, and no `name` key — the two reasons are **distinct**; (f) no vault → `no_vault`; (g) a v1 vault file → `legacy_vault`; and the F3 `set_reference`/`compare`/`reset_reference` cases still pass unchanged
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [ ] **Task 5** — Booth UI: enroll voice step + unlock voice step + two distinct rejects (LAST task — FULL §5)
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/ui/index.html` (+ `src/voicelock/app.py` only if wiring gaps surface)
  - notes: Reuse the existing mock chrome (spec §4 Booth UX). Enroll panel gains a
    **voice-capture step**: the 5 suggested sentences shown to read, a per-take
    progress indicator driven by `enroll_take()`, and the "need more audio" hint on
    a rejected take; Enroll stays disabled until 5 valid takes are banked. The
    unlock strip gains a **record-your-utterance** step before Unlock (identity
    only — no challenge phrase; that is F8). Results render **two visibly distinct**
    rejects: "Wrong passphrase" (existing `chip-wrong-pass`, now driven by
    `auth_outer`) and a NEW "Voice didn't match" chip driven by `auth_voice`, plus a
    re-enroll message for `legacy_vault` ("this vault predates voice — re-enroll to
    add the voice lock"). **JS renders only** — no embedding or crypto in JS; every
    decision comes from the bridge. Keep Record/Stop/Play, the F3 voiceprint
    diagnostic panel (meter / Set reference / Reset), and F2's enroll overwrite
    confirm unchanged. No network font/asset refs (offline). This is the feature's
    LAST task — its done-criterion is the FULL `spec.md` **Verification** list,
    including the required human-attested manual demo.
  - done-criteria: FULL list from `spec.md` **Verification** section:
    - `uv run python -c "from pathlib import Path; t = Path('src/voicelock/ui/index.html').read_text(encoding='utf-8').lower(); assert 'voice' in t; assert \"voice didn't match\" in t or 'voice did not match' in t; assert 'wrong passphrase' in t; assert 're-enroll' in t; assert 'need more audio' in t; assert 'record' in t and 'unlock' in t and 'enroll' in t; assert 'set reference' in t or 'set-reference' in t; assert 'fonts.googleapis.com' not in t; assert 'fonts.gstatic.com' not in t"` → exit 0
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
    - `uv run pytest tests/test_middlelock.py -q` → exit 0 (spec §5 cases 1–7)
    - `uv run pytest tests/test_booth_api.py -q` → exit 0 (bridge enroll seals v2; unlock returns distinct `auth_outer` vs `auth_voice`; neither returns the name)
    - **Manual (required for F4 done, human-attested):** `uv run voicelock` →
      **enroll** (name + passphrase + read the 5 sentences) → **unlock** with the
      right passphrase + the enrolled voice → **unlocked** (name shown); **wrong
      passphrase** → **outer REJECT** ("Wrong passphrase"); a **different person**
      speaks with the right passphrase → **middle REJECT** ("Voice didn't match").
      Each reject names its distinct cause. (Observable: real-mic enroll seals a v2
      vault at `~/.voicelock/vault.vl`, the genuine speaker unlocks live on a real
      cross-recording, and the two impostor classes separate visibly.)
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-25 — **F4 planned (Mode 3).** Spec APPROVED 2026-07-23 (both boxes, Grilling CLEAR). 5 tasks `TODO`; next is `/implement` Task 1 — the approved Mode is the standing "go" inside the feature.
2. Build order: fixtures (5-take enrollment) → `middlelock.py` fuzzy commitment → `vault.py` **v2** nesting → `BoothApi` bridge → Booth UI + the required manual demo (LAST task carries the FULL §5).
3. Keystone locked in spec §4: hand-rolled pure-numpy code-offset fuzzy commitment (LSH bit-expansion + reliability mask + repetition ECC), **no new dependency**; helper data lives **inside** the outer passphrase box; v1 vaults are refused with a re-enroll prompt.
4. Main build risk: raw ECAPA sign-bits carry ~25 % genuine bit-error (research 2026-07-23) — Task 2's mask/expansion tuning must separate genuine from impostor **with a margin**, or the task reports `BLOCKED` rather than loosening the radius.
5. Inherited from F3, unchanged: fixture same-speaker probes overlap the enrollment audio, so automation cannot prove cross-session generalization — that gap is exactly what Task 5's required manual demo covers. Open human item from F3: spec's "~20 MB" model-size wording is wrong (actual ~85 MB).

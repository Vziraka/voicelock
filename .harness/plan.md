# Plan — F7 — Face as the inner lock (innermost)

## Active context
- Updated: 2026-07-27
- Feature: Feature 7 from `roadmap.md` · Mode: **Mode 3 — Spec-to-done** ·
  Phase: **Ready to build.** Task 1 is `TODO`, nothing `DOING` yet (WIP=1).
- Spec: `spec.md` holds F7's spec, Grilling `Status: CLEAR` (zero
  `[NEEDS-CLARIFICATION:` hits), both approval boxes checked, `Mode: Mode 3`
  set 2026-07-27 by the human.

### Why this feature exists, in one line
F4's construction (fuzzy commitment → stable key → nested AEAD layer), one
layer deeper, for the face instead of the voice — the vault becomes three
nested locks (passphrase outer, voice middle, face inner) instead of two.

### The dependency that fixes the task order
No new model or fixture vendoring this time (unlike F5/F6) — F7 only touches
code, so the chain is a straight line: **Task 1** (`facelock.py`, the
construction itself) has no dependency on the rest and must land first — Task
2 imports it to seal the vault. **Task 2** (`vault.py` v3) must precede
**Task 3** (the Booth bridge calls both `vault.enroll`/`unlock`'s new
signature and `facelock` for the enroll-face capture step), which must
precede **Task 4** (the UI calls the bridge's new methods and renders the
third reject). WIP=1 makes this the actual build sequence.

### Named architecture decisions carried into this ledger
These fill the "exact call shape" gaps the spec deliberately left to `/plan`
(same role F6's memory-spine item 1 played) — do not re-derive them mid-build.

1. **`facelock.commit()` takes a variable-length list of embeddings (≥1), not
   a fixed exact count.** `middlelock.commit()` hard-asserts
   `len(embeddings) == ENROLLMENT_TAKES` (5) via `_stack_embeddings`. Q1
   requires `facelock.commit()` to work both with **one** fixture take (the
   Gate test, A1 alone) and **three** live frames (production) — a fixed-count
   assert would make one of those two callers impossible. Dropping the exact-
   count check is safe and requires no other code change: `_reliability_mask`'s
   cross-take-unanimity filter is already vacuously true at n=1 (nothing to
   disagree with), which *is* the documented "degrades to pure margin ranking"
   fallback — porting that function unchanged already does the right thing at
   both n=1 and n=3. Only the minimum (≥1, non-empty) is asserted.
2. **New constant `facelock.ENROLLMENT_TAKES = 3`** — the live-production take
   count (Q1: reuse F6's `REFERENCE_TAKES = 3` burst pattern), consumed by
   Task 3's new bridge capture step. Deliberately a **separate** constant from
   `faceprint.REFERENCE_TAKES` (also 3, coincidentally) — they gate two
   independent flows (Q4) and must not be import-aliased into one just because
   the numbers currently match.
3. **New bridge methods, distinctly named from F6's diagnostic ones** (which
   already own `set_face_reference`/`compare_face`/`reset_face_reference`):
   `enroll_face_take()` and `reset_enroll_face_takes()`, mirroring the voice
   pair `enroll_take()`/`reset_enroll_takes()` exactly. These feed only
   `facelock.commit` via `vault.enroll`; they never read or write
   `faceprint.ref`.
4. **`vault.py` signatures gain a face parameter**, mirroring exactly how F4
   added `voiceprints`: `enroll(name, passphrase, voiceprints, faceprints,
   path=None)` and `unlock(passphrase, voiceprint, faceprint, path=None) ->
   str`. New `FaceAuthError` (peer of `VoiceAuthError`) for the inner REJECT.
5. **Vault v3 layout and key names — copied verbatim from spec §2 Q3**, not
   re-decided here: innermost profile JSON → sealed with the face-derived
   inner key → `inner_ciphertext`; middle plaintext becomes
   `{"helper_data_face", "inner_ciphertext"}` → sealed with the voice-derived
   middle key → `middle_ciphertext`; outer plaintext becomes
   `{"helper_data_voice", "middle_ciphertext"}` (renamed from today's bare
   `"helper_data"`, since v3 refuses v2 outright — no format needs to read both
   spellings) → sealed with the passphrase key → `outer_ciphertext`. Version
   bytes: `_PREVOICE_FORMAT_VERSION = 1`, `_PREFACE_FORMAT_VERSION = 2`,
   `FORMAT_VERSION = 3`. Both legacy versions raise `LegacyVaultError`, message
   naming the specific missing layer ("predates voice" for v1, "predates face"
   for v2).
6. **Peel order stays outer → middle → inner.** `unlock()` only reaches the
   face check after the passphrase AND the voice have both already verified —
   a wrong-face impostor never learns whether the passphrase or voice would
   have passed either, and vice versa (already true for outer→middle; F7 just
   extends the chain one layer).

### Memory spine
1. Decisions 1–6 above are the load-bearing ones; nothing else is open.
2. Thin-evidence disclosure (spec Q1/Q2, §6): `CORRECTION_RADIUS` for
   `facelock.py` is measured from n=1 genuine + n=2 impostor residuals (enroll
   A1→reconcile A2; enroll A1 or A2→reconcile B) — Task 1's done-criteria
   assert the measured *relationship* (radius strictly between the genuine
   residual and the impostor floor), not a hard-coded number, so the test
   stays honest about which value the real measurement produced.
3. `middlelock.py`, `voiceprint.py`, `faceprint.py`, `facedetect.py` are
   read-only references for this feature — F7 adds a sibling module and
   extends `vault.py`/`app.py`/`index.html`; it does not edit the four
   read-only ones (spec §3 non-goals).
4. F7 is the last task's full-Verification feature — cmd 4 (the live 3-way
   manual check) is REQUIRED and only the human can attest it, at the
   feature-end checkpoint.

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [ ] **Task 1** — `facelock.py`: face fuzzy commitment (commit/reconcile/derive_key), measured `CORRECTION_RADIUS`
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/facelock.py` (new), `tests/test_facelock.py` (new)
  - notes: Port `middlelock.py`'s shape (decision 1 changes only the
    enrollment-count check — everything else, including
    `_projection_matrix`/`_reliability_mask`/`_soft_decode`/the helper-data
    JSON shape/the commitment-tag pattern, carries over unchanged in spirit,
    reparameterized for `faceprint.EMBEDDING_DIM`-equivalent — SFace emits a
    128-dim feature vector, confirm the exact constant name/value in
    `faceprint.py` before importing it, since `faceprint.py` may not export an
    `EMBEDDING_DIM` the way `voiceprint.py` does; if it doesn't, add one there
    only if truly needed, otherwise inline `128` with a comment citing SFace's
    published output width).
    `CANDIDATE_BITS`/`RELIABLE_BITS`/`KEY_BITS`/`REPETITION` are the literal
    values `4096`/`512`/`32`/`16` (decision: reused unchanged from
    `middlelock`, per spec Q2 — do NOT scale by embedding width). Reuse the
    same Argon2id `_stretch`/`_tag` pattern and `INTERACTIVE` cost (same
    reasoning as `middlelock`: this is the innermost layer, only reached after
    both outer locks already fell). `ENROLLMENT_TAKES = 3` per decision 2.
    **Measuring `CORRECTION_RADIUS`:** in the test module (or a fixture),
    `commit()` on `[embed_file(personA_1.jpg)]`, then `residual_bits()` against
    `embed_file(personA_2.jpg)` (the genuine residual) and against
    `embed_file(personB.jpg)` (one impostor residual); repeat enrolling on A2
    alone and measuring residual against B (the second impostor residual, per
    Q2's n=2). Pick `CORRECTION_RADIUS` as the midpoint of the genuine residual
    and the LOWER of the two impostor residuals (same method F4 used for 110).
    Disclose in the module docstring: n=1 genuine / n=2 impostor, thinner than
    `middlelock`'s 200-commit measurement (spec Q2, §7).
  - done-criteria:
    - §5 cmd 1 — verbatim, exit 0:
      ```
      uv run pytest tests/test_facelock.py -q
      ```
      Must cover (per spec §5 item 1): `commit` binds an inner key + emits
      helper data (LSH seed, reliability mask, XOR offset, commitment tag)
      from an enrollment embedding set — A1 alone in this test; same-person
      reconcile (enroll A1, reconcile A2) recovers the secret; different-
      person reconcile (enroll A1 or A2, reconcile B) raises a
      `ReconcileError`-equivalent, no secret/plaintext returned;
      `CANDIDATE_BITS == 4096`, `RELIABLE_BITS == 512`, `KEY_BITS == 32`,
      `REPETITION == 16`; and `CORRECTION_RADIUS` sits strictly between the
      measured genuine residual and the measured impostor floor — assert the
      actual measured gap (per memory spine item 2), not just that the
      constant exists.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count rises from F6's 145)

- [ ] **Task 2** — `vault.py`: bump to v3, nest the face inner lock, refuse v1 **and** v2
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/vault.py`, `tests/test_vault.py`
  - notes: Apply decisions 4–6 verbatim. `enroll()` gains a `faceprints:
    list[np.ndarray]` parameter (after `voiceprints`, before `path`) and calls
    `facelock.commit` the same way it already calls `middlelock.commit`;
    `unlock()` gains a `faceprint: np.ndarray` parameter (after `voiceprint`,
    before `path`) and, only after the middle box opens, calls
    `facelock.reconcile` against `helper_data_face` and decrypts
    `inner_ciphertext` with the derived inner key — any `FaceLockError`-family
    exception or `CryptoError` there raises `FaceAuthError("Face didn't
    match")`, mirroring exactly how `VoiceAuthError` wraps
    `middlelock.MiddleLockError`/`CryptoError` today. Rename the outer
    plaintext's `"helper_data"` key to `"helper_data_voice"` — safe because v3
    refuses v2 outright, so no code path ever needs to read the old key name.
    `_parse_outer`/`_parse_profile`-equivalent parsing extends one layer
    deeper; keep the "corrupt payload" `VaultError` for malformed JSON at any
    layer, same as today.
  - done-criteria:
    - §5 cmd 2 — verbatim, exit 0:
      ```
      uv run pytest tests/test_vault.py -q
      ```
      Must cover (per spec §5 item 2): enroll seals a v3 vault
      (`FORMAT_VERSION == 3`, `VLCK` magic); unlock with the right passphrase +
      voice + face returns the display name; a wrong passphrase raises before
      voice or face is consulted (outer REJECT, unchanged shape); right
      passphrase + wrong voice raises before face is consulted (middle
      REJECT, unchanged from F4); right passphrase + right voice + wrong face
      raises the new `FaceAuthError` (inner REJECT); a v1 **or** v2 vault is
      refused via `LegacyVaultError`, each message naming its own missing
      layer; no reject path returns the name or any plaintext.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, count rises)

- [ ] **Task 3** — Booth bridge: enroll-face capture step, `unlock`'s third layer, distinct `auth_face`
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: Apply decision 3. Add `self._enroll_faceprints: list[np.ndarray] =
    []` beside `self._enroll_voiceprints` in `__init__`. `enroll_face_take()`
    mirrors `enroll_take()`'s shape exactly but reads `self.face.last_frame`
    and calls `faceprint.embed_frame` to validate (mirrors
    `set_face_reference`'s validate-before-accept pattern) — a frame with no
    face is `{"ok": False, "error": "no_face", "progress": ...}` and does NOT
    advance; on the `facelock.ENROLLMENT_TAKES`-th take, banks and reports
    `done: True`. `reset_enroll_face_takes()` mirrors `reset_enroll_takes()`.
    `enroll()` gains the same `need_face_takes` guard `need_voice_takes`
    already has, and passes `self._enroll_faceprints[:facelock.ENROLLMENT_TAKES]`
    to `vault_enroll`, clearing both lists only after a successful seal.
    `unlock()` embeds `self.face.last_frame` via `faceprint.embed_frame`
    (a missing/faceless frame is a new `{"ok": False, "error": "no_face"}`
    edge — same shape as `need_more_audio`'s role for voice) and passes it to
    `vault_unlock`; catch `FaceAuthError` → `{"ok": False, "error":
    "auth_face"}`, added alongside the existing `auth_outer`/`auth_voice`
    branches, before the generic exception fallback.
  - done-criteria:
    - §5 cmd 3 — verbatim, exit 0:
      ```
      uv run pytest tests/test_booth_api.py -q
      ```
      Must cover (per spec §5 item 3): the enroll-face capture step banking
      takes via a fake `FaceEngine` (mirroring the existing voice/face-
      diagnostic bridge test fakes, no real camera); unlock returning a
      distinct reason per layer (`auth_outer`/`auth_voice`/`auth_face`), none
      leaking the name; the `no_face` edge during enroll-face capture and
      during unlock.
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, count rises)

- [ ] **Task 4** — Booth UI: enroll-face capture step + third reject chip *(LAST task — full spec Verification)*
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Mirror the existing `#enroll-voice-step` block (Q4) almost
    verbatim as a new `#enroll-face-step` block, placed directly after it
    inside `#enroll-panel`: a take-progress row (3 dots, per decision 2's
    `facelock.ENROLLMENT_TAKES`), a hint line, a "Bank this frame" button
    wired to `call('enroll_face_take')`. `btnEnrollCancel`/`btnEnrollOpen`
    must also reset this step's takes (mirrors `resetEnrollVoiceStep`'s
    await-first pattern — decision: call `reset_enroll_face_takes` alongside
    `reset_enroll_takes`, same awaited-before-focus ordering, so an abandoned
    run's face takes cannot leak into the next enrollment either). `btnEnroll`
    click handler's `need_voice_takes` branch gains a sibling `need_face_takes`
    branch with the same shape. Add `<span class="chip mono hidden"
    id="chip-wrong-face">Face didn't match</span>` to `#result-chips`, and a
    `showWrongFace()` function mirroring `showWrongVoice()` exactly (status
    text "REJECT · FACE DIDN'T MATCH", sub-text naming voice+passphrase both
    already having passed); `hideResultChips()`'s chip list gains this chip;
    `btnUnlock`'s handler gains an `auth_face` branch calling it, alongside
    the existing `auth_outer`/`auth_voice` branches. **Per the earned
    guardrail on Booth layout changes** (`project.md`): this adds a new
    take-progress block inside `.enroll-panel`, which is a **different**
    column from `.booth`/`.window` (the guardrail's specific clipping hazard
    was `main`/`.booth`) — still smoke-test the enroll panel open/scroll
    manually before calling this task done, since any visible addition to a
    fixed-height flex column deserves the same caution.
  - done-criteria: **the FULL list from `spec.md`'s Verification section**, namely —
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, ≥145 passing, count risen by Tasks 1–3's new tests)
    - §5 cmd 1 — `uv run pytest tests/test_facelock.py -q` → exit 0
    - §5 cmd 2 — `uv run pytest tests/test_vault.py -q` (or wherever vault
      tests live) → exit 0
    - §5 cmd 3 — `uv run pytest tests/test_booth_api.py -q` → exit 0
    - §5 cmd 4 — **manual check, required.** Human runs `uv run voicelock`:
      enroll (name + passphrase + voice + face) → unlock with all three
      correct → **unlocked** (name shown); **wrong passphrase** → outer
      REJECT; right passphrase + **wrong voice** → middle REJECT; right
      passphrase + right voice + **a different face** → **inner REJECT**.
      Each reject names its distinct cause. Attested by the human at the
      feature-end checkpoint.

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in spec §1 gets recorded in `.out-of-scope/` and is never built.

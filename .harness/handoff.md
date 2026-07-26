# Handoff — F4 (Voice as the middle lock) · /plan session · 2026-07-25

## Where we are
F4's spec is **APPROVED** (both §0 boxes checked, Grilling `CLEAR`, **Mode 3**),
and `plan.md` now holds F4's ledger: **5 tasks, all `TODO`, `rejects: 0`**.
Nothing has been built — planning sessions never implement.

Entry gate quoted from `spec.md` this session: `**Status: CLEAR**` · `- [x]
Grilling record below is CLEAR` · `- [x] Approved by human` · `**Mode:** Mode 3
(Spec-to-done)` · marker scan `grep -c "NEEDS-CLARIFICATION:" .harness/spec.md`
→ **0**.

## Next action
`/implement` **Task 1** in a fresh session. **Mode 3 is the standing "go"** for
tasks inside F4 — no further human approval is needed until the feature-end
checkpoint (completion report + commit approval) or an escalation/amendment.

## The ledger (order = dependency order)
1. **Task 1** — 5-take speaker-A enrollment fixtures (`speakerA_enroll1..5.wav`)
   + a measured same-vs-different separation check. F3's fixtures are untouched.
2. **Task 2** — `src/voicelock/middlelock.py`: seeded LSH binarize + reliability
   mask + repetition/majority ECC + `commit` / `reconcile` / `derive_key`, with the
   tolerance constants pinned empirically from the Task-1 fixtures.
3. **Task 3** — `vault.py` **v2**: nested outer(passphrase) → middle(voice) layout,
   helper data inside the outer box, `VoiceAuthError` / `LegacyVaultError`, v1
   refused with a re-enroll signal.
4. **Task 4** — `BoothApi`: 5-take voice enroll + voice unlock returning the
   **distinct** `auth_outer` / `auth_voice` reasons, never a name on failure.
5. **Task 5** *(LAST — carries the FULL spec §5, incl. the required manual demo)* —
   Booth UI: enroll voice step, unlock voice step, two visibly distinct rejects.

## Risks the human should know about
- **Task 2 is the one that can genuinely fail.** Research (2026-07-23) measured
  ~25 % genuine bit-error on raw ECAPA sign-bits; the reliability mask + LSH
  expansion have to pull genuine error below the correction radius while keeping
  an impostor above it. The plan says: if the clusters will not separate with a
  margin after a real tuning attempt, report `BLOCKED` — do **not** quietly widen
  the radius. Expect this to be the slowest task.
- **Fixture honesty (inherited from F3, re-stated in spec §5).** The 5 enrollment
  takes and the same-speaker probe come from the same source recording, so the
  automated tests prove the math separates same-from-different but **cannot** prove
  cross-session robustness. That is precisely why Task 5's live manual demo is a
  **required** check, not accepted risk.
- **Breaking changes inside the repo (expected, planned for):** `vault.enroll` /
  `vault.unlock` gain a voiceprint argument, and the bridge's old
  `error: "auth"` becomes `auth_outer`. `tests/test_vault.py` (Task 3) and
  `tests/test_booth_api.py` (Task 4) are updated in the tasks that cause the break.
- **Your existing `~/.voicelock/vault.vl` is a v1 vault.** After F4 it will be
  **refused** with a re-enroll prompt (by design — no passphrase-only bypass).
  You will need to re-enroll once for the manual demo.
- Carried from F3, still open for a human: `spec.md`'s "~20 MB" model-size wording
  is wrong (the vendored ECAPA is ~85 MB). Spec edits are human-only.

## Commits (this session, on `main`)
- Base `ab696f2` (F4 `/spec`: CLEAR + APPROVED) → head: the `/plan` commit for
  this session (pending the commit checkpoint below).
- Remote: **none** — local history only, no push.

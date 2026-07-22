# Handoff — F2 Task 4 REVIEW (bridge + live vault)

## Session
- Date: 2026-07-22
- Feature: F2 — Passphrase-only vault (outer lock)
- Phase: `/implement` Task 4 → `REVIEW`
- Mode: Mode 3 (spec Approval gate)

## Done this session
- Task 3 wrap-up (`928bda8`); Mode 3 continued to Task 4.
- Committed `DOING` first (`16ac680`), then built.
- `BoothApi.enroll` / `unlock` → `vault.py` at `vault_path` (default
  `~/.voicelock/vault.vl`); re-enroll returns `needs_confirm` until overwrite.
- UI: overwrite Yes re-fires Enroll with overwrite flag.
- `tests/test_booth_api.py` (temp path). Local sanity: ruff 0; pytest 21 passed.

## Next action
1. Clean-context verifier via `formats/VERIFIER-PROMPT.md` (verbatim).
   Fill-ins: task **F2-T4** · base `16ac680` · head `7da064f`.
2. FULL Verification includes **required manual** Booth demo — Gate cannot drive
   pywebview. Human: run `uv run voicelock`, Enroll (name+pass) → confirm
   `~/.voicelock/vault.vl` exists → Unlock right (profile name) → Unlock wrong
   shows Wrong passphrase REJECT. Reply **manual PASS** (or FAIL notes) so the
   verifier / executor can close the Gate line.
3. On full APPROVE → wrap-up + Mode 3 completion report + feature-end checkpoint.

## Commit checkpoint
- Diff base (DOING): `16ac680`
- Build commit: `7da064f` — F2-T4: bridge Enroll Unlock to passphrase vault.
- Bookkeeping commit: (this file) — recorded after build.
- Remote: none (local history only) — no push.
- Left untracked: `harness-v1/`

## Pending
- Verifier F2-T4 + human manual Booth attestation

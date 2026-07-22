# Handoff — F2 COMPLETE (Mode 3 completion report)

## Session
- Date: 2026-07-22
- Feature: F2 — Passphrase-only vault (outer lock)
- Phase: wrap-up Task 4 → **feature complete**
- Mode: Mode 3 (spec Approval gate)

## Completion report

### Outcome vs spec
Spec Outcome: enroll with name + passphrase, seal Vault on disk via passphrase
outer lock, unlock peels it, wrong passphrase REJECTS visibly.
Shipped: PyNaCl Argon2id MODERATE + SecretBox vault (`VLCK` header) at
`~/.voicelock/vault.vl`; Booth Enroll/Unlock wired through `BoothApi`; wrong
passphrase shows REJECT chip; empty enroll refused; no-vault copy shown.
Voice / inner lock / challenge remain out (as specified).

### Final Gate evidence (F2-T4)
| Command | Exit |
|---|---|
| `uv run ruff check .` | 0 |
| `uv run pytest` | 0 (21 passed, 0 failed) |
| `uv run pytest tests/test_vault.py tests/test_outer_lock.py -q` | 0 (8 passed) |
| Manual Booth demo (human-attested) | PASS |

### Retry counts
- T1 rejects: 0 · T2 rejects: 0 · T3 rejects: 0 · T4 rejects: 0
- T4 had one ESCALATE_HUMAN (manual pywebview) → human **manual PASS** → re-Gate PASS

### Deviations during F2
- None recorded in `memory/deviations.md`.

### Escalations that resolved
- Manual Booth Verification line: Gate could not drive pywebview → human attested PASS.

### Verdicts
- `memory/verdicts/2026-07-22-F2-T1.json` … `F2-T4.json` · lessons: none each
- No ADR earned (TECH-PICK / expected outer-lock shape / UI chrome / bridge wiring)

## Next action
1. **Feature-end checkpoint (human):** approve the wrap-up commit message below
   (and push if/when you want a remote — currently none).
2. Next roadmap feature when you say go: **F3 — Voiceprint on screen** (or
   re-open `/spec` for F3).

## Commit checkpoint
- F2-T4 build: `16ac680`..`7da064f`
- Wrap-up commit: (this close-out)
- Remote: none (local history only)
- Left untracked: `harness-v1/`

## Pending
- Human feature-end approval (commit message / optional push)

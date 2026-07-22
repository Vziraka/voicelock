# Handoff — F2 spec draft at approval gate

## Session
- Date: 2026-07-22
- Feature: F2 — Passphrase-only vault (outer lock)
- Phase: `/spec` complete → awaiting human box-2 approval
- Mode (proposed in Approval gate): Mode 3

## Done this session
- Drafted `spec.md` for F2; grilled CLEAR (zero `[NEEDS-CLARIFICATION:` markers).
- TECH-PICK: PyNaCl (Argon2id + SecretBox) — research + decisions logged.
- Locked: `~/.voicelock/vault.vl`, name+pass only, mock Enroll/Unlock UX,
  Argon2id MODERATE, VLCK header, no-vault copy, Mode 3.
- Mode 3 blind spot is a **required Verification check** (manual live Booth
  enroll → vault file → unlock → wrong REJECT), not accepted risk.

## Next action
1. Human: read Outcome + Verification in `spec.md`, confirm Mode 3, type `x`
   in Approval box 2.
2. Fresh session: `/plan` after box 2 is checked.
3. Do not plan or build until both Approval boxes are checked.

## Commit checkpoint
- Committed: `4a85ae5` — Spec F2 parked at approval.
- Session base → head: `3e98b47` → `4a85ae5`
- Remote: none (local history only) — no push.
- Left untracked: `harness-v1/` (not part of this commit)

## Pending
- Human Approval box 2 in `spec.md`
- Fresh session: `/plan` after box 2 is checked

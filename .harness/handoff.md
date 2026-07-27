# F7 — Task 1 (`facelock.py`) · DONE · Task 2 next

**Verdict:** `memory/verdicts/2026-07-27-F7-T1.json` — GATE PASS, REVIEW
APPROVE, mechanism `subagent`, lesson `none`.
**Build commit:** `18118f0`. **Base:** `2753768`.

## Changed
`src/voicelock/facelock.py` (new) — face fuzzy-commitment module
(`commit`/`reconcile`/`derive_key`/`residual_bits`), ported from
`middlelock.py`'s shape per `plan.md` decisions 1–2 (variable-length
enrollment, `EMBEDDING_DIM = 128` pinned locally). `CORRECTION_RADIUS = 95`
measured over 100 fresh-LSH-seed trials against the real A1/A2/B fixtures
(genuine residual ≤ 20, impostor residual ≥ 170) — n=1 genuine / n=2
impostor, disclosed in the module docstring per spec Q2/§7.
`tests/test_facelock.py` (new) — 28 tests, real SFace model, no mocks.

## Failed + lesson
Nothing failed — `rejects: 0`. `learn` scan found no lesson clearing the bar
(see the verdict file's `note`): the radius measurement correctly applied the
existing dry-run-before-pinning guardrail rather than teaching a new one.

## next_action
Mode 3 is the standing "go" — **Task 2** (`vault.py`: bump to v3, nest the
face inner lock, refuse v1 and v2) starts unattended, same session, per
`plan.md`'s task ledger and decisions 3–6.

## Where the rest lives
`plan.md`'s task ledger (Tasks 2–4) and "Named architecture decisions"
section — nothing new decided this task beyond what was already recorded
there before Task 1 began.

## Commits this session
Base: `967cc66` (session start). `2753768` (Task 1 DOING, plus a stale
commit-hash fix in this file left over from last session).
`18118f0` (Task 1 build). `362b36b` (Task 1 build-commit handoff bookkeeping,
now superseded by this write). This wrap-up's commit follows.

## Pending guardrail
None.

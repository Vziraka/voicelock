# Handoff — F4 Task 1 · DONE · 2026-07-26

## Where we are
F4's approval box 2 was re-checked by the human, unblocking the build. **Task 1 is
`DONE`** — verified by a clean-context subagent (GATE PASS, REVIEW APPROVE, both
axes pass) and wrapped up. Tasks 2–5 are `TODO`; Feature 4 is 1/5 complete.

## Changed
Five 5-take enrollment fixtures + their documentation. Details live in the files,
not here:
- `tests/fixtures/voiceprint/speakerA_enroll1..5.wav` — new (see the README for
  derivation, geometry and caveats)
- `tests/fixtures/voiceprint/README.md` — the durable build-notes for Task 2
- `.harness/plan.md` — Task 1 `DONE` + measurements under the task
- F3 fixtures untouched and byte-identical

## Failed + lesson
Nothing failed. `rejects: 0`, no retries, no deviations entry owed. The `learn`
compound scan ran and recorded `"lesson": "none"` — no rework, no human
course-correction, no recurring pattern. Verdict:
`memory/verdicts/2026-07-26-F4-T1.json`.

One judgment call, made by measurement and confirmed independently by the
verifier: window length was pinned at **1.6 s**, not the plan's "~1.0 s" sketch —
1.6 s is the longest length at which fixture takes 1 and 5 still share zero audio,
so anything longer would manufacture cross-take stability out of shared audio and
corrupt spec §4's unanimity filter into measuring the cut instead of the speaker.

## next_action
**Task 2 — `middlelock.py`** (LSH binarize + reliability mask + repetition ECC +
commit/reconcile + key derive). Not started. Mode 3 is the standing "go" and this
wrap-up completing is the precondition. *(curate due)*

Before pinning any tolerance constant, Task 2 should read
`tests/fixtures/voiceprint/README.md` — it carries the measured starting point
(98/192 raw sign bits unanimous across the five takes; genuine sign-BER 7.8 % vs
impostor 43.2 %; 5-take mean → same-speaker 0.0583, → impostor 0.8451). Better
than the research's ~25 % warning, but the bits stay correlated (192 real
dimensions), so binomial estimates will be optimistic. Measure; do not trust the
arithmetic. Task 2 is the one that can genuinely `BLOCKED` — never widen the
correction radius to force a pass.

## Where the rest lives
- task ledger + per-task notes → `plan.md`
- the keystone construction + the five accuracy levers → `spec.md` §4
- why the levers were chosen → `memory/decisions.md` (2026-07-26)
- fuzzy-commitment research → `memory/research/2026-07-23-f4-fuzzy-reconcile.md`
- fixture geometry, measurements, caveats → `tests/fixtures/voiceprint/README.md`

## Commits (this session, on `main`)
- `a13d891` — Task 1 `DOING` + the human's box-2 approval (diff base)
- `01667e1` — build commit (diff head)
- `a671db3` — bookkeeping handoff
- plus this wrap-up's state commit. Remote: **none** — local history only, no push.

## Pending guardrail
None. The `learn` scan proposed nothing.

## Notes for the human (no action required unless you disagree)
- **Curate is due** — 15 verdict files vs `project.md`'s `Last curated: never ·
  verdicts then: 0`. Reminder only; curate stays human-invoked and nothing blocks.
- `spec.md` §0's amendment paragraph still reads "*box 2 re-opened, awaiting the
  human's `x`*" while box 2 is `[x]`. Stale prose only — the checkbox is the
  mechanical gate. I did not edit your spec to tidy it.
- Carried from F3, still open: `spec.md`'s "~20 MB" model-size wording is wrong —
  the vendored ECAPA is ~85 MB.
- Carried: your existing `~/.voicelock/vault.vl` is a v1 vault and will be refused
  with a re-enroll prompt after F4 (by design, confirmed 2026-07-26).

# Plan — {SPEC NAME}

## Active context
- Updated: {date}
- Spec: `spec.md` · Feature: {Feature {n} | none} · Mode: {Mode 1–4} · Phase: {name}
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only when the Gate exited 0 **and** the Reviewer approved.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [ ] **Task 1** — {task; name the exact file(s) it touches}
  - state: TODO
  - rejects: 0
  - feedback: {append log, newest first — the Verifier writes structured reject
    reasons here and never overwrites older entries}
- [ ] **Task 2** — {task}
  - state: TODO
  - rejects: 0

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. {date} — initialized.

---
name: plan
description: Break an approved spec into small, independently verifiable tasks. Use after the spec is approved, before building.
invocation: user
---
# Plan

Tracer bullets: each task is the smallest slice that can be built and verified on
its own.

## Trigger
`spec.md` approval boxes are checked — including after a spec amendment (an
amended spec re-plans its affected tasks here before any building).

## Workflow
1. **Entry gate (blocking):** open `spec.md` and verify all three, quoting each:
   the Grilling record says `Status: CLEAR`; a search for the clarification
   marker (the bracketed `NEEDS-CLARIFICATION` token in its colon form) returns
   ZERO hits — this is now a true mechanical check, prose never uses the colon
   form; and both approval boxes are checked with the `Mode:` line set. If ANY
   fails, STOP and report "spec not grilled/approved — run /spec first." Do not
   plan a partially clarified spec, and do not fix the spec yourself from here.
2. Read the approved `spec.md`, the constitution, and `memory/codebase-map.md`.
3. Break the work into tasks. Each task names the exact file(s) it touches and has
   a clear, checkable, **runnable** done-criterion — the commands that prove it,
   each expected to exit 0. The feature's LAST task's done-criterion is the FULL
   list from the spec's **Verification** section (find it by name — numbers
   drift); intermediate tasks gate on their own criteria (the universal [Done]
   rule — the Gate reads these, so an unrunnable criterion blocks verification).
   At Modes 3–4 this is strict for EVERY task: a judgment-worded criterion
   ("reasonably fast") cannot gate an unsupervised task — make it runnable or
   send it back to the spec.
   A defect-fix task's done-criterion names its reproduction: the failing
   command or flow at base, the same one passing at head (a repro test when
   one exists).
4. Write the ledger to `plan.md`, all `TODO` with `rejects: 0`. Order them so
   dependencies come first. Copy the spec's `Feature:` line into the Active
   context header.
5. Refresh the `≤5-bullet` memory spine.
6. **Close the session:** update `handoff.md` (next_action: human "go" →
   `/implement` Task 1 in a fresh session — or, at Modes 2–4, "the approved
   Mode is the standing go; implement starts Task 1") per the universal [State]
   session-end rule, then run the **commit checkpoint** — stage the state
   files, show the human the proposed commit message, and on their approval
   commit (push only if a remote exists — say so). Record the session's
   base → head commit hashes in `handoff.md`, like every session does.
7. Stop. Do NOT start implementing — building belongs to the implement skill's
   own session, never the planning session. (At Modes 2–4 that next session
   starts without a further "go"; the planning session still ends here.)

## Guardrails
- Stay inside scope — honor the spec's non-goals.
- Smallest correct steps; prefer many thin tasks over one fat one.
- If a task is ambiguous in a way that changes the design, stop and ask.

## Completion criterion
Every requirement in the spec maps to **at least one** task, every task has a
checkable done, and exactly that ledger is written to `plan.md`.

## Output
A `plan.md` task ledger ready to build (`WIP=1`).

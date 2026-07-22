---
name: learn
description: Turn what a task taught us into at most one evidence-anchored guardrail. Runs automatically inside every wrap-up (compound mode); also usable directly after a systemic failure.
invocation: model
---
# Learn

A lesson is only worth a rule if it would recur. Scan every task; write rarely.

## Trigger
- **Compound mode (automatic):** the `wrap-up` skill invokes this after every
  APPROVE. Never skipped — but "no lesson" is the common, correct result.
- **Failure mode (human-invoked):** a systemic or repeated failure, a task
  rejected 3 times, or a human correction that then worked.

## Workflow
1. Scan the task's full arc — grilling answers, build, gate output, review
   verdict, handoff doubts — against the bar. A lesson clears it only if:
   it would recur on future tasks, AND (it cost real time/rework OR a human
   had to correct course OR a non-obvious pattern emerged that took 5+ tool
   calls to find). One-offs never clear the bar.
2. Nothing clears the bar → write the task's verdict file (named per
   `memory/verdicts/README.md` — `{date}-F{n}-T{n}.json`, plain task id only
   when Feature is `none`: spec, change, gate, reviewer,
   `"lesson": "none"`) and return to the caller. This is the single write of
   that file — created once here, never edited after. Done — do not invent a
   lesson to have something to show.
3. A lesson clears it → diagnose: what happened, the root cause, and the
   **evidence** (quote it).
4. Overlap-check against existing `project.md` guardrails across five dimensions
   (problem, root cause, fix, files, prevention). High overlap → update the
   existing rule instead of adding.
5. First ask: could this lesson be ENFORCED instead of remembered — an invalid
   state made unrepresentable, a lint or banned-API check, a canonical helper,
   a script, or a check added to the spec's standing Verification commands?
   If yes, propose that mechanism (it changes real code, so it goes through the
   normal spec/approval path — never applied during wrap-up). Prose is the
   fallback when enforcement genuinely needs judgment — say why when you fall
   back. Then draft ONE guardrail in `project.md` format: `[Category]` + rule +
   `severity` + expiry + `_Evidence:_`. Propose the diff to the human. Only on
   approval, write.
   If no human is present to answer, record
   `"lesson": "proposed — pending approval"` in the verdict file, park the full
   proposal in `handoff.md` (Pending guardrail), and return — never write
   `project.md` unapproved, never stall the caller waiting.

## Guardrails
- The scan is mandatory; the write is rare. Most tasks teach nothing new — say so.
- Project-specific lessons go in `project.md`, **never** `universal.md`.
- Overlap-check before writing — do not grow a pile of near-duplicates.
- A human approves before any `project.md` write, even in compound mode.

## Completion criterion
The scan ran and its outcome is recorded in the verdict file — either
`"lesson": "none"` or one approved (or explicitly declined) guardrail diff.

## Output
An updated verdict file; on approval, an updated `project.md`.

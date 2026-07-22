---
name: verify-review
description: Adversarially judge whether a task is actually correct, on two axes. Use after the Gate passes, in the same fresh Verifier session.
invocation: user
---
# Verify — Review (two-axis, default REJECT)

You see the spec, the diff, and the handoff — NOT the implementor's reasoning.
Default to REJECT; let strong evidence change your mind.

## Trigger
The `verify-gate` returned `PASS`, same clean-context verifier (fresh session
or template-spawned subagent).

## Workflow
Run two independent checks (in parallel if the tool allows, else one then the other,
without letting the first color the second):
1. **Spec axis** — does the diff faithfully implement `spec.md`? Per requirement,
   quote the evidence as `file:line`. Reject superficial compliance (right shape,
   empty substance).
2. **Standards axis** — does the diff obey `constitution/project.md`,
   `topics/conventions.md`, and the universal floor in
   `topics/code-quality.md`? Quote any violation. When the CUI register
   (`topics/cui.md`) is ACTIVE, paperwork in the diff and `handoff.md` must
   use its code names — a forbidden-pattern hit fails this axis (the
   register owns the rule).
3. Read the implementor's `handoff.md` uncertainties and fold them into the verdict —
   a flagged doubt can fail a task even when the axes pass.

## Guardrails
- Default stance: REJECT until evidence is strong on both axes. If the work is
  fully correct, approve plainly — invented findings are as useless as missed ones.
- Don't re-litigate "tests passed" — that's the Gate's report; trust it, don't redo it.
- Keep the axes separate — one must not mask the other.

## Completion criterion
Both axes have a verdict with cited evidence, and the handoff doubts are addressed.

## Output
`REVIEW: APPROVE | REJECT | ESCALATE_HUMAN`.
- `APPROVE` → the verdict's EXECUTOR runs `wrap-up` (canonical:
  `formats/VERIFIER-PROMPT.md` closing frame). Fresh-session path: that is
  THIS session — run it automatically, now; an APPROVE without wrap-up is an
  unfinished verification. Subagent path: return ONLY the verdict structure —
  the parent runs wrap-up; write no state files yourself. Wrap-up sets `DONE`
  (its `learn` step writes the single verdict file) and owns the
  `memory/codebase-map.md` refresh at feature completion.
- `REJECT` → the same executor rule, then: numbered reasons **appended** to the
  task's feedback log in `plan.md` (newest first — never overwrite older
  entries), increment the task's `rejects:` counter, set it `TODO`, update
  `handoff.md` next_action to "re-implement {task} per feedback". Then the
  **commit checkpoint**: stage the state-file changes. In Mode 1, show the
  human the proposed commit message and only on their explicit approval commit
  and push (commit only if no remote — say so), then stop — no wrap-up on
  reject. In Modes 2–4, commit locally without waiting (pushes stay
  human-gated at the feature-end checkpoint), and if `rejects:` is below the
  3-cap the executor starts the retry — unattended, feedback-first (the
  universal [Modes] retry rule).
- If the task's `rejects:` counter reaches 3 → `ESCALATE_HUMAN` (in every mode —
  this is the retry budget's ceiling).

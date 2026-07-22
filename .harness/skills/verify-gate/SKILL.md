---
name: verify-gate
description: Deterministically check a task by running the spec's verification commands. Use FIRST in a fresh Verifier session, before any judgment.
invocation: user
---
# Verify — Gate (deterministic)

The Gate has no opinions. It runs commands and reads exit codes. Same input, same
verdict, every time.

## Trigger
A task is `REVIEW`. Clean-context verifier — a fresh session, or a subagent
spawned with `formats/VERIFIER-PROMPT.md` verbatim. The Gate runs before the
Reviewer.

## Workflow
1. Read the **Verification** section of `spec.md` (find it by NAME — section
   numbers drift as specs grow) AND the task's entry in `plan.md` (its
   done-criteria). Also scan `plan.md`: any task marked `DONE` with no matching
   verdict file in `memory/verdicts/` is invalid — revert it to `REVIEW` and
   report it before proceeding.
2. Determine this task's command list per the universal [Done] rule: an
   intermediate task runs its `plan.md` done-criteria; the feature's LAST task
   runs the FULL list from the spec's Verification section. Run **every**
   command on that list exactly as written, in this session. Capture the exit
   code and output of each. Only a full run of that list counts — a subset, a
   cached result, or "it passed during implement" is not verification.
3. **Runtime budgets.** Every command has one: 10 minutes by default, or the
   budget the spec's Verification section declares for it. Run each command in
   the **foreground and wait** — watchdog scripts, kill-timers, and attaching
   monitors to process ids are forbidden verifier behavior (a stale watchdog
   once killed a healthy training run). A command still running past its budget
   is recorded `FAIL — budget exceeded`; never kill the process — report and
   let the human decide.
4. Scope check: run `git diff <base>..<head>` using the base and head commits
   recorded in `handoff.md`; confirm only the files the task and spec imply were
   changed — no forbidden writes. **CUI tripwire (only when
   `constitution/topics/cui.md`'s Status is ACTIVE):** scan the diff and the
   commit message against the register's forbidden patterns; any hit = FAIL
   (the register owns the rule). If handoff.md records no commits, that is itself
   a finding: verdict `ESCALATE_HUMAN`. (A state-only bookkeeping commit after
   the build commit is expected — see the implement skill's two-commit rule —
   and is not a scope violation.)

## Guardrails
- The Gate only runs commands and reads exit codes — fixing and judging belong
  to later steps.
- If a command cannot run (missing env/credentials), verdict is `ESCALATE_HUMAN` —
  never skip it and pass on the rest.
- `ESCALATE_HUMAN` sets the task `BLOCKED` — never leave it sitting at `REVIEW`.

## Completion criterion
Every verification command was run and its exit code recorded. Verdict is `PASS`
only if **all** exit 0 **and** scope holds.

## Output
`GATE: PASS | FAIL | ESCALATE_HUMAN` with the commands, exit codes, and scope result.
- `PASS` → hand to the `verify-review` skill (same session).
- `FAIL` → this bookkeeping belongs to the verdict's EXECUTOR (canonical:
  `formats/VERIFIER-PROMPT.md` closing frame — the parent on the subagent
  path, this session on the fresh-session path; a subagent returns the
  structure only and writes NO state files): **append** the failing
  command + output to the task's feedback log in `plan.md` (newest first —
  never overwrite older entries), increment the task's `rejects:` counter, set
  the task `TODO`, update `handoff.md` next_action to "re-implement {task}
  per feedback". Then the **commit checkpoint**: stage the state-file changes.
  In Mode 1, show the human the proposed commit message and only on their
  explicit approval commit and push (commit only if no remote — say so), then
  stop. In Modes 2–4, commit locally without waiting (pushes stay human-gated
  at the feature-end checkpoint), and if `rejects:` is below the 3-cap the
  executor starts the retry — unattended, feedback-first (the universal
  [Modes] retry rule; the cap's next failure is `BLOCKED`).

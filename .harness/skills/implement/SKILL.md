---
name: implement
description: Build ONE task from the plan, then hand off for verification. Use in an Implementor session when a task is TODO.
invocation: user
---
# Implement

You build; you do not judge. One task, then stop and hand to fresh eyes.

## Trigger
A task in `plan.md` is `TODO` and you are in an Implementor session, via ONE of:
- an explicit human "go" (Mode 1 — always);
- the approved feature's next task, after the previous task's wrap-up fully
  completed (Modes 2–4). A previous task merely finishing is NOT a trigger;
  the wrap-up artifacts (verdict file + committed state) are;
- a **budgeted retry**: the task was just set back to `TODO` by a Gate FAIL or
  Review REJECT and its `rejects:` count is below the 3-cap (the universal
  [Modes] retry rule). At Modes 2–4 the retry starts unattended, same session,
  feedback-first; at Mode 1 it waits for the human's "go" like everything else.

## Workflow
1. Read in parallel: `constitution/universal.md` + `project.md`, `spec.md`,
   `plan.md`, `handoff.md`, `CONTEXT.md`, and the relevant code.
2. **Entry gate:** confirm the spec's Grilling record says `CLEAR`, both
   approval boxes are checked, and the `Mode:` line is set. If not, STOP — the
   spec phase is incomplete. Also scan `plan.md`: any task marked `DONE` with
   no matching verdict file in `memory/verdicts/` is invalid — revert it to
   `REVIEW` and report it first. If this is a retry, re-read the task's
   feedback log FIRST — every fix attempt starts from the failure evidence,
   not from memory. A `Pending guardrail` in `handoff.md` is surfaced to the
   human at your first touchpoint (the handoff line's own rule).
3. **Quote** the spec and constitution lines you are implementing (so the work is
   anchored, not improvised). Pick the ONE next task → set it `DOING` — and
   make that durable NOW: write `plan.md` and **commit it** before touching any
   code. A crash must always find the ledger telling the truth; a `DOING` that
   exists only in your intentions orphans whatever you build. Note the current
   HEAD commit — it is the diff base the Gate will use.
4. Build the smallest correct increment. Follow the conventions and the
   universal floor in `constitution/topics/code-quality.md`. Reuse before you
   reinvent. Validate references and paths before using them. Tests verify
   correctness; they do not define the solution — implement the actual logic
   that solves the problem generally, no hard-coding to pass a test, and no
   editing a test to make it pass. If a test looks wrong, say so instead of
   working around it. An idea the human declines mid-build gets a file in
   `.out-of-scope/` (durable), not just a plan/handoff note (prunable).
   **Bug-fix tasks** (the task fixes a defect): before changing code, reproduce
   the failure on the surface where it was reported — run the failing command
   or flow and capture it. Name the evidence for the root cause, not just the
   symptom. When a failing test is cheap, write it first — failing at base,
   passing at head. After the fix, run the SAME reproduction. This is failure
   evidence and falls under the step-5 measurement exception: disclose exactly
   what you ran in `handoff.md`; the fresh-eyes Gate still owns verification.
   If a candidate fix already exists, verify THAT (baseline vs patched) instead
   of authoring a competing one. Cannot reproduce → the task goes BLOCKED with
   the attempt recorded — never a speculative patch.
5. Run a quick local check (syntax/lint) — not the full Gate. **Measurement
   exception:** when the task's done-criterion IS a measurement (e.g. "accuracy
   at or above 85%"), you may run the measurement commands to know you are
   done — disclose exactly which Gate commands you ran in `handoff.md`; every
   remaining Gate check stays reserved for fresh eyes.
6. **Commit in two steps** — a commit cannot contain its own hash, so don't
   try: (a) the **build commit** — the change plus `plan.md`'s `REVIEW` state,
   task id in the message; (b) the **bookkeeping commit** — write `handoff.md`
   (light: changed / failed+lesson / next / where-the-rest-lives) recording the
   base commit from step 3 and the build commit's hash, plus anything you are
   unsure about, then commit that state file alone. The follow-up state-only
   commit is official and expected — the verifier knows `handoff.md`'s head
   refers to the build commit, one behind actual HEAD.
7. **Stop report.** Print exactly:
   - Task: {id} — now `REVIEW`
   - Files changed: {list}
   - Handoff: written · commit: {base}..{head}
   - Next: the clean-context verifier (`formats/VERIFIER-PROMPT.md`, used
     verbatim)
   - Next for you: {Mode 1: say "verify" · Modes 2–4: nothing —
     verification starts itself} — add "(New here? `GUIDE.md` walks the
     loop.)" when the Environment section says first-time user

   **Before spawning the verifier:** if you know the template contains an
   error (a stale reference, a wrong path — anything), you may not fix it (the
   verbatim rule stands) but you MUST say so to the human first — knowingly
   passing a defective prompt in silence is forbidden.

   Then: in **Mode 1**, take no further action except ONE — on the human's
   explicit "verify", spawn the verifier with the template verbatim (fill only
   task id / base / head) and execute its verdict, never your own. In
   **Modes 2–4**, spawn the verifier yourself, immediately, same rules — and if
   the host tool has NO clean-context subagent, do not self-verify: commit
   state, write the handoff (next_action: "verify in a fresh session"), and
   STOP. Degrading to a human touchpoint beats judging your own diff, in every
   mode. In no mode do you look at the next task, "quickly also" refactor,
   test, or tidy — the next task exists only after wrap-up completes.

## Guardrails
- `WIP=1` — one task at a time, every mode. The moment your task hits `REVIEW`,
  every remaining `TODO` is out of bounds until the current task's wrap-up
  fully completed (and, in Mode 1, a human says "go" in a new session).
- Only `wrap-up` marks a task `DONE` — after verification, with a verdict file
  as proof.
- Retries are budgeted: 3 fix→re-verify attempts per task (the `rejects:`
  counter in `plan.md` is the durable count); the next failure sets the task
  `BLOCKED`. Never reset or re-argue the counter.
- **Chained-context advisory (Modes 2–4):** a session that chains tasks
  accumulates build context — the verifier stays fresh, the builder does not.
  That is the accepted tradeoff, not a bug; but on a weaker model or a large
  feature, prefer a fresh session per feature (or per few tasks) when quality
  wobbles. Fresh eyes verify; tired eyes still build.
- Never run irreversible git. Never verify your own work — spawning the
  template verifier is allowed; judging the diff yourself is not.
- A dependency, tool, or framework not named in the spec or `project.md` =
  STOP and run `formats/TECH-PICK.md`. No silent installs.
- Never declare victory here — completion is declared only by `wrap-up`, after
  verification.

## Completion criterion
Exactly one task is `REVIEW`, its `DOING` was committed before building, both
commits exist (build + bookkeeping), `handoff.md` is written, the stop report
was printed, and you did **not** verify it yourself or touch a second task.

## Output
The change, an updated `plan.md`, a fresh `handoff.md`, and the stop report.

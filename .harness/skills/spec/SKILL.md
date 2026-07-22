---
name: spec
description: Turn a change request into an approved, executable spec. Use at the start of any new piece of work, before planning or building.
invocation: user
---
# Spec

A spec is a contract the build is measured against. Make it tight and runnable.
The ambiguity scan is unconditional — "the request was clear" is a scan RESULT
(all rows Clear), never a reason to skip the scan.

## Trigger
The human wants to build or change something — or, in a Mode 4 feature, the
previous feature just completed and the roadmap has a next entry (see
"Unattended drafting" below).

## Workflow
1. Read `constitution/universal.md`, `constitution/project.md`, `CONTEXT.md`,
   and the `.out-of-scope/` folder — concept-match the request against past
   rejections and surface any hit before drafting (never silently re-propose
   a rejected idea). **Scaffold guard:** if `project.md` / `conventions.md` are still empty templates and
   no test/lint commands exist (a new repo where intake never ran), STOP and run
   `/intake-scaffold` first — the Gate needs real commands. Don't silently fold setup
   into a feature spec.
2. Draft `spec.md` from the request: outcome, non-goals, constraints. Fill the
   `Feature:` line from `roadmap.md` (`none` if no roadmap exists) — wrap-up
   uses it to know when a feature is complete. Any NEW dependency, tool, or
   framework the spec introduces → run `formats/TECH-PICK.md` (candidates +
   liveness evidence + walkthrough + human approval) before locking the
   Constraints section.
3. **Ambiguity scan (mandatory — never skipped, even for "simple" requests):**
   grade every category in the Grilling record Clear / Partial / Missing.
   Anything Partial or Missing that would change what gets built is
   **implementation-critical** — mark it inline in the section where it belongs
   with the clarification marker (colon form — the greppable token the
   universal [Startup] rule checks).
4. Run the `grilling` skill on the markers — one question at a time, each with
   your recommended answer. Write every answer back into the matching spec section
   and update that category's row (the spec stays the single source of truth).
5. **Mode.** Ask the human which development mode this feature runs at
   (Mode 2 is the default; describe the ladder in one line each). Two checks:
   Mode 4 requires a prior feature in this repo completed cleanly at Mode 3
   or 4 — the check is mechanical, not vibes: a `memory/verdicts/` file whose
   `dev_mode` records Mode 3 or 4, plus that feature's completion report in
   git history. Neither exists → refuse Mode 4 and offer Mode 3. At Mode 2 or higher, ask
   ONE extra mandatory grilling question: **"If every gate in this spec passed
   but the feature were still wrong, what would be wrong?"** — the answer
   becomes a new verification check or is recorded in the spec as accepted
   risk. Write the `Mode:` line into the Approval gate.
6. When every row is Clear/Resolved and zero markers remain, set the Grilling
   record to `Status: CLEAR` and check the first approval box.
7. Write the **Verification** section as **runnable** commands — the exact
   commands the Gate will run, each expected to exit 0. This is the definition
   of done. It always has two parts: the project's **standing commands** (full
   test / lint / build from `project.md` — the regression net that proves
   nothing else broke) plus the **feature-specific** commands that prove this
   feature works. Pick the feature-specific commands at the highest real
   surface the feature touches (UI, CLI, API — a script driving the real thing
   counts); if that surface is unreachable, write the exact limitation into the
   Verification section instead of substituting a proxy silently. Any command
   expected to exceed the 10-minute default budget
   declares its own budget here. At Mode 2+, every command must have pinned
   expectations; at Modes 3–4, the spec must also state the out-of-scope
   default (record in `.out-of-scope/`, never build).
8. Stop at the approval gate. The human checks the second box.
9. **Close the session:** update `handoff.md` (next_action: human checks box 2 if
   still open, then `/plan` in a fresh session) per the universal [State]
   session-end rule, then run the **commit checkpoint** — stage the state files,
   show the human the proposed commit message, and on their approval commit
   (push only if a remote exists — say so). Record the session's base → head
   commit hashes in `handoff.md`, like every session does.

## Unattended drafting (Mode 4 only)
When this skill runs unattended after a Mode 4 feature completes, steps 4–5
change shape — there is no human to interview:
- Every grilling question is written INTO the draft spec as a clarification
  marker (colon form) with your recommended answer attached — batch grilling.
  The human resolves each one at approval time; the mechanical marker check
  makes an unresolved question physically block approval.
- The `Mode:` line is left blank for the human to set at approval.
- The draft parks at the approval gate and the session closes (handoff:
  next_action = "resolve the draft spec's embedded questions, set the mode,
  check box 2"). Never proceed past the gate; never draft more than this ONE
  spec. Roadmap empty = report "roadmap complete" and stop.

## Guardrails
- Do not plan or build until the Grilling record is `CLEAR` AND the human box is
  checked. Never set the status to CLEAR while a clarification marker remains.
- A question that changes architecture, security, data model, or naming is a
  must-answer — never a silent default.
- Use `CONTEXT.md` terms so names stay consistent.

## Completion criterion
Every section is filled, the Grilling record says `CLEAR` with every row resolved,
the verification commands are real and runnable, the `Mode:` line is set (or, in
unattended drafting, deliberately blank), and the approval box is checked by the
human — or the draft is parked at the gate with its questions embedded.

## Output
A complete `spec.md` awaiting approval. End with one line for the human —
"Next for you: in `spec.md`, read Outcome + Verification, set the Mode
line, and type the x in box 2 yourself." If the Environment section says
first-time user, add: "(New here? `GUIDE.md` walks the loop.)"

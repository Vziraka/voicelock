---
name: wrap-up
description: The mandatory end-of-task protocol — update every state file, run the learn compound scan, then stop. Reached automatically by verify-review on APPROVE; the ONLY permitted way to declare a task complete.
invocation: model
---
# Wrap-up

No victory lap without the ledger. Every state file updated, every update proven,
the compound scan run — then, and only then, the stop report.

## Trigger
`verify-review` returned `APPROVE`, and the verdict's EXECUTOR invokes this
skill (the canonical owner rule is `formats/VERIFIER-PROMPT.md`'s closing
frame): on the fresh-session path that is the verifier session itself, same
session; on the subagent path it is the parent, right after the structure
comes back. A human can also invoke it to close out an interrupted task.

## Workflow
Execute in order. For every file write, **prove it**: re-open the file and quote
the updated line in your output. An unquoted update did not happen.
**`DONE` is written LAST** — literally the final file write of the checklist
(step 5), so if the session dies mid-checklist, the task must look unfinished,
never finished. The steps below are ordered to honor that; follow the numbers.

1. **ADR** — apply the 3-condition gate from `formats/ADR.md` (hard to reverse ·
   surprising without context · real trade-off). All three → write the ADR at
   the path `formats/ADR.md` names for this repo (default
   `docs/adr/NNNN-short-title.md`) and quote its title line. Any fail → state
   "no ADR: fails condition {n}". Never silently skip the check.
2. **`learn` compound scan** — run the `learn` skill in compound mode over this
   task's full arc (grilling answers, build, gate output, review verdict). It
   writes THE verdict file — named per `memory/verdicts/README.md`
   (`{date}-F{n}-T{n}.json`; plain task id only when Feature is `none`) with
   spec, change, gate, reviewer, **mechanism** (which clean-context path
   actually verified — subagent or fresh-session; record what happened, not
   what the template assumed), lesson — the single write of that file. "No
   lesson met the bar" is a valid, recorded outcome; skipping the scan is not.
   If a guardrail proposal needs approval and no human answers, park it in
   `handoff.md` (Pending guardrail) and proceed — never write `project.md`
   unapproved, and never stall the wrap-up waiting. Also check: any idea the
   human declined during this task must have its `.out-of-scope/` file — if it
   lives only in plan/handoff notes, write the file now (those notes get
   pruned; the rejection must not evaporate).
3. **`handoff.md`** — regenerate (reference, don't restate): changed /
   failed+lesson / next_action / where-the-rest-lives / commits / pending
   guardrail. Keep the template's parenthetical format rules — they are part
   of the format, not instance content to prune. `next_action` names the next roadmap item but does NOT start it.
4. **`roadmap.md`** — read the plan's `Feature:` line. If every OTHER task in
   `plan.md` for that feature is `DONE` and this task just got APPROVE (i.e.
   step 5 is about to complete the feature), check the feature's box
   (`- [x] **Feature {n}**`). Otherwise state "roadmap unchanged — {n} tasks
   remain in Feature {n}". Quote or state. **Feature-complete extras:** refresh
   `memory/codebase-map.md` to match what was actually built, or stamp its
   header `STALE as of {date}` — the read order tells every session to trust
   that file, so it is either true or marked untrue, never silently wrong.
5. **`plan.md`** — the LAST file write: refresh the **Active context** block
   (Updated / Phase / next), refresh the memory spine (≤5 bullets, resolved
   items pruned; first bullet = current truth), then set the task `DONE` as the
   final line touched. Quote the Active context, the spine, and the task line.
6. **Commit checkpoint + stop report** — stage the state files (plan, roadmap,
   handoff, ADR, verdict, decisions) with the task id in the message.
   **Curate check:** count the verdict files (`*.json`) in `memory/verdicts/`
   — the folder's permanent `.md` files never count — and subtract the
   `verdicts then` number from `project.md`'s `Last curated` stamp (no stamp
   or `never` = subtract zero). At 10 or more, print one line — "Curate is
   due: {n} tasks since the last curate" — and append "(curate due)" to
   `handoff.md`'s next_action. A reminder only: curate stays human-invoked,
   and nothing blocks on it.
   **Mode 1:** show the human the proposed commit message and WAIT for explicit
   approval — only then commit AND push (commit only if no remote — say so).
   **Modes 2–4:** commit locally without waiting; pushes stay human-gated at
   the feature-end checkpoint. Then print the checklist with each item ✅ + its
   quoted proof, the verdict, and the mode-appropriate closing:
   - **Mode 1:** "Task {id} complete. Awaiting human go for the next task."
     Then stop — starting the next task from here is forbidden.
   - **Modes 2–4, feature not complete:** "Task {id} complete. Continuing to
     the next task per the approved Mode." The session may take the next task
     (the implement skill's trigger) — this wrap-up completing IS the
     precondition.
   - **Modes 3–4, feature complete:** write the **completion report** into
     `handoff.md` (replacing the next-session framing): outcome vs the spec's
     Outcome section · full final-Gate evidence (command → exit code) · retry
     counts per task · every `memory/deviations.md` entry made during the
     feature · anything escalation-worthy that resolved itself. In **Mode 4**,
     THEN invoke the `spec` skill's unattended drafting for the next roadmap
     entry (one draft, parked at its approval gate; roadmap empty = "roadmap
     complete") — the draft is file work and happens BEFORE the wait, so the
     human sits down once to everything: report, draft, checkpoint. LAST, show
     the proposed commit message and WAIT for human approval (the feature-end
     checkpoint — commit + push on approval).
   - **Mode 2, feature complete:** same feature-end checkpoint (message shown,
     human approves commit + push) — present the final verdict's summary
     (Gate results + both review axes + any deviations entries) alongside it;
     reviewing that is Mode 2's contract.

   In every mode: when `project.md`'s Environment section says first-time
   user, append "(New here? `GUIDE.md` walks the loop.)" to the closing line.

## Guardrails
- All six steps, in order, every time — a "trivial" task still gets the full
  protocol.
- Proof = quoted line from the re-opened file. Claiming without quoting fails
  the wrap-up.
- This skill closes tasks; the only work it may open is the Mode 4 unattended
  spec draft, and only at feature completion.
- **Interrupted wrap-up:** a task with an APPROVE verdict file in
  `memory/verdicts/` but not `DONE` in `plan.md` is an interrupted wrap-up.
  The human re-invokes `wrap-up`; resume from the first unproven step.
  (A checked roadmap box with the task still `REVIEW` is the same signal.)

## Completion criterion
Every checklist item shows ✅ with quoted proof (or an explicit recorded
"unchanged / no ADR / no lesson" with its reason), and the stop report — or the
mode-appropriate continuation — was printed.

## Output
Updated `plan.md`, `roadmap.md`, `handoff.md` (+ ADR / guardrail if earned), the
archived verdict, and the stop report (or completion report at Modes 3–4).

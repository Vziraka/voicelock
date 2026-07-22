---
name: spec-lite
description: The small-change fast path — a minimal spec (outcome + runnable verification) built and verified in one sitting. HUMAN-INVOKED ONLY; the agent must never suggest, recommend, or choose it.
invocation: user
---
# Spec-lite (small-change fast path)

The escape valve, inside the harness. For changes a HUMAN judges genuinely small
— a typo, a config value, a one-line fix. Ceremony is waived; determinism is not:
the Gate's commands still run, the verdict file is still written.

## Trigger
The HUMAN explicitly invokes `/spec-lite`. The agent may never propose it or
reclassify work into it — deciding a change is "small enough to skip grilling"
is exactly the judgment call this harness exists to take away from the agent.

## Workflow
1. Write a minimal `spec.md`: the Outcome section (1–2 sentences) + a runnable
   Verification section. Set the Grilling record to
   `Status: LITE (human-invoked)`. If ANY ambiguity would change what gets
   built, STOP — this is not small; run `/spec` instead.
2. The human checks the approval box (still human-only, still required).
3. Note the base commit. Build the change — one small task, nothing else.
4. Run EVERY Verification-section command; all must exit 0. The Gate is not waived — only the
   fresh-eyes review is, and that waiver is the cost the human accepted by
   invoking this skill.
5. Commit the change. Then exit through the same door as every task: run the
   `wrap-up` skill in **lite scope** — ADR check, the `learn` scan (it writes
   THE verdict file with `"mode": "lite"` — the single writer, even here),
   `handoff.md` (commits: base → head), and `plan.md` (one task, `rejects: 0`,
   set `DONE` LAST), then the commit checkpoint. Only wrap-up marks `DONE`;
   the fast path waives grilling and fresh-eyes review, never the ledger.
6. Stop report. `WIP=1` still applies — no second change, no "while I'm here".

## Guardrails
- Human-invoked only. If you find yourself wanting this path, that is a signal
  to run `/spec`, not to ask for this.
- If the change grows mid-build, STOP and hand to `/spec` — do not stretch the
  definition of small.
- Verification runs in full and the verdict file is written — a lite task with
  no verdict file is as invalid as any other.

## Completion criterion
All Verification-section commands exited 0 in this session, the verdict file exists with
`"mode": "lite"`, and the stop report was printed.

## Output
The change, a minimal `spec.md`, updated `plan.md` + `handoff.md`, a verdict
file, and the stop report.

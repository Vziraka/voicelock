---
name: design
description: Turn a fuzzy idea into a build you can start — clarify it, choose an approach, and decompose it into an ordered roadmap of features. Use when you have an idea but aren't sure what to build or in what order, before any spec.
invocation: user
---
# Design (idea → roadmap)

The front door. `spec` assumes you already know the feature; `design` is for when
you don't. Its output is a `roadmap.md` — an ordered list of features — not code.

## Trigger
You have an idea and aren't sure what to build, how to shape it, or where to start.
(Already know the single feature? Skip this — run `/spec`.)

## Workflow
1. Read `constitution/universal.md`, `CONTEXT.md`, the `.out-of-scope/` folder
   (concept-match the idea against past rejections — surface any hit before
   proceeding), and — if the repo exists — `memory/codebase-map.md`.
2. **Sharpen the idea.** Run the `grilling` skill (one question at a time, each with
   your recommended answer) until you can state, in the user's own words: the problem,
   the outcome, who it's for, the constraints, the success signal, and the non-goals.
   If a question needs a *runnable* answer (you have to see it work), say so and spike
   a throwaway prototype before locking anything.
3. **Assess scope.** One thin feature, or many? If it's one, stop and hand to `/spec`.
   If it's bigger, continue.
4. **Choose an approach.** Propose 2–3 approaches with tradeoffs and a recommendation;
   the human picks. Any concrete technology named in an approach goes through
   `formats/TECH-PICK.md` (liveness evidence + plain-English walkthrough) before the
   pick. Every approved choice → one entry in `memory/decisions.md`; if it is also
   hard to reverse and a real tradeoff, record an ADR (`formats/ADR.md`).
5. **Decompose into tracer bullets.** Break the approach into **vertical slices** —
   each a thin path through *all* layers end-to-end, demoable on its own — NOT
   horizontal layers. Order them by dependency (blocked-by). "Make the change easy,
   then make the easy change" — put any prefactor first.
6. **Draw the intended architecture** as a Mermaid `flowchart` (boxes = components,
   arrows = data flow — the "how it connects" picture). Write `roadmap.md` (idea ·
   approach · **the diagram** · ordered features · out-of-scope), seed `CONTEXT.md`
   with the terms that emerged, and seed the `memory/codebase-map.md` diagram with the
   same boxes marked planned (dashed) until built. Quiz the human on granularity and
   dependencies; iterate until they approve.
7. **Close the session:** update `handoff.md` (next_action per the Output section
   below) per the universal [State] session-end rule, then run the **commit
   checkpoint** — stage the state files, show the human the proposed commit
   message, and on their approval commit (push only if a remote exists — say so).
   Record the session's base → head commit hashes in `handoff.md`, like every
   session does.

## Guardrails
- Design decides **what** and **in what order** — never how to code it. No file paths,
  no code (a prototype snippet that encodes a real decision is the only exception).
- An idea the human rejects during design gets one file in `.out-of-scope/`
  (what · why · when it came up) so it never gets re-proposed.
- Every feature is a vertical slice that is demoable on its own. "Just the schema" is a
  horizontal slice — not a feature.
- Keep the diagram high-level — major components and data flow, not every function.
- Keep this in one unbroken session so grilling → approach → roadmap build on the same
  thinking. Each `/spec` afterward starts fresh.

## Completion criterion
`roadmap.md` exists with the idea in the user's words, the chosen approach, a Mermaid
architecture diagram, an **ordered** feature list where **every feature is a demoable
vertical slice with its blocked-by named**, and a non-goals list — and the human
approved the breakdown.

## Output
`roadmap.md` (with the architecture diagram) + a seeded `CONTEXT.md` and
`codebase-map.md` diagram. Then:
- **new / empty repo** → "Roadmap set — run `/intake-scaffold` to lock the stack, then `/spec` on Feature 1."
- **existing repo** → "Roadmap set — run `/spec` on Feature 1 to start."

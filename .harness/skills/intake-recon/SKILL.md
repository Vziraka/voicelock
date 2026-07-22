---
name: intake-recon
description: Onboard the harness into an EXISTING codebase by extracting its real conventions and mapping it. Use once, on the first run in a brownfield repo, before any spec.
invocation: user
---
# Intake — Recon (brownfield)

The code is the truth. Your job is to read it and write down what's already true —
not to impose anything.

## Trigger
First run of the harness in a repo that already has code.

## Workflow
1. Read `constitution/universal.md` and `manifest.json`. **Git check:** if this
   repo is not under git, say so and run `git init` before proceeding — every
   checkpoint in the harness depends on it (an existing codebase without git
   also deserves the human's attention: flag it). Then run the `setup` skill —
   the environment interview. It writes the Environment section into
   `constitution/project.md` and offers the adapter install. Gate: do not
   proceed to the steps below while that section is missing.
2. Survey in parallel: top-level structure, package manifests, lint/format/test
   configs, CI files, existing READMEs/docs. Build `memory/codebase-map.md`, including
   a Mermaid `flowchart` of the **actual** architecture (boxes = components, arrows =
   data flow). Keep it high-level; if the repo is large, draw one diagram per subsystem
   instead of a single hairball. **CUI quarantine (only when the register in
   `constitution/topics/cui.md` is ACTIVE):** anything the survey finds that
   matches a register category or forbidden pattern goes on a candidates
   list shown to the human BEFORE any file is written — each candidate gets
   a code name or an explicit all-clear; the map, conventions, and CONTEXT
   are then written with code names.
3. Extract conventions from the real code — naming, structure, style — and the
   actual test/lint/build commands. Write `constitution/topics/conventions.md`;
   mirror the non-negotiables into `constitution/project.md`.
4. Extract the project's domain terms → seed `CONTEXT.md` (term · definition · _Avoid_).
5. Anything ambiguous: run the `grilling` skill (one question at a time).
6. Install the root signpost per the Environment section's **Signposts**
   answer: copy `adapters/AGENTS-template.md`'s template to the repo root as
   `AGENTS.md` and `CLAUDE.md` (the default), or as the single chosen file
   (merge, don't overwrite, if the repo already has it).
7. **Close the session:** update `handoff.md` (next_action: `/design` or `/spec`
   in a fresh session) per the universal [State] session-end rule, then run the
   **commit checkpoint** — stage the state files, show the human the proposed
   commit message, and on their approval commit (push only if a remote exists —
   say so). Record the session's base → head commit hashes in `handoff.md`,
   like every session does (first commit of a fresh repo: base is
   `none — initial`, and the head hash lands via a follow-up state-only
   bookkeeping commit — a commit cannot contain its own hash).

## Guardrails
- Cite a real `file:line` for every convention you record. Never invent one.
- Record conventions only. Guardrails are the `learn` skill's job, not yours.
- The diagram reflects what the code *actually does*, not what it should do.

## Completion criterion
`memory/codebase-map.md` (with an architecture diagram), `conventions.md`, the
`project.md` conventions, and `CONTEXT.md` are filled, **each detected convention cites
a real example**, and the human has confirmed them.

## Output
The four files, a one-screen summary, and: "Intake complete — run /spec to
start work." End with one line for the human — "Next for you: describe what
to build (/spec), or /design for a rough idea." If the Environment section
says first-time user, add: "(New here? `GUIDE.md` walks the loop.)"

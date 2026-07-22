---
name: intake-scaffold
description: Onboard the harness into a NEW or empty repo by having the human declare its conventions. Use once, on the first run in a greenfield project, before any spec.
invocation: user
---
# Intake — Scaffold (greenfield)

Nothing exists yet, so conventions are declared, not extracted.

## Trigger
First run of the harness in a new or empty repo.

## Workflow
1. Read `constitution/universal.md` and `manifest.json`. **Git check:** if this
   folder is not a git repository, say so and run `git init` before
   proceeding — every checkpoint in the harness depends on it. Then run the
   `setup` skill — the environment interview. It writes the Environment
   section into `constitution/project.md` and offers the adapter install.
   Gate: do not proceed to the steps below while that section is missing.
2. Run the `grilling` skill to have the human declare: stack, naming, structure,
   test/lint/build commands, and the first domain terms. One question at a time,
   each with your recommended default.
3. Write `constitution/topics/conventions.md`, mirror non-negotiables into
   `constitution/project.md`, seed `CONTEXT.md`, and start
   `memory/codebase-map.md`. Offer a minimal `.gitignore` for the declared
   stack. When the CUI register (`constitution/topics/cui.md`) is ACTIVE,
   sensitive declared values get code names from birth, with real values
   read from config files outside git.
4. Install the root signpost per the Environment section's **Signposts**
   answer: copy `adapters/AGENTS-template.md`'s template to the repo root as
   `AGENTS.md` and `CLAUDE.md` (the default), or as the single chosen file —
   so every future agent routes into the harness automatically.
5. State plainly: the declared commands are promises until they run — **the
   first task of the first feature makes them actually run** (install the test
   runner, wire up lint). The Gate has no teeth until that task passes.
6. **Close the session:** update `handoff.md` (next_action: `/design` or `/spec`
   in a fresh session) per the universal [State] session-end rule, then run the
   **commit checkpoint** — stage the state files, show the human the proposed
   commit message, and on their approval commit (push only if a remote exists —
   say so). Record the session's base → head commit hashes in `handoff.md`,
   like every session does (first commit of a fresh repo: base is
   `none — initial`, and the head hash lands via a follow-up state-only
   bookkeeping commit — a commit cannot contain its own hash).

## Guardrails
- Declare, don't assume. If the human is unsure, propose a sensible default and
  mark it as a default (so it can be revisited).

## Completion criterion
The four files (`topics/conventions.md`, `constitution/project.md`,
`CONTEXT.md`, `memory/codebase-map.md`) are filled and confirmed, and the
test/lint/build commands are named (the Gate needs them).

## Output
The four files and: "Scaffold complete — run /spec to start work." End with
one line for the human — "Next for you: describe what to build (/spec), or
/design for a rough idea." If the Environment section says first-time user,
add: "(New here? `GUIDE.md` walks the loop.)"

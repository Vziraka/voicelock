---
name: setup
description: The environment interview — record which tool, model, and choices this repo runs with, before intake writes anything. Reached by both intake skills; re-run it directly anytime an answer changes.
invocation: model
---
# Setup (environment interview)

Seven questions, each with a recommended default — accepting every default is
a valid path (about two minutes). Answers are RECORDED, never silently acted
on: they land in `constitution/project.md`'s Environment section, where every
future session reads them. The rules never change per answer; what the rules
read does.

## Trigger
Invoked by `intake-recon` / `intake-scaffold` right after their git check —
before any file is written. A human may also invoke it directly later to
revise an answer (it updates the Environment section in place, dated).

## Workflow
Run the `grilling` skill over these questions, in order, one at a time, each
with its recommended default:
1. **Tool** — which AI tool runs this repo now, and could a different one
   take over later? (Recommend: assume yes.)
2. **Model** — which model(s)? Recorded for future adapter work.
   (Recommend: record whatever is running right now.)
3. **Subagents** — can this tool spawn a clean-context subagent (the
   fresh-eyes verifier)? Auto-detect where possible and confirm. Record the
   verifier path: `subagent` or `fresh-session` — the implement skill's
   no-subagent fallback reads this instead of discovering it mid-task.
4. **Signposts** — install both root files, `AGENTS.md` + `CLAUDE.md`
   (recommended: the tool that runs intake is not guaranteed to be the next
   tool in this repo), or one? A single-file choice is allowed — record it
   WITH its risk: a future session in the other tool will not be routed.
5. **Git remote** — local history only (default), or wire a remote now? If
   remote: add it once; the existing checkpoint rules handle pushes from
   here on.
6. **Sensitive data** — any secrets or identifiers that must never appear in
   files or commits? None → record "none declared". Some → record the rule:
   secrets live in config files outside git, never in specs/plans/handoffs.
   Heavy or regulated (CUI-class) → activate the locked-down mode: run the
   register interview from `constitution/topics/cui.md` (categories →
   forbidden patterns, compliance approver, research tier — R0 recommended),
   set the register's Status to ACTIVE, generate the translation-sheet
   skeleton as chat output with its storage instructions (the sheet itself
   NEVER enters the repo), and point the human at `docs/CUI.md`.
7. **First time?** — new to this harness? Yes → point to `README.md` (and
   its stuck-recovery runbook) and recommend Mode 1 for the first feature.
   No mechanics change either way.

Then:
8. Write the **Environment** section into `constitution/project.md` (its
   template shows the format) and quote it back.
9. **Offer the adapter install** where one exists for the recorded tool
   (Claude Code: `adapters/claude-code/README.md` — copies the skills into
   `.claude/skills/` so `/commands` become real). On yes, do the install and
   list what was copied. On no, state that commands stay manual ("read the
   skill file and follow it").
10. Return to the calling intake skill.

## Guardrails
- Setup gates intake: conventions and signposts must not be written until
  the Environment section exists with the Tool line filled.
- Every behavior that branches on an answer reads the Environment section,
  not chat memory.
- Re-running setup updates the section in place and re-dates it — never a
  second copy.

## Completion criterion
The Environment section exists in `constitution/project.md` with all seven
answers, quoted back, and the adapter install was offered (done, declined,
or unavailable — stated).

## Output
An updated `constitution/project.md` (Environment section) and, if accepted,
an installed adapter.

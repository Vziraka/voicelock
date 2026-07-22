# AGENTS-template — copy to repo root as `AGENTS.md` AND `CLAUDE.md`

Intake (recon or scaffold) installs this at the repo root so every agent —
any tool — gets routed into the harness automatically. Keep it a signpost,
never a second rulebook: the two must not disagree, so this one only points.

--- template below (copy verbatim, fill {nothing}) ---

# This repo is harness-governed

Before doing anything else, read `.harness/constitution/universal.md` and
follow its read order. All work runs through the harness loop
(`.harness/docs/COMMANDS.md`).

The current feature runs at a development **Mode** (1–4) — read it from
`.harness/spec.md`'s Approval gate before acting; it decides what waits for
the human. If your tool has NO clean-context subagent, never self-verify:
at the verify step, commit state, write the handoff, and stop for a
fresh-session verifier.

Files listed in `.harness/protected.txt` are human-only.
State lives in files, not in chat — see the write-before-proceed rule.

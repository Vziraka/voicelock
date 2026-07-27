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

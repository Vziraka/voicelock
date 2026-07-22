# Claude Code adapter

The core harness is tool-agnostic markdown — that stays true (a mid-run
handover to another tool has been survived in testing precisely because of
it). This adapter wires the harness into Claude Code's two native features:
skill discovery and subagents.

## Install (once per repo) — makes `/implement` etc. real commands

Claude Code only discovers skills in `.claude/skills/`; the harness keeps its
canonical copies in `.harness/skills/`. Without this step, typing `/implement`
fails with "Unknown skill" and every guardrail depends on the agent
voluntarily hunting down the markdown — enforcement becomes opt-in. So:

1. Copy each `.harness/skills/<name>/` folder into `.claude/skills/<name>/`
   (create `.claude/skills/` if missing). A junction/symlink per skill folder
   is better if your setup allows it — then there's only one copy to maintain.
2. If you copied (no links): re-run the copy whenever `.harness/skills/`
   changes — a version bump's sync-impact list tells you when. Stale copies
   are worse than no copies; when in doubt, re-copy all.
3. The intake skills install the root `AGENTS.md` / `CLAUDE.md` signpost
   separately (`adapters/AGENTS-template.md`) — that routes agents to the
   constitution; this step routes slash commands to the skills. You want both.

The `setup` skill (run during intake) offers to perform this install for
you — accepting there is the same as doing these steps by hand.

The canonical home stays `.harness/skills/` — propose harness changes there,
never by editing the `.claude/skills/` copies.

## Inline verification via subagents

A subagent gets a CLEAN context window: it never sees the implementor's
conversation or reasoning, which is what "fresh eyes" actually requires. A new
chat session and a clean-context subagent are therefore equivalent; use
whichever is less friction.

Flow (one session per task, Mode 1 touchpoints shown):
1. `/implement` finishes: task at `REVIEW`, the two local commits made (build,
   then bookkeeping — the Gate's base→head range is in `handoff.md`), stop
   report printed.
2. Human says **"verify"** (touchpoint 1). At Modes 2–4 the session proceeds
   on its own — no touchpoint here.
3. The session spawns a subagent using `formats/VERIFIER-PROMPT.md` VERBATIM —
   fill only `{task id}`, `{base}`, `{head}`.
4. The subagent runs Gate + Review with clean context and returns the verdicts
   (including which MECHANISM it ran as — the verdict file records it).
5. The parent executes the result: `wrap-up` on APPROVE, feedback + `TODO` on
   REJECT — then the **commit checkpoint** (touchpoint 2 at Mode 1: message
   shown, wait for approval, commit AND push; at Modes 2–4: local commit
   without waiting, push gated at the feature-end checkpoint).

## Rules that keep this honest
- The verifier prompt is used verbatim — no additions, no "helpful context"
  from the implementor. Known template defects are flagged to the human before
  spawning, never fixed silently and never left unsaid.
- The parent never overrides the subagent's verdict; wanting to = ESCALATE_HUMAN.
- If your tool has no subagents, fall back to the classic path: a fresh session
  running `/verify-gate` then `/verify-review` — the template's closing frame
  covers that path too (the fresh session does its own bookkeeping).

## Not included (yet): hooks
Stop / PreToolUse / PostToolUse hooks could mechanically enforce state-file
updates, commit checkpoints, and protected-file immutability — prose cannot.
Deliberately skipped in v0.3 (hybrid decision, 2026-07-13). If context drift
returns despite the write-before-proceed rule, hooks are the next lever.

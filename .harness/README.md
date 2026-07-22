# SDD Harness

*(Version lives in `manifest.json` — the single owner; this title carries none
on purpose, after the banner went stale twice.)*

**New here? `GUIDE.md` walks your first feature start to finish.**

> **The v0.4.1 freeze is lifted** (human ruling 2026-07-16, quota met). v0.5
> was designed from the ranked pattern across two validation runs — a 25-session
> simulated stress run and a real human-driven dogfooding run — exactly as the
> freeze intended. See `docs/CHANGELOG.md` for the full change list.

A spec-driven development harness. Drop this folder into any repo as `.harness/`.
Works with any AI tool that reads and writes files (Claude Code, Cursor, Gemini
CLI, Codex, …). No servers; one optional install step wires the skills into
Claude Code as real slash commands (`adapters/claude-code/`).

**New in v0.5 — development Modes.** You choose, per feature, how hands-on to
be: **Mode 1** (supervised — every gate waits), **Mode 2** (trusted cycles —
the default), **Mode 3** (spec-to-done — you approve the spec; the feature
runs to DONE and waits for you at the feature-end checkpoint with its
completion report and the commit/push approval), **Mode 4** (continuous
roadmap — Mode 3 plus the next spec drafted and parked at your approval gate;
unlock rule in the universal Modes section). Spec approval, spec amendments,
and escalations stay human-only in every mode. The contract lives in
`constitution/universal.md`.

**Designed for frontier models.** Weaker models can run it — the Gate is
deterministic and the entry gates are simple file checks — but the file-based
rules cannot enforce authorship or session identity, so with a weaker model
*more* rides on the [human duties](#human-duties--the-seven-steps-only-you-can-enforce)
below, not less. (A runtime-hook adapter is the eventual fix for unattended use.)

**Full command list → see [`docs/COMMANDS.md`](./docs/COMMANDS.md).**

## The idea
Stop chatting with the AI. Run a loop — **spec → plan → build → verify → learn** —
with state kept in files so no single session has to hold it all, and a fresh-eyes
**Verifier** that won't grade its own homework.

## It scales to your level
- **Core loop (everyone):** `spec → plan → implement → verify`. This is what makes it spec-driven.
- **Optional on-ramps:** `/design` when you have a fuzzy idea but aren't sure *what* to
  build, and `/explain` when the agent uses tech you don't know. Experts skip both;
  learners lean on them. Same harness.

## How you use it
The walkthrough below shows **Mode 1** (every gate waits for you). At Modes
2–4 the same loop runs with fewer pauses — the agent chains tasks, spawns the
verifier itself, and commits locally without waiting; you meet it at spec
approval, escalations, and the feature-end checkpoint.
1. **First time:** *"read `.harness/constitution/universal.md` and run intake."* It
   extracts your conventions (existing repo) or has you declare them (new repo), and
   draws an architecture diagram into `memory/codebase-map.md`.
2. **Fuzzy idea?** *(optional)* Run `/design` — it grills the idea and produces
   `roadmap.md` (ordered features + a diagram). Skip it if you already know the feature.
3. **Per feature:** the agent drafts `spec.md`, grills you one question at a time, and
   you check the approval box. Then `/plan` breaks it into one-at-a-time tasks.
4. **Build** one task in one session — the agent auto-commits locally (the
   Gate's diff range) and stops cold at review. Say **"verify"**: a
   clean-context verifier (a subagent spawned from `formats/VERIFIER-PROMPT.md`
   verbatim, or a fresh session — both count as fresh eyes) runs the
   deterministic **Gate** (your commands) then the two-axis **Reviewer**
   (defaults to REJECT).
5. On approve, the agent runs **wrap-up** automatically: updates `plan.md`,
   `roadmap.md`, ADRs, `memory/decisions.md` and `handoff.md` (quoting each
   write as proof), runs the `/learn` compound scan — then the **commit
   checkpoint**: it shows you the proposed commit message, waits for your
   approval, and only then commits and pushes. Run `/curate` now and then to
   keep the rulebook lean.

> Diagrams are **Mermaid** — view them *rendered* (VS Code preview, GitHub, or
> [mermaid.live](https://mermaid.live)), not as raw text.

## Human duties — the seven steps only you can enforce
The harness is markdown; these seven have no artifact that can check them. Skip
one and a promise silently breaks.
1. **Read the spec before checking "Approved by human."** It is the only
   independent check on the agent-graded ambiguity scan. In a Mode 4 draft,
   this includes actually THINKING about each embedded question — the gate can
   force them answered, not thought about.
2. **Keep the verifier clean-context.** Either a subagent spawned with
   `formats/VERIFIER-PROMPT.md` *verbatim*, or a genuinely new session — never
   the implementor judging its own diff inline, and never a "customized"
   verifier prompt.
3. **Honor the mode you picked.** At Mode 1: new session + explicit "go"
   before the next task — never "keep going" in a warm session. At Modes 2–4:
   resist the urge to interrupt mid-feature with chat instructions — a change
   of mind goes through the amendment path or a mode lowering, in the files.
4. **Read the stop report (Mode 1) or the completion report (Modes 3–4).** If
   `plan.md` says `DONE` but `handoff.md`'s Wrap-up line says "not run",
   re-invoke `wrap-up`.
5. **Approve or decline guardrail proposals** (check handoff.md's *Pending
   guardrail* line) and run `/curate` every ~10 tasks — curate also scans the
   judgment-call log (`memory/deviations.md`) for rules that keep needing
   reinterpretation.
6. **Only you may invoke `/spec-lite`**, and only for genuinely small changes —
   the agent judging a change "small enough" is the failure mode this harness
   was built to remove.
7. **Only you set the Mode**, in the spec's Approval gate — and never raise it
   mid-feature. "Just let it run" typed in frustration is the exact pressure
   the mode ladder exists to absorb calmly at spec time.

## When the harness stops on you (`BLOCKED` / `ESCALATE_HUMAN`)
A stop is the harness working, not failing. The runbook:
1. Read the stop report and `handoff.md` — they name what blocked and why
   (missing env, budget exceeded, retry cap hit, an unfollowable rule).
2. Decide the unblock, and put it in the FILES, not in chat: fix the
   environment · amend the spec (full amendment path, box-2 re-check) · lower
   the mode (one line in the spec + a deviations entry) · re-plan the task.
3. A retry-capped task's `rejects:` counter stands — resuming it is a human
   decision recorded in the feedback log, never a silent counter reset.
4. Resume with an explicit "go" in a fresh session. At Modes 2–4 the standing
   go does NOT survive an escalation — your new "go" is required.

## What you need
- Any file-capable AI tool.
- **git** — checkpoints and rollback.
- Runnable check commands in your project (test / lint / build) — that's what the Gate runs.
- You, in the loop. This is high-control by design.

## Layout
- `GUIDE.md` — the first-feature walkthrough (start here if you're new).
- `docs/` — reference docs: `ARCHITECTURE.md` (lifecycle + file map diagrams), `CANON.md` (load-bearing-sentence registry), `CHANGELOG.md` (version log with sync-impact lines), `COMMANDS.md` (every command).
- `FAILURES.md` — the failure log; stays at root on purpose (it teaches the discipline).
- `variants/` — master-only: blueprints for generating the give-away and CUI copies; never ships.
- `constitution/` — the rules: `universal.md` (router) + `project.md` (per-repo, learns) + `topics/`.
- `roadmap.md` — the feature sequence for a whole idea (from `/design`).
- `spec.md` · `plan.md` · `handoff.md` — current feature, its tasks, and session state.
- `CONTEXT.md` — the project's shared glossary.
- `formats/` — reference formats: ADR, TECH-PICK (dependency vetting), VERIFIER-PROMPT (the fixed fresh-eyes template), source-playbooks/ (where to research, per scenario).
- `memory/` — the codebase map (+ architecture diagram), the append-only decision log, cited research findings, the append-only verdict archive (+ dormant calibration loop), and the append-only judgment-call log (`deviations.md` — where rule conflicts get logged instead of silently reinterpreted).
- `.out-of-scope/` — institutional memory of rejected ideas; design/spec check it so nothing rejected gets re-proposed.
- `adapters/` — tool-specific wiring (Claude Code inline verification, root AGENTS.md template installed by intake).
- `protected.txt` — files only a human may edit.
- `skills/` — the modular instructions (the 16 commands; see `docs/COMMANDS.md`).

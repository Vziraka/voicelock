# Project Constitution — VoiceLock

Per-repo rules. This file **learns**: conventions go in once (from intake);
guardrails accrue over time (from failures). Keep it curated — see the `curate`
skill. Specific lessons live here, never in `universal.md`.

## Environment (written by the setup skill — revise via setup, not hand-drift)
- Tool(s): Cursor only · Model(s): Cursor Grok 4.5
- Verifier path: subagent
- Signposts: AGENTS.md only — risk: Claude Code sessions will not be auto-routed
- Remote: none — local history
- Sensitive data: none declared
- First-time user: yes — Mode 1 recommended first
- Setup run: 2026-07-21

## Conventions
Extracted by `intake-recon` (existing repo) or declared by `intake-scaffold` (new
repo). The non-negotiables go here; the full detail lives in
`constitution/topics/conventions.md`.

- Naming: {e.g. snake_case files, PascalCase types}
- Structure: {e.g. tests next to source}
- Stack rules: {e.g. reuse the existing Redis client; no new dependencies without approval}

## Earned guardrails
Last curated: never · verdicts then: 0

Each entry = one failure turned into a rule. Keep them few and current — the
`curate` skill dedups and retires expired ones.

Format:
- **[Category]** Rule in one line. `severity` · expires: {YYYY-MM-DD}
  - _Evidence:_ the failure this came from (so it can be reviewed and retired).
  - _Added:_ {YYYY-MM-DD}

<!-- example — delete when the first real rule lands
- **[Forbidden]** Never set SSH ingress to 0.0.0.0/0 outside a lab. `block` · expires: 2026-12-31
  - _Evidence:_ a session proposed open SSH as a convenient "default".
  - _Added:_ 2026-06-28
-->

(Empty until the harness learns something. Do not pre-fill.)

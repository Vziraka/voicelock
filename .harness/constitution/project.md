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

- Naming: snake_case files/functions/variables, PascalCase classes,
  `tests/test_<module>.py`; prefer CONTEXT.md terms in identifiers.
- Structure: code in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in
  `tests/`, design mock reference in `design/` (not final UI).
- Stack rules: Python 3.11 + uv only (no bare pip); JS UI for looks, Python for
  brain; UI shell TECH-PICK at F1; **offline-only — no network at runtime**;
  no new dependencies without human approval.
- Division of labor: Python owns audio/DSP/crypto/state; JS owns rendering only.
- Gate commands: `uv run ruff check .` and `uv run pytest`, both exit 0
  (promises until F1 wires them).

## Earned guardrails
Last curated: 2026-07-26 · verdicts then: 19

Each entry = one failure turned into a rule. Keep them few and current — the
`curate` skill dedups and retires expired ones.

Format:
- **[Category]** Rule in one line. `severity` · expires: {YYYY-MM-DD}
  - _Evidence:_ the failure this came from (so it can be reviewed and retired).
  - _Added:_ {YYYY-MM-DD}

- **[Forbidden]** Never add a helper, method, or branch that no caller and no test exercises — delete it and let the task that genuinely needs it introduce it. `warn` · expires: 2027-01-31
  - _Evidence:_ three REJECTs in F4 (2026-07-26), all the same defect: `BoothApi.reset_enroll_takes()` added in Task 3 with zero callers and zero tests; `lock_voiceprint()`'s `hop == 0` branch in Task 4, reachable only for a take of exactly 19 200 samples and driven by no test; and an enroll "BRIDGE MISSING" branch in Task 5 that the same diff made unreachable. Each cost a full verify cycle. Note the rule is "introduce at the point of use", not "never add helpers" — the same `reset_enroll_takes()` was correctly restored in Task 5 once the UI called it in three places and two tests covered it.
  - _Added:_ 2026-07-26 (human-approved)

- **[Forbidden]** The UI must not keep its own copy of state the engine owns — render the engine's value instead of a local mirror. `warn` · expires: 2027-01-31
  - _Evidence:_ F4 Task 5 (2026-07-26) — `resetEnrollVoiceStep()` zeroed a JS take-counter while the bridge kept its banked takes, so the panel showed `0 / 5` over a non-empty engine and the next enrollment would have sealed abandoned takes — possibly a different person's — into the vault. Caught as a CORRECTNESS reject by the Task 5 verifier. Relevant beyond that bug: F5–F8 add FaceView, liveness and more UI state to a project whose stated convention is already "Python owns state; JS renders only".
  - _Added:_ 2026-07-26 (human-approved; proposed by F4 Task 5's `learn` scan and carried unapproved across two handoffs)

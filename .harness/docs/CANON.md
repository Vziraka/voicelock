# Canon — load-bearing sentences and their owners

Each rule below lives in exactly ONE file (its owner). Every other file
references it by name and never restates it — a paraphrased copy is drift
waiting to happen. `/curate`'s defrift check greps each of these and flags any
near-copy found elsewhere.

| # | Rule (short name) | Canonical sentence lives in |
|---|---|---|
| 1 | WIP=1 (one task at a time, in every mode) | `constitution/universal.md` — [Forbidden] hard rule |
| 2 | Grilling CLEAR gate | `constitution/universal.md` — [Startup] hard rule |
| 3 | Verdicts append-only | `protected.txt` — the `memory/verdicts/` entry |
| 4 | DONE requires a verdict file | `constitution/universal.md` — [Done] hard rule |
| 5 | Write-before-proceed | `constitution/universal.md` — [State] hard rule |
| 6 | Clean-context verification | `constitution/universal.md` — the Loop section |
| 7 | Human checks approval box 2 | `spec.md` — section 0, Approval gate |
| 8 | Verifier prompt used verbatim | `formats/VERIFIER-PROMPT.md` — header |
| 9 | Mode ladder, the always-human gates, and the Mode 4 unlock | `constitution/universal.md` — Modes section |
| 10 | Unfollowable rule: Modes 3–4 stop, Modes 1–2 log first | `constitution/universal.md` — [Modes] hard rule |
| 11 | State-file precedence on conflict | `constitution/universal.md` — [State] precedence rule |
| 12 | Retry budget: 3 attempts then BLOCKED, every mode | `constitution/universal.md` — [Modes] hard rule |
| 13 | Durable DOING: committed before building | `skills/implement/SKILL.md` — step 3 |
| 14 | Two-commit rule (build, then bookkeeping) | `skills/implement/SKILL.md` — step 6 |
| 15 | Executor owns post-verdict bookkeeping (one session, never both) | `formats/VERIFIER-PROMPT.md` — closing frame |
| 16 | Code-quality floor (the universal bar every diff meets) | `constitution/topics/code-quality.md` |
| 17 | CUI tripwire + research-tier rules (in force only while ACTIVE) | `constitution/topics/cui.md` — Rules block |

Changing a canonical sentence = a harness version bump + a `docs/CHANGELOG.md`
entry whose sync-impact line names every file that references it.

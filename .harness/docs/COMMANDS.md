# Commands

Every skill in this harness, grouped by when you reach for it. All paths are
relative to `.harness/`.

**How invocation actually works — read this once.** The skills are markdown
files in `skills/`; they are NOT installed slash commands out of the box. Two
ways to run one:
1. **Any tool (always works):** tell your agent *"read
   `.harness/skills/<name>/SKILL.md` and follow it"*. The agent must actually
   open the file — the guardrails live inside it, not in this table.
2. **Claude Code, after the adapter install** (`adapters/claude-code/` — copies
   the skills into `.claude/skills/` so they're discovered): type `/name`.

Ones marked **optional** you can skip entirely.

## Modes — how hands-on the human is
Chosen per feature in the spec's Approval gate; approving the spec approves the
mode. The contract lives in `constitution/universal.md` (Modes section).
- **Mode 1 — Supervised:** every gate waits for you.
- **Mode 2 — Trusted cycles** *(default)*: build↔verify cycles run
  back-to-back inside an approved feature; you approve the spec and review the
  feature's final verdict.
- **Mode 3 — Spec-to-done:** you approve the spec; the agent runs the feature
  to DONE and you read a completion report.
- **Mode 4 — Continuous roadmap:** Mode 3, plus the next feature's spec is
  drafted (questions embedded) and parked at your approval gate. Unlock rule:
  see the universal Modes section (its line is the single source).
Spec approval, spec amendments, and escalations are human-only in every mode.

## ① Onboarding — once per repo
| Command | Use when… | What it does |
|---|---|---|
| `/intake-recon` | first time in an **existing** codebase | reads the code, extracts conventions, builds the map + architecture diagram + `CONTEXT.md` |
| `/intake-scaffold` | first time in a **new / empty** repo | grills you to declare stack, conventions, and the Gate's commands |

*(Just say "run intake" — it picks recon vs scaffold by whether code exists.)*

## ② Idea → plan — per idea · **optional**
| Command | Use when… | What it does |
|---|---|---|
| `/design` | you have an idea but aren't sure **what** to build or in what order | grills it, picks an approach, writes `roadmap.md` (ordered features + diagram); on a new repo, hands off to `/intake-scaffold` |

## ③ Define a feature — per feature
| Command | Use when… | What it does |
|---|---|---|
| `/spec` | you know the **specific feature** | drafts an approved, runnable `spec.md`; stops if a new repo skipped scaffold |
| `/spec-lite` | the change is **genuinely small** and YOU say so (typo, config value, one-liner) | minimal spec + build + Gate in one sitting; **human-invoked only — the agent may never suggest it** |
| `/plan` | the spec is **approved** | breaks it into small, ordered, one-at-a-time tasks |

## ④ Build ↔ verify — per task, with **fresh eyes** (subagent or fresh session)
| Command | Use when… | What it does |
|---|---|---|
| `/implement` | a task is `TODO` (build session) | builds **one** task (committed `DOING` first, two commits after), writes handoff, then hands to the clean-context verifier from `formats/VERIFIER-PROMPT.md` — waits for your "verify" at Mode 1, proceeds itself at Modes 2–4 |
| `/verify-gate` | task is `REVIEW` (clean-context verifier, runs first) | runs your commands within their runtime budgets, checks exit codes — deterministic, no opinions |
| `/verify-review` | right after the Gate passes | two-axis judgment (**Spec** + **Standards**), defaults to REJECT; on approve, the verdict's executor chains into `wrap-up`; every verification ends with a **commit checkpoint** — message approval + push at Mode 1, local commit at Modes 2–4 (push waits for the feature-end checkpoint) |

## ⑤ Get smarter — over time
| Command | Use when… | What it does |
|---|---|---|
| `/learn` | (auto in every wrap-up) or a **systemic** failure | compound scan of the task; at most one evidence-anchored guardrail (you approve) |
| `/curate` | the rulebook is **getting big** (~every 10 tasks) | prunes / dedups / retires guardrails |

## ⑥ Understand — anytime · **optional**
| Command | Use when… | What it does |
|---|---|---|
| `/explain` | the agent uses a **tool/term you don't know** | plain-English *job · tradeoff · blast radius*, then records it in `CONTEXT.md` |
| `/research` | a decision hinges on a **fact outside the repo** (library, API, ecosystem) | loads the matching source playbook, investigates primary sources only, writes cited + dated findings to `memory/research/` |

## ⑦ Internal — you rarely type it
| Command | Use when… | What it does |
|---|---|---|
| `grilling` | (the agent calls it) | the one-question-at-a-time interview inside `design` / `spec` / `intake` |
| `setup` | (intake calls it; re-run to revise an answer) | the 7-question environment interview — records the Environment section in `constitution/project.md`, offers the adapter install |
| `wrap-up` | (verify-review calls it on APPROVE) | the mandatory end-of-task checklist: plan/roadmap/ADR/handoff updated with proof, learn scan run, then STOP |

## The typical cycle (Mode 1 shown — the fully supervised shape)
```
run intake  (once)
  → /design → roadmap.md                       (optional)
    → /spec (grilling gate: record must be CLEAR; you set the Mode) → /plan
      → [fresh session] /implement → committed DOING → build → two commits
        → STOPS at one task
      → [fresh eyes: subagent via VERIFIER-PROMPT, or fresh session]
        /verify-gate → /verify-review
        → APPROVE → wrap-up (state files + learn scan, DONE written last)
                    → commit checkpoint (you approve message → commit + push)
                    → STOP, await human go
        → REJECT  → feedback into plan.md, task back to TODO
                    → commit checkpoint (3 failed retries = BLOCKED)
    → next task/feature — only on your explicit "go", new session
  → /curate   (periodically)
  → /explain  (anytime you hit an unknown)
```
At Modes 2–4 the same loop runs, but the agent pushes it between gates itself:
tasks chain after each completed wrap-up, the verifier is spawned without
waiting for "verify", and local commits don't pause for message approval —
the human touchpoints compress to spec approval, escalations, and the
feature-end checkpoint (final-verdict review at Mode 2; completion report at
Modes 3–4).

## Which one do I want?
- *idea, not sure how to build it* → `/design`
- *I know the feature* → `/spec`
- *tiny change, I take responsibility for skipping grilling* → `/spec-lite` (only you may pick this)
- *spec approved, break it up* → `/plan`
- *build the next task* → `/implement` (fresh session at Mode 1; the session
  chains it itself at Modes 2–4)
- *check the last task* → `/verify-gate` then `/verify-review` (always fresh
  eyes: subagent or fresh session, every mode)
- *is this library/approach actually good, currently?* → `/research`
- *that mistake keeps happening* → `/learn`
- *the rulebook's bloated* → `/curate`
- *don't know a tool the agent used* → `/explain`
- *changed tools / want a remote / revise an environment answer* → `setup`
- *brand-new repo* → run intake

## Not built (ideas only — nothing below exists, do not reference these as if they do)
`/diagnose`, `/domain-modeling`, a `git-guardrails` hook, `/ask`. *(Rejected-idea
memory shipped in v0.4 as the `.out-of-scope/` folder — no skill needed.)*

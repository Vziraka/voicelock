---
name: research
description: Investigate a question against primary sources and write the findings to a cited, dated file. Use when a decision hinges on a fact about the ecosystem, a library, an API, or anything the model might otherwise answer from training data.
invocation: user
---
# Research (primary sources, cited findings)

Training data is a rumor about the past. Research replaces it with sources that
own their claims. The one rule that matters most: **load the matching source
playbook before any search** — strategy first, then searching.

## Trigger
You — or `TECH-PICK` / `grilling` mid-flow — hit a question whose answer lives
outside this repo: library facts, API behavior, ecosystem state, "what's the
current way to do X".

## Workflow
1. Load the matching playbook from `formats/source-playbooks/`
   (library-evaluation · debugging · api-how-to). If none fits, say so and name
   the sources you'll use instead — then proceed.
2. Investigate against **primary sources** — official docs, changelogs,
   registries, source code — not secondary write-ups of them. Follow every
   claim back to the source that owns it.
3. Write findings to `memory/research/{YYYY-MM-DD}-{topic}.md`: one claim per
   line, each with its source link and the date of the evidence. Note where the
   research contradicted your first instinct — that delta is the whole point.
4. **Gray zone = FAIL.** A claim you could not confirm is recorded as
   `unconfirmed` — never smoothed into the findings.

## Guardrails
- Quote dates, versions, and numbers. "Actively maintained" is not evidence;
  "v5.2 released 2026-05-12 (releases page)" is.
- If you could not actually search (no web access this session), label every
  claim "training data, unverified" instead of dressing memory up as research.
- Findings files are never edited after writing — a newer file supersedes.
- CUI: when `constitution/topics/cui.md` is ACTIVE, follow its recorded
  research tier (the register owns the tier definitions) — R0 means no
  external calls at all; R1 means generic-terms-only queries shown to the
  human before running and logged in the findings file.

## Completion criterion
A findings file exists, every claim carries a source + date (or an explicit
`unconfirmed`), and the caller can check any claim in under a minute.

## Output
`memory/research/{date}-{topic}.md`, plus a one-paragraph answer to the
question that prompted the research.

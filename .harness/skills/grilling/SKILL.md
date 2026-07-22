---
name: grilling
description: Resolve ambiguity by interviewing the human one question at a time. Reached by other skills (spec, intake, design) when a decision needs the human; rarely invoked directly.
invocation: model
---
# Grilling

The reusable interview loop. One question per turn, each with your recommended
answer — and the split that makes it work: **facts get looked up; decisions get
asked.** If the codebase, the environment, or research can answer it, it is a
fact — look it up and record `Resolved by: codebase` (or the research file).
The decisions are the human's — put each one to them and wait.

## Trigger
A calling skill hits a decision it cannot make alone.

## Workflow
1. List the open questions (every clarification marker — the bracketed
   `NEEDS-CLARIFICATION` token in its colon form — is one); rank
   them by impact × uncertainty and label each **must-answer** (would change
   what gets built) or **nice-to-have**.
   Ordering has one hard rule above the ranking: never ask a question whose
   answer depends on another question still open — resolve the prerequisite
   first, whatever the ranking says.
2. Resolve the facts first — codebase exploration, or the `research` skill when
   the question hinges on a tech choice or a current-ecosystem fact.
   Independent fact lookups may run in parallel where the tool allows. Recommend
   from that evidence, not from training-data familiarity, and say where the
   research disagreed with your first instinct.
3. Ask the top question alone, with your recommended answer. Wait for the reply
   before the next. One question per turn — several at once is bewildering.
4. Write each answer back into the calling artifact (spec, conventions, etc.),
   delete its clarification marker, and update its scan-table row.
5. When the must-answers are done, list the remaining nice-to-haves in one line
   each and ask whether to keep going. **The human decides where questioning
   stops — never drop a question silently.**

## Guardrails
- Must-answers have no cap; every implementation-critical marker gets asked.
- Always offer a recommended answer; never ask a bare question.
- An unanswered must-answer stays a marker, and the calling skill stays
  blocked — silence and defaults don't resolve it.
- Batch asking exists in exactly ONE place: Mode 4 unattended drafting
  (`skills/spec/SKILL.md`, "Unattended drafting") embeds every question in the
  draft spec. Any change to how questions are asked here must stay consistent
  with that path.

## Completion criterion
Every must-answer resolved and written back, its marker deleted, and the human
explicitly chose where the nice-to-haves stopped.

## Output
The calling artifact, updated with the answers.

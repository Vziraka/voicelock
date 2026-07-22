# Tech Pick — choosing a dependency, tool, or framework

Why this exists: models default to what was common in their training data, not
what is best for THIS architecture — and keyword research happily surfaces a
dead repo from three years ago because it matched the words. This protocol
forces every pick into the open before it hardens into code.

## Trigger (unconditional)
Any NEW dependency, library, framework, service, or CLI tool about to enter the
spec or the build — anything not already in `project.md`, the lockfile, or a
prior decision. No exception for "obvious" picks: obvious is what
training-data bias feels like from the inside.

## Protocol
0. **Load the playbook** — read `formats/source-playbooks/library-evaluation.md`
   before any search (strategy first, then searching). For anything beyond a
   quick check, run the `research` skill and cite its findings file here.
1. **Candidates** — name 2–3 real alternatives (one may be "stdlib / build it
   ourselves"). Only able to think of one? That is the bias showing — research
   until you have two. Judge fit against the spec's Outcome and Constraints
   sections — "best for this scenario", never "most popular".
2. **Liveness bar** — for each candidate, check and QUOTE the evidence:
   - last release or commit within ~12 months
   - real adoption (downloads, dependents, active issues — never star count alone)
   - working documentation
   **Gray zone = FAIL:** if you cannot confirm a candidate clears the bar, it
   is OUT — "uncertain" is a fail, not a maybe. The human may waive it;
   a waiver is recorded as waived. "It matched the keywords" is never evidence.
3. **Walkthrough (plain English, before anything is installed):**
   - **Job** — what it does in OUR system, one sentence.
   - **Tradeoff** — why it over the alternatives, and what choosing it costs.
   - **Blast radius** — if it breaks or is removed tomorrow, what stops working.
   - **Connection** — how it wires into the existing components, by name
     (the human must be able to redraw the architecture with it in place).
4. **Human decides.** Present the comparison table + your recommendation; wait.
   Never install first and justify later.
5. **Record** — one entry in `memory/decisions.md` (decision · why · rejected
   alternatives) and the pick into the spec's Constraints section. If the pick
   introduced a term the glossary should carry, add its `CONTEXT.md` entry now,
   with its `_From:_` line pointing back at this decision. If it also clears
   the ADR bar (hard to reverse · surprising · real tradeoff), write the ADR too.

## Comparison format (keep it one screen)
| Candidate | Live? (quoted evidence) | Fits our stack because | Cost / risk |
|---|---|---|---|

## Guardrails
- Recency is checked against real dates, not vibes — quote the release date.
- If the honest recommendation is "none of these; do it by hand", say so.
- A waived liveness bar is recorded as waived in `memory/decisions.md`.
- At CUI research tier R0 (`constitution/topics/cui.md` ACTIVE), liveness
  evidence comes from an internal registry or the human; neither available
  = the existing waiver path, recorded.

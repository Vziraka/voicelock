---
name: curate
description: Garden the guardrails so the rulebook stays lean and current. Use periodically (every ~10 tasks, or when project.md guardrails exceed ~20), or on demand.
invocation: user
---
# Curate

The gardener. `learn` adds; `curate` prunes. Without it the rulebook bloats until
the agent can't hold it.

## Trigger
Every ~10 completed tasks, or when `project.md` guardrails pass ~20, or on demand.

## Workflow
1. Read all `project.md` guardrails and recent `memory/verdicts/`.
2. Assign each guardrail exactly one outcome:
   - **Keep** — accurate and still useful.
   - **Update** — fix still valid, references drifted.
   - **Consolidate** — two correct rules overlap → merge, delete the subsumed one.
   - **Replace** — now misleading → write a successor, delete the old.
   - **Delete** — domain gone, expired, or no real citations.
   Apply the retrieval-value test for Consolidate: *would separate rules help a
   maintainer in 6 months, or just create drift?*
   While assigning outcomes, also flag any prose guardrail that has since
   become mechanically enforceable (a check now exists or is cheap to add) —
   propose replacing the prose with the mechanism, human-approved like every
   other change.
3. **Decisions log** — review `memory/decisions.md`: entries superseded by newer
   decisions or belonging to dead domains get MOVED (human-approved) into an
   `## Archive` section at the bottom. Entries are never edited or deleted —
   moving keeps the log honest and the top of the file current.
4. **Defrift check** — grep each canonical sentence in `docs/CANON.md` across the
   harness; a paraphrased copy in a non-owner file is a finding (replace it
   with a reference to the owner). If `memory/verdicts/` holds ≥5 verdicts and
   harness files changed since last curate, run the calibration check
   (`memory/verdicts/CALIBRATION.md`).
5. **Deviations scan** — read `memory/deviations.md`. Two or more entries
   citing the SAME rule = that rule is a `FAILURES.md` candidate: draft the
   entry (what the rule says · why sessions keep having to reinterpret it) and
   put it to the human. The log is append-only — you read it here, you never
   edit it.
6. Produce a diff (old → new) with one reason per change.
7. The human approves; apply. Then update the stamp line at the top of
   `project.md`'s Earned guardrails section: `Last curated: {today} ·
   verdicts then: {n}` — {n} is the current count of verdict files (`*.json`)
   in `memory/verdicts/`. The wrap-up skill's curate check reads this stamp.

## Guardrails
- Auto-delete only if all hold: implementation gone, problem domain gone, no
  substantive citations. Expired rules are flagged for delete, not silently dropped.
- Never touch `protected.txt` files. When unsure, mark a rule `stale`, don't guess.
- Edits text rules only — git makes every change reversible.

## Completion criterion
Every guardrail has an assigned outcome, a diff with reasons is produced, and the
human approved before the write.

## Output
The curation diff; on approval, a leaner `project.md`.

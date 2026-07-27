# Handoff — F5.5 spec drafted, parked at the approval gate

**Waiting on one thing: the human checks box 2 in `spec.md` §0.** The agent
never checks it. Nothing may be planned or built until it is checked.

## Where the project is

- **F5 — Camera booth: DONE and committed** (`319b48b`). 7/7 tasks, live demo
  attested, roadmap box checked.
- **`/curate` (second pass): DONE and committed** (`296357a`). 6 guardrails,
  archive move, calibration run 2 (0/3 — see
  `memory/verdicts/2026-07-26-CALIBRATION-RUN-2.md`).
- **`/setup` re-run: DONE and committed** (`2a87c28`). Both tools recorded,
  `CLAUDE.md` added beside `AGENTS.md`, Claude Code adapter installed as 16
  per-skill junctions, private remote recorded.
- **F5.5 — Voiceprint dead-surface hygiene: SPEC DRAFTED, unapproved.**

## F5.5 in one paragraph

Remove code in `voiceprint.py` that no caller and no test can reach, refuse bad
audio loudly instead of converting it silently, and stop one test overclaiming.
Sourced from calibration run 2. Inserted before F6 for the same reason F4.5 was
inserted before F5: **F6 reopens this exact module** and will copy its shape.

- **Mode 4** (human's choice, 2026-07-26). Unlock verified mechanically: all 29
  verdict files record `"dev_mode": "Mode 3"`, and F3/F4/F5 completion reports
  are in history (`627963e`, `22e6a4a`, `319b48b`). Mode 4 means F5.5 runs to
  DONE unattended, **then F6's spec is drafted with questions embedded and
  parked at the gate** — never approved, never built.
- **Grilling record: `CLEAR`**, zero markers (verified mechanically: a grep for
  the marker token returns **0**).
- **No new dependencies. No live surface. No manual check** — the first feature
  with none, and §5 records why rather than leaving it implicit.

## Two things worth knowing before planning

1. **The scope shrank during grilling, on measurement.** A fourth item — an
   *ordering* assertion on the byte-disjoint `enroll1`/`enroll5` pair — was
   drafted and then **disproved**: a dummy embedder with no speaker modelling
   orders that pair correctly too (0.077 < 0.113), so the new test would have
   been as vacuous as the one it replaced. Root cause is not byte overlap but
   **one recording session per speaker**. With one clip per speaker in the
   Apache-2.0 source and offline-only forbidding a fetch, **no fixture-based
   same-speaker assertion can be made mutation-resistant.** That is already the
   standing position of `tests/fixtures/voiceprint/README.md:89-93`. Do not
   re-propose it.
2. **The §5 commands were dry-run before approval** (a `FAILURES.md` lesson —
   unrunnable pinned commands survived grilling twice). All seven execute; cmds
   1, 2, 5 and 7 fail today with assertions naming the exact build targets, and
   cmds 3 (constants unmoved) and 4 (mutation proof) **pass today and must keep
   passing**.

## Open items for the human

1. **Check box 2 in `spec.md` §0** — the only thing blocking `/plan`.
2. **A live finding stays logged, not fixed** —
   `.out-of-scope/2026-07-26-calibration-findings-run2.md`. F5.5 takes its
   item 1; item 2 shrank to the rename; item 3 is closed history.

## Pending guardrail

None.

## Commits

- Session base: `2a87c28` → head: this bookkeeping commit.
- Remote `origin` exists (private), so the checkpoint pushes as well as commits.

## next_action

**Human: check box 2 in `spec.md` §0.** Then `/plan` in a fresh session — it
breaks F5.5 into small ordered tasks. Expect roughly two: the deletion plus its
raises and tests, then the test rename and the justification comment.

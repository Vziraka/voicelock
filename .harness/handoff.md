# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** `/plan` for F1 — 5-task ledger written to `plan.md`
  (scaffold → capture → playback → UI chrome → pywebview bridge). All `TODO`,
  `rejects: 0`. Mode 3 standing go applies after this session's commit.
- **Commits:** base {pending plan commit} → head {pending plan commit}
  (fill after commit checkpoint; prior HEAD was
  `82e7e1c190453d0fb042402f022b88daeb664bb3`)
- **Failed + lesson:** none
- **Next action:** Mode 3 standing go — start `/implement` Task 1 in a **fresh
  session** (do not build in the plan session).
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` · `plan.md` · `roadmap.md` ·
  `memory/decisions.md` · `memory/research/2026-07-22-f1-ui-shell.md` ·
  `memory/research/2026-07-22-f1-audio-capture.md`
- **Wrap-up:** not run — session ending at plan / commit checkpoint

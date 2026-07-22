# Verdicts (append-only)

When wrap-up runs, its `learn` step writes ONE file here named
`{date}-F{n}-T{n}.json` (feature-qualified — task ids restart per feature, so
a date+task name alone collides on any multi-feature day; use plain
`{date}-{task-id}.json` only when the spec's `Feature:` line is `none`).
The compact `F{n}-T{n}` codes are a FILENAME convention only — filenames can't
hold spaces; prose everywhere else says "Feature 2, Task 3".
It captures the spec, the change, the Gate + Reviewer verdict, and the learn
outcome. Single writer, single write: created once by `learn`, never edited
afterward by anyone but a human.

**Why this exists (the calibration hook):** these accumulate into a
**calibration set** — 10–20 past tasks with known-correct verdicts. Later, any
change to the harness itself is re-run against them; if agreement drops below
~80%, the change is rejected. You cannot build that set retroactively, so we
start saving now.

This folder is **protected** (`protected.txt`). The agent may not edit past
verdicts — the system being improved cannot rewrite its own measurements.

Entry shape:

    {
      "task": "T1",
      "spec": "spec.md@<commit>",
      "change": "<commit range or diff path>",
      "gate":     { "commands": ["npm test"], "exit": 0, "note": "<optional context>" },
      "reviewer": { "verdict": "APPROVE", "axes": { "spec": "pass", "standards": "pass" }, "note": "<optional context>" },
      "mechanism": "subagent | fresh-session   (REQUIRED — which clean-context path actually verified; recording the wrong one is a defect)",
      "lesson":   "none | <the approved guardrail> | proposed — pending approval",
      "mode":     "full | lite   (lite = human-invoked spec-lite fast path)",
      "dev_mode": "Mode 1 | Mode 2 | Mode 3 | Mode 4   (optional — the development mode the feature ran under)",
      "date": "YYYY-MM-DD"
    }

The `note` fields are optional explanatory strings (escalation history, doubt
rulings, naming rationale) — an honest annotation in the artifact beats a
silent improvisation outside the schema.

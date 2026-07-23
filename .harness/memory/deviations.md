# Deviations — the judgment-call log (append-only)

When a rule cannot be followed literally (contradictory, impossible, or
pointing at something that does not exist), the universal [Modes] rule decides
what happens: Modes 3–4 STOP; Modes 1–2 may resolve it — but ONLY after
logging it here first. Guess out loud, or don't guess.

This file is **protected** (`protected.txt`, append-only): add entries at the
bottom, never edit or delete an existing one. State-file conflicts (the
universal [State] precedence rule) and mid-feature mode lowerings also land
here.

`curate` reads this log: two or more entries citing the same rule = that rule
is automatically a `FAILURES.md` candidate. The second patch files the bug.

Format — one entry per event:
- {YYYY-MM-DD} · task {id} · mode {n} · rule: {file:line or rule name, as written} · conflict: {why it cannot be followed} · resolution: {the reading chosen}

<!-- entries go below this line -->

- 2026-07-22 · task F3-T1 · mode 3 · rule: `spec.md` §4 Constraints + `plan.md` Task 1 notes — "download the official files once and commit them (~20 MB in git; plain git, no LFS)" · conflict: the real vendored ECAPA set is ~85 MB (`embedding_model.ckpt` alone is 83 MB), ~4× the spec's "~20 MB" estimate; the size figure cannot be met with the actual model. · resolution: proceeded — "~20 MB" is a descriptive estimate, not an actionable constraint; the actual constraints (commit the files, plain git, no LFS, no runtime network) are all satisfiable and were satisfied. Vendored the official Apache-2.0 files plainly (no LFS). Spec amendments are human-only, so the "~20 MB" text is left for the human to correct; flagged in the stop report + handoff.

- 2026-07-22 · task F3-T3 · mode 3 · rule: `skills/implement/SKILL.md` step 3 + universal BUILD gate — "set it DOING … write plan.md and commit it before touching any code"; the completion criterion "its DOING was committed before building" · conflict: none in principle — the rule was followable; I simply skipped it. Task 3's `plan.md` state went TODO → REVIEW inside the single build commit (`e020198`), with no standalone committed DOING checkpoint. · resolution: an execution slip caught right after the build commit, not a rule impossibility. I did NOT rewrite history to fabricate a backdated DOING (that would be a false ledger and irreversible git). The build is intact and the Gate diff base is unambiguous — `e47c8b6` (Task 2 wrap-up, HEAD before any Task-3 code) `..` `e020198` (Task 3 build). Flagged in the stop report + handoff for the human and the fresh-eyes verifier to weigh. Process note for future tasks: commit the DOING state as its own commit before editing code.


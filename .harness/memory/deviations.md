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


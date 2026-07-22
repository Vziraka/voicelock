# Calibration loop — INACTIVE until ≥5 verdicts exist

This activates itself: once this folder holds 5 or more real verdict files,
any change to harness files triggers the check below (run it via `/curate`).

**The check:** re-run `formats/VERIFIER-PROMPT.md` (fresh subagent or session)
against 3–5 archived verdicts — same spec, same diff (the verdict's `change`
commit range), same commands. Compare the fresh verdicts to the archived ones.

- Agreement → the harness change didn't break the verifier's judgment; proceed.
- Disagreement on any verdict → investigate before trusting the change. Either
  the change degraded the verifier (revert it) or the archived verdict was
  wrong (a human records that finding — the archive itself is never edited).

Why: any self-improving system needs a fixed measuring stick. These verdicts
are the stick — which is why `protected.txt` makes them append-only. You
cannot build this set retroactively; it accumulates one real task at a time.

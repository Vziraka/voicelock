# Code quality — the universal floor

Distribution-owned — intake never writes this file. Per-repo detail lives in
`conventions.md`; this is the floor beneath it, so the Reviewer's Standards
axis has something to enforce from day one, before any project rules are
learned. Tech-agnostic on purpose.

## The bar (every diff, every task)
- **Smallest change that solves it.** Every changed line traces to the task;
  a change that can't say which requirement it serves doesn't belong in the diff.
- **No speculative anything.** No features, abstractions, config options, or
  "flexibility" added for imagined future needs — "might need it later" is the
  signature of AI slop, not foresight.
- **Surgical scope.** Touch only what the task requires. Restructuring existing
  code needs execution evidence that the structure itself is the root cause —
  "I'd have organized it differently" is not a finding. Clean up only orphans
  YOUR change created.
- **Root cause, not symptom.** A fix that makes the failure invisible without
  addressing why it happened gets named as such.
- **Beyond the diff.** Would this change break unchanged code that calls it or
  depends on it? Name the coupling and why it holds — or flag it.
- **Security findings need a traced path.** From a real input to a real sink —
  generic "this could be insecure" speculation is noise, not a finding.

A small, correct, boring change passes this bar by default — the bar exists to
catch cleverness, not to demand it.

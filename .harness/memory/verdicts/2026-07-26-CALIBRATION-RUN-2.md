# Calibration run 2 — 2026-07-26

Run by `curate` (second pass) per `CALIBRATION.md`. Both trigger conditions met:
the folder holds ≥5 verdicts (29), and harness files changed since the last
curate — `constitution/project.md` gained two guardrails (`a114a49`, `5522bd3`)
and, immediately before this run, three more curate edits.

This run re-tests **the same three archived verdicts as run 1**, deliberately,
so the two numbers are comparable and run 1's confounds can be judged.

**The archive itself is NOT edited.** This file records the finding beside it,
as `CALIBRATION.md` requires.

## Result: 0 of 3 agreement — unchanged from run 1, now with the confounds fixed

| Archived verdict | Archived | Run 1 | Run 2 (confounds fixed) | Agree? |
|---|---|---|---|---|
| `2026-07-22-F1-T2` (capture engine) | GATE PASS · APPROVE | GATE PASS · REJECT | GATE PASS · **REJECT** | ✗ |
| `2026-07-22-F2-T3` (Booth enroll/unlock chrome) | GATE PASS · APPROVE | GATE PASS · REJECT | GATE PASS · **REJECT** | ✗ |
| `2026-07-22-F3-T2` (voiceprint engine) | GATE PASS · APPROVE | GATE PASS · REJECT | GATE PASS · **REJECT** | ✗ |

Every fresh Gate passed. All three disagreements are on the **Reviewer** axes —
the same shape as run 1. **The 0/3 held up under a corrected setup**, which run 1
explicitly said was needed before its number could be trusted.

## What run 2 fixed, and the confound run 1 did not know about

Run 1 named three flaws in its own setup. Run 2 addressed all three:

1. **Priming — fixed.** Run 1's brief told each agent that "`project.md`'s
   guardrails are what we are calibrating against", plausibly priming them to
   hunt dead code. Run 2 used `formats/VERIFIER-PROMPT.md` **verbatim**, with a
   location-only preamble naming the working directory and nothing else. No
   mention of calibration, guardrails, or what to look for.
2. **Wrong plan supplied — fixed.** Run 1 extracted state files at the *spec's*
   commit. Run 2 used a real `git worktree` per task, so every state file is
   whatever that commit actually contained.
3. **Commands run against today's tree — fixed.** Run 2 ran each Gate inside a
   worktree checked out at the archived commit, with its own `uv sync --frozen`
   against that commit's lockfile. Exit codes describe the archived tree.

**A fourth confound, found by run 2 and caused by run 2.** The worktrees were
first checked out at each task's **build** commit. But every task has a
state-only **bookkeeping** commit immediately after it, and that is the commit
that writes `handoff.md` with the task's base/head — so the verifier was handed
a handoff describing the *previous* task. Two of three verifiers correctly
returned `ESCALATE_HUMAN` on it (`verify-gate` step 4). All three worktrees were
moved forward one commit and **all three tasks re-run from scratch** with fresh
subagents; only those re-runs are tabulated above. The bookkeeping commits touch
`.harness/handoff.md` and nothing else, so the code and the `base..head` diff are
byte-identical either way.

*Method note for run 3:* check out the **bookkeeping** commit, not the build
commit.

### The one confound that cannot be fixed

The fresh verifiers read **today's** `constitution/project.md` — six earned
guardrails, all from F4/F4.5/F5 — while judging F1–F3 code that predates every
one of them. That anachronism is inherent to the check: the harness change under
test *is* the current rulebook. It inflates disagreement by construction and no
setup change removes it. It is why the next section matters more than the 0/3.

## Which way does the disagreement point?

`CALIBRATION.md` asks: did the harness change degrade the verifier, or were the
archived verdicts wrong? **Run 2 gives a sharper answer than run 1: mostly the
archived verdicts, but not uniformly.**

Splitting the rejects by whether they depend on today's guardrails:

- **F1-T2 — stands without any new rule.** `capture.py` called
  `stream.stop()` from inside the PortAudio callback, which blocks until the
  callback returns. That is a live self-deadlock, and the project itself later
  confirmed it: **F4.5 was inserted into the roadmap specifically to fix it.**
  The verifier proved the coverage gap by mutation — neutering `_on_audio` to a
  bare `return` left all 5 tests green.
- **F2-T3 — stands without any new rule.** The overwrite-confirm button called
  `hideOverwriteConfirm()`, zeroing the `pendingOverwrite` flag the confirm
  existed to set, so the affirmative path was inert. **Run 1 found this
  independently**, and the project later rewrote the handler — at HEAD
  `index.html:1120` reads `if (result && result.needs_confirm)`.
- **F3-T2 — guardrail-dependent.** Its Spec axis **passed**. The REJECT rests
  entirely on `_resample` being unexercised, i.e. on the earned "no unexercised
  branch" rule. Without that rule this task would plausibly have been approved
  again.

So **2 of 3 rejects are independent of the new rulebook** and are corroborated
by the project's own later behaviour. That is the strongest evidence available
that the early F1–F3 reviews were lenient rather than that the verifier has
drifted. The third is a genuine effect of the guardrails — which is what
guardrails are for, but it should be counted honestly rather than folded into
the same bucket.

## Evidence that the newly-adopted guardrails are load-bearing

Both proposals adopted at this curate were cited **by file:line** in reviews
written minutes later, unprompted:

- **Guardrail A** (a test must break if the behaviour is removed) — cited as
  `project.md:63` by the F1-T2 verifier, which ran two independent mutations
  (neutering `_on_audio`; stubbing `_close_stream`) and found both survived.
- **Guardrail C** (every ending path releases the device) — cited as
  `project.md:59` by the same verifier, against the untested release path.

Mutation testing appeared in **all three** run-2 reviews. It appeared in none of
the three archived verdicts.

## Consequences

- **Do NOT revert the guardrails.** Two of three rejects do not depend on them,
  and the third is the rule working as designed.
- **The three archived verdicts stand as historical record** and are not edited.
  This file is the recorded finding, beside run 1's.
- **Findings are logged, not fixed** — see
  `.out-of-scope/2026-07-26-calibration-findings-run2.md`. Run 1's items 1 and 2
  are now closed (fixed by F4.5); one blocking item (`_resample`) remains live,
  plus a narrow test-strength item.
- **A run-1 finding was overstated and is corrected there.** Run 1's item 4
  treated the fixture overlap as a documentation caveat; an intermediate draft of
  run 2 overcorrected and called it a serious defect. Neither is right: the
  overlap is byte-exact and verified, but it is fully disclosed and reasoned in
  `tests/fixtures/voiceprint/README.md`, which the second F3-T2 verifier weighed
  before deliberately passing the Spec axis. What survives is only that the
  same-speaker *assertion* is weak by construction.
- **Run 3 should change what it measures.** Three runs against the same three
  F1–F3 tasks now agree with each other and disagree with the archive; a fourth
  repetition adds little. Sample F4/F4.5/F5 verdicts instead — tasks judged
  under a rulebook close to today's — which isolates verifier drift from
  rulebook growth in a way this run cannot.

## Cost

Six subagent verifier runs (three tripped the fourth confound and were
discarded, three counted), three `git worktree` checkouts with per-commit
`uv sync --frozen`. Worktrees are disposable and were removed after the run.

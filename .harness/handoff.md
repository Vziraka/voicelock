# Handoff — F4 Task 1 (5-take enrollment fixtures) · /implement session · 2026-07-26

## Where we are
Approval box 2 was **re-checked by the human**, so F4 is unblocked and building
started. **Task 1 is `REVIEW`** — five speaker-A enrollment fixtures exist and the
same/different separation is measured. Tasks 2–5 stay `TODO` (WIP=1).

- base: `a13d891` (DOING + the human's box-2 approval, committed before building)
- head: `01667e1` (the build commit — this handoff's own commit is one after it)

## Changed
- `tests/fixtures/voiceprint/speakerA_enroll1..5.wav` — **new**. Five 1.600 s
  windows (25 600 samples) at hop 0.415 s over the reassembled 3.261 s speaker-A
  source (`speakerA_take1/2/3.wav` concatenated = the model repo's `example1.wav`,
  Apache-2.0 rev `0f99f2d`). Mono 16 kHz PCM_16, committed via the existing
  `.gitignore` exception.
- `tests/fixtures/voiceprint/README.md` — documents the derivation, the
  window-length comparison table, the measured separation, and the
  fixture-vs-reality caveat.
- `.harness/plan.md` — Task 1 `TODO → DOING → REVIEW`, Active context unblocked,
  measurements recorded under the task, memory spine bullets 1 and 5 refreshed.
- **F3 fixtures untouched** — `speakerA_take1/2/3.wav`, `speakerA_live.wav`,
  `speakerB.wav`, `too_short.wav` are byte-identical; `test_voiceprint.py` and
  `test_booth_api.py` still pass on them.

## One judgment call the verifier should check
The plan sketched "five ~1.0 s windows" but also said "cut the windows as long as
the source allows (prefer overlap over shortness)". Those pull opposite ways, so I
**measured** four window lengths and pinned **1.6 s**:

| window | take1↔take5 overlap | cross-take pairwise max | sign-unanimous | genuine BER |
|---|---|---|---|---|
| 1.2 s | 0 % | 0.747 | 64/192 | 13 % |
| **1.6 s** | **0 %** | **0.624** | **98/192** | **7.8 %** |
| 2.0 s | 37 % | 0.350 | 128/192 | 8 % |
| 2.4 s | 64 % | 0.219 | 137/192 | 8 % |

1.6 s is the longest window where takes 1 and 5 still share **zero** audio, and
genuine BER plateaus at ~8 % from there. Anything longer buys its extra stability
by making the five "takes" literally the same audio — Task 2's cross-take
unanimity filter would then be measuring the cut, not the speaker. At 1.2 s the
opposite failure appears: two takes of the SAME speaker land 0.747 apart, past
F3's 0.65 reject cutoff, which starves the same filter. This is a fixture-geometry
choice inside Task 1's stated scope, not a spec change — spec §4's numbers
(~2048–4096 pool, ~512 kept bits, ~32-bit key, ~16× repetition) are untouched.

## Numbers Task 2 needs (the "build-notes" the plan asked for)
Recorded durably in the **fixtures README** and under Task 1 in `plan.md` — there
is no `build-notes` file convention in this repo, and the README is what a Task 2
session reading the fixtures will actually open.

- 5-take mean → `speakerA_live.wav`: **0.0583** (accept ≤ 0.45)
- 5-take mean → `speakerB.wav`: **0.8451** (reject ≥ 0.65)
- per-take → mean: 0.2695 / 0.0772 / 0.0619 / 0.0891 / 0.1576 (take 1 is the outlier)
- cross-take pairwise: max 0.6241, mean 0.3062
- raw 192-dim sign bits: **98/192 (51 %) unanimous** across all five takes
- raw sign-BER vs the mean: genuine **7.8 %**, impostor **43.2 %**

Read that as **better than the research's ~25 % warning but not safe**: 7.8 % is on
raw 192-dim bits from longer windows than F3 used, and only ~51 % of bits survive
unanimity, so Task 2's ~512 kept bits out of a 2048–4096 pool is the right order of
magnitude — but the bits stay correlated (192 real dimensions), so binomial
estimates will still be optimistic. Measure; do not trust the arithmetic.

## What I ran (measurement-exception disclosure)
Task 1's done-criterion IS a measurement, so I ran all three of its commands. The
Gate still owns verification — these are disclosed, not a substitute:
- the plan's `uv run python -c ...` separation check → exit 0
  (`same 0.05832901647226285 diff 0.8450908827361865`)
- `uv run ruff check .` → exit 0 (`All checks passed!`)
- `uv run pytest` → exit 0 (`35 passed in 8.77s`)

## Next action
Verify Task 1 with **clean context** — `formats/VERIFIER-PROMPT.md` used verbatim,
task `F4-T1`, base `a13d891`, head `01667e1`. Mode 3 means verification starts
itself; no human "go" needed. On APPROVE → wrap-up, then Task 2 (`middlelock.py`).

## Notes for the human (no action required unless you disagree)
- `spec.md` §0's amendment paragraph still reads "*box 2 re-opened, awaiting the
  human's `x`*" even though box 2 is now `[x]`. Stale prose only — the checkbox is
  the mechanical gate, and I did not edit the spec to tidy it (that is your file to
  amend). Worth a one-line fix next time you touch the spec.
- Carried from F3, still open: `spec.md`'s "~20 MB" model-size wording is wrong —
  the vendored ECAPA is ~85 MB.
- Carried: your existing `~/.voicelock/vault.vl` is a v1 vault and will be refused
  with a re-enroll prompt after F4 (by design, confirmed 2026-07-26).
- No pending guardrail proposal from this task.

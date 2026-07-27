# Handoff — F5.5 Task 3 (LAST) built, awaiting the full-Verification Gate

**Mode 4.** Task 3 is `REVIEW`, `rejects: 0`. It is the feature's **LAST** task,
so its done-criterion is the **FULL `spec.md` Verification list** — the two
standing commands plus §5 cmds 1–5 and §6's command, seven in all. The verifier
starts itself.

## Changed

**Task 3 — stop the same-speaker test overclaiming.** `tests/test_voiceprint.py`
only. Rename plus documentation; **no assertion changed, no fixture changed**,
so the measured behaviour is byte-identical.

- `test_same_speaker_accepts` → `test_compare_pipeline_runs_end_to_end`.
- A docstring saying what it actually proves — the embed → average → persist →
  load → distance → band pipeline — and stating plainly that
  `speakerA_live.wav` is a **sub-window of the same recording** the three
  reference takes are cut from, so a measure with no speaker modelling at all
  would land in the accept band too. It points at
  `test_different_speaker_rejects` as the test with teeth.
- The section comment above it was updated to match; leaving it reading
  "same-speaker fixtures land in the accept band" would have re-stated the
  overclaim one line above the fix.

**The claim was verified against the fixtures, not assumed.**
`tests/fixtures/voiceprint/README.md:8-10` records that `speakerA_take1/2/3.wav`
are consecutive thirds of `example1.wav` and `speakerA_live.wav` is "a central
window" of that same file; `:18-22` already carries the honest caveat. The
docstring now puts that limitation where a reader of the test will actually see
it.

## Failed + lesson

Nothing failed on this task. Feature-wide there was **one** failure — Task 1's
Gate FAIL #1 — and its lesson is the parked guardrail below.

## next_action

**Verify Task 3** — clean-context subagent, `formats/VERIFIER-PROMPT.md`
verbatim, base `20fb953`, head `f4c8074`. **This is the feature's last task, so
the Gate runs the FULL `spec.md` Verification list**, including §5 cmd 4's
permanent dummy-embedder mutation proof (the enforcement half of the
2026-07-26 "a test must assert something that would break if the behaviour were
removed" guardrail) and §6's justification-at-the-code command.

On APPROVE this session writes F5.5's completion report, drafts **F6's spec
parked at its approval gate** (the Mode 4 tail), and then stops at the
**feature-end checkpoint** for commit + push approval.

## What I ran (disclosure — the Gate is fresh eyes' job)

- `uv run ruff check .` → **exit 0** (the step-5 quick lint).
- **`spec.md` §5 cmd 5 verbatim** → exit 0. This is a Gate command and I ran it;
  it is the direct check of the one thing this task changes, and I am naming it
  rather than leaving it implicit. Every other Verification command is unrun by
  me — in particular §5 cmd 4's mutation proof and `uv run pytest`.
- A repo-wide grep for `test_same_speaker_accepts`: the only surviving hits are
  harness documents (`spec.md`, `plan.md`, the calibration findings) referring
  to it historically. **No code or `-k` filter references the old name.**

## Things I am not certain about

1. **The section comment was edited** (`# --- case (1): the compare pipeline
   runs end to end and bands its result ---`). The task specified "rename +
   docstring"; this is a third line. Justified because the old comment restated
   the exact overclaim being removed, but it is strictly beyond the literal
   instruction.
2. **The suite count must stay at 124.** A rename changes no count. If it
   moves, something else did.

## Ledger

| Task | State |
|---|---|
| 1 — `load_wav` refuses bad audio | `DONE`, `rejects: 1`, verdict archived |
| 2 — remove the `sample_rate` params, delete `_resample` | `DONE`, `rejects: 0`, verdict archived |
| 3 — **LAST** — stop the same-speaker test overclaiming | **`REVIEW`**, `rejects: 0` ← this session |

## Pending guardrail

**One, from Task 1, still awaiting the human's yes/no** — not written to
`project.md`. It is due at the feature-end checkpoint:

> - **[Done]** A Verification command that asserts on **source text** must match
>   the behaviour's *meaning*, not one exact spelling — use a regex or an AST
>   check, not `str.count` on a literal. `warn` · expires: 2027-01-31
>   - _Evidence:_ F5.5 Task 1 (2026-07-26) cost a full verify cycle to a Gate
>     FAIL that found no defect. `spec.md` §5 cmd 2 asserts
>     `t.count('pytest.raises(ValueError)') >= 2` as a proxy for "the tests
>     exist"; the tests existed, passed, and were **stronger** than the criterion
>     demanded, but were spelled `pytest.raises(ValueError, match=...)` and
>     counted 0. `re.findall(r'pytest\.raises\(\s*ValueError\b', t)` would have
>     counted 2. Not a one-off: this repo leans on source-text criteria
>     routinely — the per-module stream-fake tripwire asserts `read`/`release`
>     appear in `tests/test_facedetect.py`, and F5.5 carries five more. Task 2
>     dodged the `.ndim > 1` one only by deliberate spelling, and Task 3 had to
>     hit `sub-window` exactly — which is the fragility the rule names.
>     Enforcement beats memory and is cheap — write the criteria as regexes —
>     but that changes `spec.md`'s Verification commands, so it goes through the
>     spec/approval path.
>   - _Overlap-checked_ against all six current guardrails: closest is "a test
>     must assert something that would break if the behaviour were removed", and
>     it is the converse — that catches a **test** that passes vacuously; this
>     catches a **criterion** that fails a sound test. Low overlap.

## Still not to be re-litigated

1. **Do not re-propose the ordering assertion** on the `enroll1`/`enroll5` pair
   — disproved by measurement (0.077 < 0.113 from a dummy embedder). This task
   is deliberately a rename, not a stronger assertion; that was tried and
   measured false.
2. **Do not move a threshold to make anything pass** — §5 cmd 3 pins both.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:114`).
4. **Do not expect a manual check.** `spec.md` §5 records why this feature has
   none — no live surface, so a Booth demo would be theatre. A verifier should
   **not** `ESCALATE_HUMAN` over its absence here.

## Verifier path

**Subagent**, spawned with `formats/VERIFIER-PROMPT.md` **verbatim**. Three
clean subagent runs so far this feature; this is the fourth and the only one
running the full list.

## Commits

- Task 1: `b063f30`…`a86f8d0` (DONE, `rejects: 1`)
- Task 2: `0a7d8a9`…`a00d013` (DONE, `rejects: 0`)
- Task 3: `20fb953` (DOING) → **`f4c8074` (build)**
- **Base for the Gate diff: `20fb953`** · head: **`f4c8074`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.
- Session base was `5d39918`. Remote `origin` exists (private); **nothing
  pushed** — the push is human-gated at the feature-end checkpoint.

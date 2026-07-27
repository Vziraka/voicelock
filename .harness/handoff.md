# Handoff — F5.5 Task 2 DONE, Task 3 (LAST) next

**Mode 4.** Two of three tasks closed with verdict files. Task 3 is the feature's
LAST task, so its done-criterion is the FULL `spec.md` Verification list.

## Changed

**Task 2 — remove the `sample_rate` parameters and delete `_resample`.**
`src/voicelock/voiceprint.py` only, subtraction apart from three docstring
lines. `embed` and `compare` lost the parameter, `compare` lost its
pass-through, and `_resample` — callerless once Task 1 removed `load_wav`'s
call — is gone. Suite held at **124 passed / 0 failed**, exactly as the task
required: a moving count would have meant a missed caller.

`embed`'s docstring gained three lines recording where the 16 kHz expectation
comes from, because the deleted parameter was the only statement of it at the
signature. Flagged as possible scope creep; the verifier ruled on it explicitly
and kept it.

**Discovered, recorded, not built:** `_resample` was the repo's only
`torchaudio` import →
`.out-of-scope/2026-07-26-torchaudio-no-longer-imported-directly.md`.

## Failed + lesson

Nothing failed — `rejects: 0`, Gate passed 4/4 first time. `learn` scan
outcome: **no lesson** (recorded in the verdict file). The only candidate — "a
deletion that removes a parameter also removes the documentation it carried" —
is one occurrence and close to a general engineering principle, so it does not
clear the bar.

## next_action

**`/implement` Task 3 (LAST)** — rename `test_same_speaker_accepts` to say what
it actually proves and document that its probe is a sub-window of the same
recording, pointing at the impostor test. **No assertion changes, no fixture
changes.** Its done-criterion is the FULL `spec.md` Verification list, including
§5 cmd 4's permanent dummy-embedder mutation proof and §6's command. Mode 4
starts it without a further "go"; after it, the Mode 4 tail drafts F6's spec.

## Where the rest lives

- Task ledger, feedback, memory spine → `plan.md`
- What is fixed and why → `spec.md` (§3 non-goals, §4 the deletions, §5 the
  seven commands, §6 the F6 blind spot)
- Verdicts → `memory/verdicts/2026-07-26-F5.5-T1.json` and `-T2.json`
- Why this feature exists →
  `.out-of-scope/2026-07-26-calibration-findings-run2.md`

## Pending guardrail

**One, from Task 1, still awaiting the human's yes/no** — not written to
`project.md`:

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
>     dodged the `.ndim > 1` one only by deliberate spelling, which is exactly
>     the fragility the rule names. Enforcement beats memory and is cheap —
>     write the criteria as regexes — but that changes `spec.md`'s Verification
>     commands, so it goes through the spec/approval path.
>   - _Overlap-checked_ against all six current guardrails: closest is "a test
>     must assert something that would break if the behaviour were removed", and
>     it is the converse — that catches a **test** that passes vacuously; this
>     catches a **criterion** that fails a sound test. Low overlap.

## Still not to be re-litigated

1. **Do not re-propose the ordering assertion** on the `enroll1`/`enroll5` pair
   — disproved by measurement (0.077 < 0.113 from a dummy embedder).
2. **Do not move a threshold to make anything pass** — §5 cmd 3 pins both.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:114`).
4. **Do not expect a manual check.** `spec.md` §5 records why; a verifier should
   **not** `ESCALATE_HUMAN` over its absence on this feature.

## Verifier path

**Subagent**, spawned with `formats/VERIFIER-PROMPT.md` **verbatim**; the
implement session executes the verdict and never overrides it. Three clean
subagent runs so far this feature (Task 1 twice, Task 2 once).

## Mode 4 tail — after Task 3

Once Task 3 is `DONE` and wrap-up writes F5.5's completion report, the session
drafts **F6 — Faceprint on screen**'s spec with every grilling question embedded
as a clarification marker and its `Mode:` line left blank, then **parks it at
the approval gate and stops.** Never approved, never built. F6 inherits F5's
fetched-not-committed fixture arrangement, the two-faces gap (CC0 shortlist in
`memory/research/2026-07-26-f5-fixture-replacement-candidates.md`), and a second
vendored model dir for OpenCV SFace — which owes a per-asset licence check.

## Commits

- Task 1: `b063f30`…`a86f8d0` (DONE, `rejects: 1`)
- Task 2: `0a7d8a9` (DOING) → `d6af571` (build) → `0a6602e` (bookkeeping) →
  this wrap-up commit (DONE, `rejects: 0`)
- Session base was `5d39918`. Remote `origin` exists (private); **nothing
  pushed** — the push is human-gated at the feature-end checkpoint, which is now
  one task away.

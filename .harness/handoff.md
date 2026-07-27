# F5.5 — Voiceprint dead-surface hygiene · COMPLETION REPORT

**DONE 2026-07-26 · Mode 4 · 3 tasks · 1 reject across the feature.**
Awaiting the human at the **feature-end checkpoint**: commit + push approval,
and a yes/no on the one parked guardrail.

## Outcome vs the spec

`spec.md` §1 required three things to be true. All three are, each pinned by a
runnable command rather than by assertion:

1. **No unreachable surface in `voiceprint.py`.** `_resample`, both of its call
   sites, the stereo-downmix branch, and the `sample_rate` parameters on `embed`
   and `compare` are gone. §5 cmd 1 → exit 0. This closes the one blocking
   finding **both** independent F3-T2 verifiers agreed on, and it is a direct
   hit on the earned "no unexercised branch" guardrail.
2. **Bad audio is refused loudly, not misread quietly.** `load_wav` raises
   `ValueError` naming the real sample rate and the real channel count. Two
   tests drive both raises through a real `soundfile` round-trip, so the
   replacement is genuinely exercised and is not new dead surface of its own.
   §5 cmd 2, both halves → exit 0.
3. **The same-speaker test stops overclaiming.**
   `test_same_speaker_accepts` → `test_compare_pipeline_runs_end_to_end`, with a
   docstring stating that its probe is a sub-window of the same recording as the
   reference takes and pointing at the impostor test as the one with teeth.
   §5 cmd 5 → exit 0.

**Demo, as specified:** `uv run pytest` is green with the measured constants
unmoved, and `voiceprint.py` no longer contains a line that cannot execute.

## Final Gate — the FULL spec Verification list, run on Task 3

| # | Command | Exit |
|---|---|---|
| 1 | `uv run ruff check .` | **0** — "All checks passed!" |
| 2 | `uv run pytest` | **0** — **124 passed**, 0 failed, 41.98 s |
| 3 | §5 cmd 1 — the dead surface is gone | **0** |
| 4 | §5 cmd 2 (behaviour) — `load_wav` raises on stereo and on 44.1 kHz | **0** |
| 5 | §5 cmd 2 (existence) — the tests for it exist | **0** |
| 6 | §5 cmd 3 — `ACCEPT_CUTOFF == 0.45`, `REJECT_CUTOFF == 0.65` | **0** |
| 7 | §5 cmd 4 — the dummy-embedder mutation proof | **0** |
| 8 | §5 cmd 5 — the overclaiming name is gone, the limitation documented | **0** |
| 9 | §6 cmd — the `capture.py` justification is still at the raises | **0** |

Test count went **122 → 124**: the spec required it to rise by the new
`load_wav` tests and never fall, and it did exactly that.

**No manual check, deliberately.** `spec.md` §5 records why: this is the first
feature with no live surface, so a Booth demo would be theatre rather than
evidence. The Task 3 verifier explicitly did **not** treat its absence as a gap.

## Per-task record

| Task | What | rejects | Verdict |
|---|---|---|---|
| 1 | `load_wav` refuses bad audio (+ the F6 justification comment) | **1** | `memory/verdicts/2026-07-26-F5.5-T1.json` |
| 2 | Remove the `sample_rate` params, delete `_resample` | 0 | `…-F5.5-T2.json` |
| 3 | Stop the same-speaker test overclaiming (LAST) | 0 | `…-F5.5-T3.json` |

All three verified by **clean-context subagents** (four runs; Task 1 twice).
Every verdict records `"mechanism": "subagent"` and `"dev_mode": "Mode 4"`.

**The one reject, in full:** Task 1's Gate FAIL #1 found **no defect**. `spec.md`
§5 cmd 2 counts the literal substring `pytest.raises(ValueError)`; the tests were
spelled `pytest.raises(ValueError, match=…)`, so the comma broke the match and
the count measured 0. Every other criterion passed on that attempt, `pytest`
included. Fixed in the test spelling — `with pytest.raises(ValueError) as
excinfo:` plus an assertion on `str(excinfo.value)` — which satisfies the
command as written and keeps the message assertion. **The criterion was not
touched**: it is human-approved spec text, and editing it to fit the code would
have been a silent spec amendment.

## `memory/deviations.md` entries during this feature

**None.** No rule proved impossible to follow literally, and no conflict between
state files arose. Verified against git history for the feature's commit range.

## Escalation-worthy things that resolved themselves

1. **A spec-vs-plan wording mismatch.** `spec.md` §6 says the raises "**each**
   carry a comment"; `plan.md` Task 1 says "a comment" (singular). Resolved
   without escalating by satisfying the stricter reading — one block comment
   carrying the full doctrine plus a per-raise inline comment naming the pin
   each rests on — and by flagging it in the handoff so the verifier ruled on it
   rather than inheriting my judgment. It approved the arrangement.
2. **A dependency that fell out of use.** Deleting `_resample` removed the
   repo's only `torchaudio` import. Not acted on: §4 forbids touching
   `pyproject.toml`, it is not in §1, and it would change nothing —
   `speechbrain` declares `torchaudio>=2.1.0` itself. Recorded per §5's Modes
   3–4 out-of-scope default in
   `.out-of-scope/2026-07-26-torchaudio-no-longer-imported-directly.md`.

## The named blind spot — mitigated, and the mitigation is enforced

`spec.md` §6's answer to "if every gate passed but the feature were still wrong":
**F6 would copy the strict-rejection pattern into a place it does not belong.**
Refusing unexpected input is correct in `voiceprint.py` *only* because
`capture.py` pins the mic to one rate and one channel; camera frames have no
such pin and legitimately vary in resolution.

The mitigation is live: the justification is written beside the raises, and §6's
Gate command asserts it stays there, so a later tidy-up cannot silently drop it.
**F6's spec must not inherit "refuse unexpected input" for image data.**

## Pending guardrail

**None — the one proposal was ADOPTED.** `learn` proposed one guardrail across
the feature (Tasks 2 and 3 recorded `"lesson": "none"`); the human approved it
2026-07-26 and it is now the seventh entry in `project.md`'s Earned guardrails:

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
>     hit `sub-window` exactly. Enforcement beats memory and is cheap — write
>     the criteria as regexes — but that changes `spec.md`'s Verification
>     commands, so it goes through the spec/approval path.
>   - _Overlap-checked_ against all six current guardrails: closest is "a test
>     must assert something that would break if the behaviour were removed", and
>     it is the converse — that catches a **test** that passes vacuously; this
>     catches a **criterion** that fails a sound test. Low overlap; a new entry
>     rather than an edit.

## Mode 4 tail — F6's spec

Drafted and **parked at its approval gate** with every open question embedded as
a clarification marker and its `Mode:` line left blank. Never approved, never
built. See `spec.md`. It carries forward: OpenCV SFace as the embedding, the
two-faces fixture gap, the per-asset licence rule, and — from this feature's
blind spot — the explicit instruction **not** to copy `voiceprint.py`'s
refuse-unexpected-input pattern onto camera frames.

## Commits

- Task 1: `b063f30` → `a86f8d0` (4 commits incl. the FAIL record and the retry)
- Task 2: `0a7d8a9` → `a00d013`
- Task 3: `20fb953` → `f4c8074` → `c143792` → this wrap-up commit
- Feature base: `5d39918`.
- **Nothing pushed.** `origin` exists (private) and the push is part of the
  approval being requested here.

## next_action

**Resolve F6's parked spec.** The feature-end checkpoint is closed — the human
approved the commit + push and adopted the guardrail (2026-07-26). What remains
is `spec.md`: answer its **ten** embedded clarification markers (Q1 fixtures and
Q7 alignment are the ones that change what gets built), set the `Mode:` line,
and check box 2. Only then does `/plan` run. Q1 likely needs a `research` pass
first — it is a licence question as much as a technical one.

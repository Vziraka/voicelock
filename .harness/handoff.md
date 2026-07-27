# Handoff — F5.5 Task 1 built, awaiting the clean-context verifier

**Mode 4.** Task 1 is `REVIEW`. The next move belongs to the verifier, not to a
human — the approved spec's `Mode:` line is the standing "go" inside F5.5.

## What changed

**Task 1 — `load_wav` refuses bad audio instead of silently converting it.**

- `src/voicelock/voiceprint.py` (`load_wav` only) — the stereo downmix and the
  resample call are replaced by two `ValueError`s that name the offending
  value: the real sample rate (`got 44100 Hz`) and the real channel count
  (`got 2 channels`). The docstring now records that a non-conforming file is
  treated as malformed, not as a variant.
- The `spec.md` §6 justification is written beside the raises: a block comment
  stating that refusing is correct **only** because `capture.py` pins the one
  real source to `CHANNELS = 1` at `SAMPLE_RATE = 16 kHz`, that a source
  without such a pin (camera frames, whose resolution legitimately varies) must
  convert rather than refuse, plus a per-raise inline comment naming the pin
  each one rests on. §6 says the raises "each carry a comment", so each does.
- `tests/test_voiceprint.py` — two new tests,
  `test_load_wav_refuses_multichannel` and
  `test_load_wav_refuses_wrong_sample_rate`. Both write a real file with
  `soundfile` into `tmp_path` and read it back through `load_wav`; neither
  monkeypatches `sf.read`. Each asserts on the message content (`2 channels`,
  `44100 Hz`), so a generic raise would not satisfy them. `soundfile` is now
  imported at the top of the test module.

**`_resample` was deliberately left in place** — `embed` still calls it, and
deleting it here would break Task 2's starting state. Task 1 removed one of its
two callers, nothing more.

## The precondition I checked before writing the raises

Every committed voiceprint fixture is **16 kHz mono PCM_16** (verified with
`soundfile.info` across all 11 `.wav` files), and every caller of `load_wav` in
the repo — `tests/test_voiceprint.py`, `tests/test_booth_api.py`,
`tests/test_middlelock.py` — reads only from that fixture directory. There is
no production caller. So the new raises cannot fire on any existing test, and
the expectation is that the suite count **rises by 2 and nothing fails**.

## What I ran (disclosure — the Gate is still fresh eyes' job)

- `uv run ruff check .` → **exit 0** ("All checks passed!"). This is the step-5
  quick lint, and it is also a Gate command; the verifier should re-run it
  rather than trust this line.
- An `ast.parse` syntax check on both changed files → ok.
- `soundfile.info` over the fixtures (the precondition above).
- **I did NOT run `uv run pytest`, nor any of the §5 verification commands.**
  Task 1's own §5-derived criteria are unrun by me, on purpose.

## Things I am not certain about

1. **`spec.md` §6 says the raises "each carry a comment"; `plan.md` Task 1 says
   "a comment" (singular).** I wrote one shared block comment carrying the full
   doctrine plus a short inline comment on each `if`, rather than duplicating
   the paragraph twice — duplicating it would have been worse code. The §6
   Gate command only checks that `capture.py` appears in `load_wav`'s source,
   which it does. If a verifier reads "each" as demanding two full statements,
   that is a fair REJECT and cheap to fix.
2. **The mono check is `data.ndim != 1`, not `data.ndim > 1`.** That is
   deliberate: §5 cmd 1 asserts the literal string `.ndim > 1` is absent from
   the module, and `!= 1` is the more exact "not mono" test anyway. It reads
   `data.shape[1]` for the channel count, which is safe because `sf.read` with
   `always_2d=False` returns 1-D or 2-D and nothing else.
3. **Order:** the rate check runs before the channel check, matching §4's
   wording order. A stereo 44.1 kHz file would therefore report the rate first.
   No test or criterion depends on which fires first.

## Ledger

| Task | State |
|---|---|
| 1 — `load_wav` refuses bad audio | **`REVIEW`** ← this session, `rejects: 0` |
| 2 — remove the `sample_rate` params, delete `_resample` | `TODO` |
| 3 — **LAST** — stop the same-speaker test overclaiming | `TODO` |

## Still not to be re-litigated (carried forward)

1. **Do not re-propose the ordering assertion** on the `enroll1`/`enroll5` pair
   — drafted during grilling and disproved by measurement (a dummy embedder
   orders it correctly too: 0.077 < 0.113). `plan.md` memory spine item 1.
2. **Do not move a threshold to make anything pass.** `ACCEPT_CUTOFF = 0.45`
   and `REJECT_CUTOFF = 0.65` are pinned on Tasks 2 and 3.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:112`) —
   `spec.md` §3 keeps it deliberately.
4. **Do not expect a manual check.** `spec.md` §5 records why this feature has
   none. A verifier should **not** `ESCALATE_HUMAN` over its absence here.

## Verifier path

**Subagent**, spawned by this session with `formats/VERIFIER-PROMPT.md`
**verbatim** (fill-ins only). This session is the executor of the returned
verdict and never overrides it; wanting to override = `ESCALATE_HUMAN`.

## Pending guardrail

None.

## Commits

- Task 1: `b063f30` (DOING) → **`a6572c0` (build)**
- **Base for the Gate diff: `b063f30`** · head: **`a6572c0`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.
- Session base was `5d39918`. Remote `origin` exists (private); pushes happen
  at the feature-end checkpoint, not here.

## next_action

**Verify Task 1** — clean-context subagent, `formats/VERIFIER-PROMPT.md`
verbatim, base `b063f30`, head `a6572c0`.

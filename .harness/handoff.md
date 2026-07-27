# Handoff — F5.5 Task 1 retry 1 built, awaiting the clean-context verifier

**Mode 4.** Task 1 is `REVIEW` with `rejects: 1`. The next move belongs to the
verifier, not to a human — the approved spec's `Mode:` line is the standing
"go" inside F5.5, and one retry remains well inside the 3-cap.

## What changed

**Task 1 — `load_wav` refuses bad audio instead of silently converting it.**

- `src/voicelock/voiceprint.py` (`load_wav` only, unchanged since the first
  attempt) — the stereo downmix and the resample call are replaced by two
  `ValueError`s that name the offending value: the real sample rate
  (`got 44100 Hz`) and the real channel count (`got 2 channels`). The docstring
  records that a non-conforming file is treated as malformed, not as a variant.
  The mono check is written `data.ndim != 1`, deliberately — `spec.md` §5 cmd 1
  asserts the literal string `.ndim > 1` is absent from the module, and `!= 1`
  is the more exact "not mono" test anyway.
- The `spec.md` §6 justification is written beside the raises: a block comment
  stating that refusing is correct **only** because `capture.py` pins the one
  real source to `CHANNELS = 1` at `SAMPLE_RATE = 16 kHz`, that a source
  without such a pin (camera frames, whose resolution legitimately varies) must
  convert rather than refuse, plus a per-raise inline comment naming the pin
  each one rests on.
- `tests/test_voiceprint.py` — two tests,
  `test_load_wav_refuses_multichannel` and
  `test_load_wav_refuses_wrong_sample_rate`. Both write a real file with
  `soundfile` into `tmp_path` and read it back through `load_wav`; neither
  monkeypatches `sf.read`. Each asserts on the message content (`2 channels`,
  `44100 Hz`), so a generic raise would not satisfy them. `soundfile` is
  imported at the top of the test module.

**`_resample` was deliberately left in place** — `embed` still calls it, and
deleting it here would break Task 2's starting state. Task 1 removed one of its
two callers, nothing more.

## The retry (what Gate FAIL #1 found and what it changed)

The first attempt (`b063f30` → `a6572c0`) failed **one** criterion: `plan.md`
done-criterion 2, the second half of `spec.md` §5 cmd 2. That command counts the
**literal substring** `pytest.raises(ValueError)`, and the tests were spelled
`pytest.raises(ValueError, match="2 channels")` — the comma breaks the match, so
the count measured 0, not 2. Every other criterion passed on that attempt,
including `uv run pytest` at **124 passed** (up from 122, 0 failed).

The fix is in the test spelling only: `with pytest.raises(ValueError) as
excinfo:` followed by `assert "2 channels" in str(excinfo.value)`. That
satisfies the command as written **and** keeps the message assertion, so the
tests remain stronger than the criterion demands. No production code changed on
this retry.

**I did not touch the criterion.** It is `spec.md` §5 cmd 2, human-approved, and
repeated verbatim in Task 3's full list; editing it to fit the code would be a
spec amendment needing a fresh approval, not an implementor's call.

## The precondition I checked before writing the raises

Every committed voiceprint fixture is **16 kHz mono PCM_16** (verified with
`soundfile.info` across all 11 `.wav` files), and every caller of `load_wav` in
the repo — `tests/test_voiceprint.py`, `tests/test_booth_api.py`,
`tests/test_middlelock.py` — reads only from that fixture directory. There is
no production caller. So the new raises cannot fire on any existing test; the
first attempt's Gate confirmed this empirically at 124 passed / 0 failed.

## What I ran (disclosure — the Gate is still fresh eyes' job)

- `uv run ruff check .` → **exit 0** ("All checks passed!").
- The **one failing criterion, re-run after the fix** (the implement skill's
  bug-fix reproduction clause): `uv run python -c "...t.count(
  'pytest.raises(ValueError)') >= 2..."` → **exit 0**.
- Earlier, before the first attempt: an `ast.parse` syntax check on both
  changed files, and `soundfile.info` over the fixtures.
- **I did NOT run `uv run pytest`, nor the §5 verification commands, on this
  retry.** The 124-passed figure above is the *verifier's* measurement from
  attempt 1, not mine.

## Things I am not certain about

1. **`spec.md` §6 says the raises "each carry a comment"; `plan.md` Task 1 says
   "a comment" (singular).** I wrote one shared block comment carrying the full
   doctrine plus a short inline comment on each `if`, rather than duplicating
   the paragraph twice. The §6 Gate command only checks that `capture.py`
   appears in `load_wav`'s source, which it does, and the attempt-1 verifier
   accepted the arrangement in its scope check. If "each" is read as demanding
   two full statements, that is a fair REJECT and cheap to fix.
2. **Order:** the rate check runs before the channel check, matching §4's
   wording order. A stereo 44.1 kHz file would therefore report the rate first.
   No test or criterion depends on which fires first.
3. **`data.shape[1]`** is read for the channel count. Safe because `sf.read`
   with `always_2d=False` returns 1-D or 2-D and nothing else; a deeper array
   would raise `IndexError` rather than the intended `ValueError`, but no
   decoder path produces one.

## Ledger

| Task | State |
|---|---|
| 1 — `load_wav` refuses bad audio | **`REVIEW`**, `rejects: 1` ← this session |
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

None. (A candidate is visible — "a verification command that matches source
text literally must be written against the spelling the code will actually
use" — but guardrails are the `learn` scan's output at wrap-up, not an
implementor's, so it is noted here and nowhere else.)

## Commits

- Attempt 1: `b063f30` (DOING) → `a6572c0` (build) → `e21665c` (bookkeeping)
  → `b9007a3` (**GATE FAIL #1** recorded)
- Retry 1: `a16841f` (DOING) → **`d110551` (build)**
- **Base for the Gate diff: `a16841f`** · head: **`d110551`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.
- Session base was `5d39918`. Remote `origin` exists (private); pushes happen
  at the feature-end checkpoint, not here.

## next_action

**Verify Task 1 (retry 1)** — clean-context subagent,
`formats/VERIFIER-PROMPT.md` verbatim, base `a16841f`, head `d110551`.

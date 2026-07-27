# Handoff — F5.5 Task 2 built, awaiting the clean-context verifier

**Mode 4.** Task 2 is `REVIEW`, `rejects: 0`. The verifier starts itself; no
human gate until the feature-end checkpoint.

## Changed

**Task 2 — remove the `sample_rate` parameters and delete `_resample`.**
`src/voicelock/voiceprint.py` only. Pure subtraction, no test changes:

- `embed` loses its `sample_rate` parameter and the `if sample_rate !=
  SAMPLE_RATE: sig = _resample(...)` branch.
- `compare` loses the parameter and its pass-through — `embed(live_audio,
  sample_rate)` is now `embed(live_audio)`. The signature fits one line again.
- `_resample` is deleted; it was callerless once those two went (Task 1 removed
  `load_wav`'s call).
- **One line added, not subtracted:** `embed`'s docstring now records where the
  16 kHz expectation comes from — `capture.py` pins the mic, `load_wav` refuses
  anything else. The parameter that used to imply it is gone, so the constraint
  would otherwise be invisible at the call site. Flagging it because the task
  was specified as pure subtraction and this is the one thing that is not.

**Not touched, on purpose:** `load_reference`'s re-normalize (`:112`) is a
`spec.md` §3 non-goal; the F5.5 §5 cmd 3 constants are untouched.

## Caller-safety — re-verified, not inherited

`spec.md` §4 asserts the only production callers are `app.py:66`, `:221` and
`:245`. I re-grepped `src/` and `tests/` rather than trusting it: every call
site passes one positional argument, or `path=` as a keyword —
`voiceprint.embed(signal[...])`, `voiceprint.embed(buf)`,
`voiceprint.compare(buf, path=self.ref_path)`, and 14 single-argument call
sites across `tests/test_booth_api.py`, `tests/test_middlelock.py` and
`tests/test_voiceprint.py`. Removing a **middle** positional parameter from
`compare` is therefore safe: nobody was passing a third argument positionally.

## Out-of-scope discovery (recorded, not built)

`_resample` was the repo's only `torchaudio` import, so `torchaudio>=2.11.0` is
now declared with no first-party use. **Not acted on** — `spec.md` §4 forbids
touching `pyproject.toml`, it is not in §1, and it would change nothing:
`speechbrain` declares `torchaudio>=2.1.0` itself (verified via
`importlib.metadata.requires`), so the resolved environment is identical either
way. Written up in
`.out-of-scope/2026-07-26-torchaudio-no-longer-imported-directly.md` per
`spec.md` §5's Modes 3–4 default.

## What I ran (disclosure — the Gate is fresh eyes' job)

- `uv run ruff check .` → **exit 0** (the step-5 quick lint).
- Two greps as reference-validation, not verification: no `_resample` /
  `sample_rate` survives in the module (the only `ndim` left is Task 1's
  `!= 1`, which is what `spec.md` §5 cmd 1's `'.ndim > 1' not in s` wants), and
  the caller sweep above.
- `importlib.metadata.requires('speechbrain')` for the out-of-scope note.
- **I did NOT run `uv run pytest` or any §5 verification command.**

## Things I am not certain about

1. **The added docstring lines** (see "Changed"). Justified as replacing
   information the deleted parameter used to carry, but it is an addition in a
   deletion task and a reviewer may fairly call it scope creep.
2. **The suite count should stay at 124** — Task 2 changes no test. If it moves
   at all, a caller was missed and that is the finding, not a nuisance
   (`plan.md` Task 2 notes say exactly this).

## Ledger

| Task | State |
|---|---|
| 1 — `load_wav` refuses bad audio | `DONE`, `rejects: 1`, verdict archived |
| 2 — remove the `sample_rate` params, delete `_resample` | **`REVIEW`**, `rejects: 0` ← this session |
| 3 — **LAST** — stop the same-speaker test overclaiming | `TODO` |

## Pending guardrail

**One, unchanged from Task 1's wrap-up, still awaiting the human's yes/no** —
not written to `project.md`:

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
>     appear in `tests/test_facedetect.py`, and F5.5 carries five more.
>     Task 2 dodged the `.ndim > 1` one only by deliberate spelling, which is
>     exactly the fragility the rule names. Enforcement beats memory and is
>     cheap — write the criteria as regexes — but that changes `spec.md`'s
>     Verification commands, so it goes through the spec/approval path.
>   - _Overlap-checked_ against all six current guardrails: closest is "a test
>     must assert something that would break if the behaviour were removed", and
>     it is the converse — that catches a **test** that passes vacuously; this
>     catches a **criterion** that fails a sound test. Low overlap.

## Still not to be re-litigated

1. **Do not re-propose the ordering assertion** on the `enroll1`/`enroll5` pair
   — disproved by measurement (0.077 < 0.113 from a dummy embedder).
2. **Do not move a threshold to make anything pass** — §5 cmd 3 pins both.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:112`).
4. **Do not expect a manual check.** `spec.md` §5 records why this feature has
   none; a verifier should **not** `ESCALATE_HUMAN` over its absence.

## Verifier path

**Subagent**, spawned by this session with `formats/VERIFIER-PROMPT.md`
**verbatim**. This session executes the returned verdict and never overrides it;
wanting to override = `ESCALATE_HUMAN`.

## Commits

- Task 1: `b063f30`…`a86f8d0` (DONE, verdict archived)
- Task 2: `0a7d8a9` (DOING) → **`d6af571` (build)**
- **Base for the Gate diff: `0a7d8a9`** · head: **`d6af571`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.
- Session base was `5d39918`. Remote `origin` exists (private); nothing pushed —
  pushes are human-gated at the feature-end checkpoint.

## next_action

**Verify Task 2** — clean-context subagent, `formats/VERIFIER-PROMPT.md`
verbatim, base `0a7d8a9`, head `d6af571`.

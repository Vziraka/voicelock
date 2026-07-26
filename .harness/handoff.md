# Handoff — F4.5 Task 2 built, awaiting verification · 2026-07-26

Session type: `/implement` (build), chained after Task 1's completed wrap-up.
Task 2 of 3. Mode 3.

## Entry gate — quoted, not remembered
- Trigger satisfied per the implement skill: Task 1's wrap-up **fully
  completed** — verdict file `memory/verdicts/2026-07-26-F4.5-T1.json` exists
  and state was committed (`8f86fc7`). A previous task merely finishing is not
  the trigger; the artifacts are.
- `plan.md` ledger scan: the one `DONE` task (Task 1) has its matching verdict
  file. Nothing to invalidate.
- Not a retry — `rejects: 0`, feedback log empty.
- No pending guardrail to surface.

## Changed this session
- **`tests/test_capture.py`** — the only file. `capture.py` and every other
  source file are byte-identical to base, which is why all of this passes at
  base. Added:
  - `ReentrantTeardown(BaseException)` and `FakeStream`'s `deliver(mono)` /
    `delivering` / `callback_stopped` / `_forbid_reentrant_teardown`.
  - Three tests, appended after the existing ones:
    `test_callback_path_carries_audio_without_pump`,
    `test_teardown_from_inside_the_callback_trips_the_wire`,
    `test_delivery_halts_once_the_callback_raises_callback_stop`.
  - The five pre-existing pump-driven tests are **unmodified** (spec §3: "the
    pump-driven tests stay").
- **`plan.md`** — Task 2 `TODO → DOING` (committed first, `0106418`) → `REVIEW`;
  phase line updated.
- **`handoff.md`** — this file.

## A judgment call the verifier should see (not scope creep)
`plan.md` Task 2 names **two** tests to add; I added **three**. The extra one is
`test_delivery_halts_once_the_callback_raises_callback_stop`, and it exists to
satisfy the earned guardrail (`project.md` 2026-07-26: no branch that no caller
and no test exercises). Task 2 is required to build branch (b) — "it **stops
delivering** once the callback raises `sd.CallbackStop`" — but the plan's two
named tests exercise only (a) and (c). Branch (b) would otherwise sit
uncovered at this task's HEAD until Task 3 arrived. The test is six lines,
drives `FakeStream` directly (no `CaptureEngine`, so no deadlock risk at base),
and follows the plan's own reasoning for why branch (c) got a test:
"testing the safety net on purpose, not gold-plating".

I did **not** log this in `memory/deviations.md` — nothing in the plan forbids
covering a branch it required, so no rule was reinterpreted. Flagged here so it
is scored deliberately rather than discovered.

## Two design points worth a look
- **`ReentrantTeardown` subclasses `BaseException`, not `Exception`** — the trap
  the plan session found (`capture.py:135-142` wraps `stream.stop()` and
  `stream.close()` in `except Exception: pass`). The tripwire test proves the
  escape directly rather than asserting the class hierarchy: it wraps
  `deliver()` in `except Exception: pass` — mirroring `_close_stream` — and
  still expects the raise to reach `pytest.raises`.
- **`deliver()` catches `sd.CallbackStop` rather than re-raising it.** That
  mirrors PortAudio, which absorbs `CallbackStop` and stops the stream. Task 3's
  "the supported stop is used" test therefore asserts against
  `stream.callback_stopped` / `stream.delivering`, or calls `_on_audio`
  directly — the propagation is observable either way.

## What I ran (disclosure)
Only the quick local check the implement skill permits:
- `uv run ruff check .` → `All checks passed!` (ruff parses the file, so this is
  also the syntax check)

I did **not** run `uv run pytest` or `uv run pytest tests/test_capture.py -q`.
Those are Gate commands and stay reserved for fresh eyes. **Stated plainly
because it is the material risk on this task:** these are newly authored tests
that I have not executed. The plan asserts they pass at base; my confidence
comes from reading, not from a run. If any of them is wrong, the Gate is where
that surfaces.

## next_action
1. **Verify Task 2** with clean context — `formats/VERIFIER-PROMPT.md` verbatim:
   `/verify-gate` then `/verify-review`. Task 2's done-criteria are its four
   commands in `plan.md`. Task 2 of 3, so the FULL spec §5 list is **not** due
   here — it lands on Task 3.
2. **Do not score the missing cap-through-callback test as a coverage gap** —
   `plan.md` Task 2 rules it out explicitly ("at base that path deadlocks…it
   belongs to Task 3").
3. On APPROVE → `wrap-up`, then Mode 3 chains **Task 3** (`_on_audio` raises
   `sd.CallbackStop`; the fix plus its regression tests; FULL spec §5).
4. Task 3 will reach the Gate as **ESCALATE_HUMAN** on spec §5's required
   31-second live Booth check. Do not mark it `DONE` or write its verdict until
   the human attests it (F3-T5 / F4-T5 precedent).

## Commits
Base `8f86fc7` → build commit `f2a1013` (this file's bookkeeping commit follows,
per the two-commit rule). `0106418` is the committed `DOING` write.
Remote: **none** — local history only, nothing pushed.

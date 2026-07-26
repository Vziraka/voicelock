# Handoff — F4.5 Task 3 built (the LAST task), awaiting verification · 2026-07-26

Session type: `/implement` (build), chained after Task 2's completed wrap-up.
Task 3 of 3 — the feature's last. Mode 3.

## Entry gate — quoted, not remembered
- Trigger satisfied: Task 2's wrap-up **fully completed** — verdict
  `memory/verdicts/2026-07-26-F4.5-T2.json` written and state committed
  (`f12dd19`).
- `plan.md` ledger scan: both `DONE` tasks (1 and 2) have matching verdict
  files. Nothing to invalidate.
- Not a retry — `rejects: 0`, feedback log empty. No pending guardrail.

## Changed this session
- **`src/voicelock/capture.py`** — five lines replaced by four inside
  `_on_audio`. The `_close_stream()` / `status = IDLE` / `_started_at = None`
  block is gone; the cap now does exactly one thing:
  `raise sd.CallbackStop`. The stale comment (which claimed the code marked
  for stop via pump/stop while the code did the opposite) is corrected to
  describe the deadlock it avoids. **Nothing else in the file changed** —
  `_close_stream` keeps its try/except and its caller in `stop()`; `pump()`,
  `start()`, `stop()`, `toggle()`, `_ingest`, and the mic-error path are
  untouched. No new state, no new flag.
- **`tests/test_capture.py`** — two regression tests plus a small
  `_recording_engine_with_stream()` helper that both use (spec §5 feature
  tests 2 and 3). Task 2's harness is unmodified; the five pump-driven tests
  are unmodified.
- **`plan.md`** — Task 3 `TODO → DOING` (committed first, `a130ac5`) →
  `REVIEW`; phase line updated. **`handoff.md`** — this file.

## Repro — seen failing at base, passing at head (same command both times)
`uv run pytest tests/test_capture.py -q`

- **At base** (`capture.py` unchanged): `2 failed, 8 passed in 0.47s`. Both new
  tests failed **fast**, not as a hang — which is the whole point of Task 2's
  tripwire. The traceback named the root cause, not the symptom:
  ```
  tests\test_capture.py:55: in deliver   self.callback(indata, indata.shape[0], None, None)
  src\voicelock\capture.py:118: in _on_audio      self._close_stream()
  src\voicelock\capture.py:136: in _close_stream  stream.stop()
  E   test_capture.ReentrantTeardown: stream.stop() called from inside the callback
  ```
- **At head**, same command: `10 passed in 0.35s`.

## What I ran (disclosure)
- `uv run pytest tests/test_capture.py -q` — twice, base and head, as the
  bug-fix reproduction the implement skill requires. This is a Gate command and
  I am naming it explicitly rather than leaving it implied.
- `uv run ruff check .` → `All checks passed!` (the permitted quick local check)

I did **not** run `uv run pytest` (whole suite), either source-assertion
one-liner, or the manifest check. Those stay reserved for fresh eyes, and the
Gate re-runs everything including the two above.

## One deliberate non-change the reviewer may query
`pump()`'s docstring (`capture.py:98-102`) still says live use "can call it
periodically (or rely on the stream callback) to enforce the 30s auto-stop".
I left it alone on purpose: `spec.md` §4 cites that exact docstring approvingly
when accepting the "cap reached with no pump running" edge case, and
`plan.md` Task 3 names precisely one comment to correct — the one on the old
`capture.py:117`. Editing it would be scope the task did not ask for. Flagging
it so the choice is visible rather than assumed.

## next_action
1. **Verify Task 3** with clean context — `formats/VERIFIER-PROMPT.md` verbatim.
   This is the feature's LAST task, so the Gate runs the **FULL `spec.md`
   Verification list**, not `plan.md` done-criteria alone.
2. **Expect `ESCALATE_HUMAN`.** Spec §5's final line is a required,
   human-attested manual check that no agent can perform:
   `uv run voicelock` → press Record → let it run **past 30 seconds without
   pressing Stop** → the recording auto-stops on its own, the window **stays
   responsive**, and Play plays back the captured audio. Do **not** mark Task 3
   `DONE` and do **not** write its verdict file until the human attests it
   (F3-T5 / F4-T5 precedent). The automated tests prove the fix's logic against
   fakes; they do not prove `sd.CallbackStop` unwinds cleanly through
   sounddevice's CFFI boundary on real hardware — that is what this line covers.
3. After the human attests → `wrap-up` closes Task 3 **and** the feature:
   check `roadmap.md`'s F4.5 box, refresh `memory/codebase-map.md` (or stamp it
   `STALE`), write the Mode 3 **completion report** into `handoff.md`, then
   **wait** for the human at the feature-end checkpoint (commit message
   approval; there is no remote, so no push).
4. Then: `/spec` for **F5 — Camera booth**, starting with its TECH-PICK
   (offline face detect / landmark / embedding stack). Named only, not started.

## Commits
Base `f12dd19` → build commit `8267878` (this file's bookkeeping commit follows,
per the two-commit rule). `a130ac5` is the committed `DOING` write.
Remote: **none** — local history only, nothing pushed.

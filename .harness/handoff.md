# Handoff — F4.5 Task 3 verified, BLOCKED on the human's live-demo attestation · 2026-07-26

Session type: `/implement` Task 3 → subagent verification → **stop**.
Mode 3. All three tasks are built. Nothing left to build in this feature.

## Status
| Task | State | Verdict |
|---|---|---|
| 1 — declare `soundfile` | `DONE` | `memory/verdicts/2026-07-26-F4.5-T1.json` — APPROVE, first pass |
| 2 — `FakeStream` real callback + tripwire | `DONE` | `memory/verdicts/2026-07-26-F4.5-T2.json` — APPROVE, first pass |
| 3 — `_on_audio` raises `sd.CallbackStop` | **`REVIEW`** | **none yet — deliberately** |

`rejects: 0` on all three. Task 3 has **no verdict file on purpose**: the Gate
returned `ESCALATE_HUMAN`, and `plan.md` Task 3 plus the F3-T5 / F4-T5 precedent
forbid marking it `DONE` or writing its verdict until the human attests the live
demo.

## Task 3's verification — the FULL spec §5 list, by a clean-context subagent
Six automated commands, all exit 0:
- `uv run ruff check .` → `All checks passed!`
- `uv run pytest` → `88 passed in 50.42s`, 0 failed (all F1–F4 still green)
- `uv run pytest tests/test_capture.py -q` → `10 passed in 0.32s`
- the `_on_audio` source assertion (no `_close_stream`, does use `CallbackStop`) → exit 0
- the `soundfile` manifest assertion → exit 0
- the `callback` tripwire on the test file → exit 0

Seventh line — **NOT RUN, and no agent can run it.** Review returned **APPROVE**
on both axes with no findings, conditional on that attestation.

## ▶ What the human needs to do (the only open item)
Run spec §5's required manual check:

```
uv run voicelock
```
→ press **Record** → let it run **past 30 seconds without pressing Stop**.

Attest all three observables:
1. the recording **auto-stops on its own**;
2. the window **stays responsive** — buttons still react, no freeze;
3. pressing **Play** plays back the captured audio.

This is the exact path that deadlocks at `9d0b137`-era HEAD. The automated tests
prove the fix's logic against fakes; they do **not** prove that
`sd.CallbackStop` unwinds cleanly through sounddevice's CFFI boundary on real
hardware. That gap is what this check closes — a required check, not accepted
risk (spec §2's Mode 3 resolution).

**Then say so**, and the next session runs `wrap-up` for Task 3 — which also
closes the feature.

## What happens after the attestation (so the next session doesn't improvise)
`wrap-up` at Modes 3–4 with the feature complete:
1. ADR gate · 2. `learn` scan + write `memory/verdicts/2026-07-26-F4.5-T3.json`
   (`gate` must record the ESCALATE_HUMAN → human-attested resolution in its
   `note`, honestly, not as a plain PASS) · 3. `handoff.md` · 4. **`roadmap.md`:
   check the F4.5 box**, and refresh `memory/codebase-map.md` or stamp it
   `STALE` (feature-complete extra) · 5. `plan.md`, `DONE` last ·
   6. the Mode 3 **completion report** into `handoff.md`, then **wait** for the
   human at the feature-end checkpoint (commit message approval; no remote, so
   commit only, no push).

If the demo **fails**, that is a Gate FAIL: append the reasons to Task 3's
feedback log, set it back to `TODO`, and `rejects: 0 → 1` (cap 3).

## Changed this session (three build↔verify cycles, all in one session)
- `pyproject.toml`, `uv.lock` — `soundfile>=0.14.0` declared (Task 1).
- `tests/test_capture.py` — `ReentrantTeardown` + `FakeStream.deliver()` and the
  re-entrant guard, then five new tests total (Tasks 2 and 3). The five
  pre-existing pump-driven tests are unmodified throughout.
- `src/voicelock/capture.py` — the fix, and only the fix: inside `_on_audio`,
  the `_close_stream()` / `IDLE` / `_started_at = None` block replaced by
  `raise sd.CallbackStop`, and the stale comment corrected (Task 3).
- State: `plan.md`, this file, two verdict files.

## Repro evidence for Task 3 (base vs head, same command)
`uv run pytest tests/test_capture.py -q` — base: `2 failed, 8 passed in 0.47s`,
failing **fast** via Task 2's tripwire with the traceback naming
`capture.py:118 _close_stream` → `capture.py:136 stream.stop()`; head:
`10 passed in 0.35s`.

## Pending guardrail
None so far. Task 3's `learn` scan has not run yet — it runs inside the
post-attestation wrap-up and may propose one.

## next_action
1. **HUMAN: run the 31-second live Booth check above and attest it.** Nothing
   else can proceed. This is the feature's designed human touchpoint.
2. Then `wrap-up` Task 3 + the feature, per the sequence above.
3. Then the feature-end checkpoint (commit message approval; no push, no remote).
4. Only after that: `/spec` for **F5 — Camera booth**, starting with its
   TECH-PICK (offline face detect / landmark / embedding stack).

## Commits
This session: `727fbbc` (base) → `da7b8f9` `0ae0fd3` `b48f546` `8f86fc7`
(Task 1) → `0106418` `f2a1013` `fc7f5c8` `f12dd19` (Task 2) → `a130ac5`
`8267878` `99573c9` (Task 3 build) → the state commit carrying this file.
Task 3's build range is `f12dd19..8267878`.
Curate check: 21 verdict `.json` files vs `project.md`'s "verdicts then: 19" →
**2 since the last curate; not due** (threshold 10). Task 3's verdict will make 22.
Remote: **none** — local history only, nothing pushed.

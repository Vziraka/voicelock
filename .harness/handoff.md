# F4.5 — COMPLETION REPORT · DONE 2026-07-26 (Mode 3)

**Capture callback + test-harness hygiene.** Three tasks, three APPROVEs, zero
rejects, one session. Human attested the live Booth check 2026-07-26.

## Outcome vs the spec's Outcome section

Spec §1 promised three things. All three landed.

1. **"The capture callback no longer deadlocks against itself."** ✅
   `capture.py:116-120` — at `max_seconds` the callback raises
   `sd.CallbackStop` and does nothing else. The `_close_stream()` /
   `status = IDLE` / `_started_at = None` block is gone, so the callback never
   waits on `Pa_StopStream`, which blocks until the callback returns. No new
   state, no new flag: `pump()`'s existing cap check (`capture.py:107-108`)
   does the teardown and `app.py`'s 50 ms loop fires `onCaptureEnded` exactly
   as before. The comment that claimed the opposite of what the code did now
   describes the deadlock it avoids.
2. **"The tests drive the real callback path."** ✅
   `FakeStream` keeps the `callback=` it was handed and delivers through it in
   PortAudio's own shape — 2-D `(frames, channels)` — stopping once the
   callback raises `CallbackStop`. `_on_audio` went from **zero** coverage to
   five tests. The re-entrant-teardown tripwire raises a `BaseException`
   subclass so it escapes `_close_stream`'s blanket `except Exception: pass`;
   without that, the regression would have surfaced as a **hung suite** instead
   of a fast failure. Measured: the defect fails in **0.47 s**.
3. **"`soundfile` is declared."** ✅ `pyproject.toml:11`
   `"soundfile>=0.14.0"`. `voiceprint.py:150` imports it inside `load_wav`; it
   previously reached the environment only as a SpeechBrain transitive.

Demo line delivered: a recording left past 30 seconds auto-stops with the audio
intact instead of freezing — **attested by the human**, not inferred.

## Final Gate evidence — the FULL spec §5 list

| Command | Exit |
|---|---|
| `uv run ruff check .` | **0** — `All checks passed!` |
| `uv run pytest` | **0** — `88 passed in 50.42s`, 0 failed (all F1–F4 green) |
| `uv run pytest tests/test_capture.py -q` | **0** — `10 passed in 0.32s` |
| `_on_audio` source assertion (no `_close_stream`, uses `CallbackStop`) | **0** |
| `soundfile` manifest assertion | **0** |
| `callback`-in-test-file tripwire | **0** |
| **Manual, human-attested:** `uv run voicelock` → Record → past 30 s | **attested 2026-07-26** — auto-stopped, window responsive, Play worked |

The Gate first returned **ESCALATE_HUMAN**, not PASS: six commands exited 0 and
the seventh cannot be run by an agent. Task 3 was held at `REVIEW` with no
verdict file until the attestation arrived (F3-T5 / F4-T5 precedent). The
verdict file records that sequence honestly rather than as a plain PASS.

Suite growth across the feature: **83 → 88** tests (5 new, all on the callback
path). Runtime `50.42 s` against F4's `48.15 s` baseline — the new tests cost
well under a second; the rest is torch + ECAPA + Argon2id, as before.

## Retry counts

**`rejects: 0` on all three tasks.** Every task approved on its first
verification, each by a clean-context subagent using
`formats/VERIFIER-PROMPT.md` verbatim. No task was ever `BLOCKED`.

| Task | Verdict file | Result |
|---|---|---|
| 1 — declare `soundfile` | `2026-07-26-F4.5-T1.json` | APPROVE, first pass |
| 2 — `FakeStream` real callback + tripwire | `2026-07-26-F4.5-T2.json` | APPROVE, first pass |
| 3 — `_on_audio` raises `sd.CallbackStop` | `2026-07-26-F4.5-T3.json` | APPROVE (Gate ESCALATE_HUMAN → attested) |

## Deviations recorded during the feature

**None.** `memory/deviations.md` was not appended to — no rule proved
unfollowable and no judgment call required reinterpretation.

The one call worth naming (disclosed in Task 2's handoff, and scored
deliberately by that verifier rather than discovered): Task 2 added a **third**
test where `plan.md` named two. The plan mandated branch (b) — "stops
delivering once the callback raises `sd.CallbackStop`" — but named tests only
for branches (a) and (c), so (b) would have sat uncovered at that task's HEAD,
which is precisely what the earned guardrail forbids. Covering a branch the
plan required is not a deviation from the plan, so no log entry was owed.

## Anything escalation-worthy that resolved itself

- **The repro was seen failing before the fix.** Same command at base and head:
  `2 failed, 8 passed in 0.47s` → `10 passed in 0.35s`. The base traceback named
  the root cause, not the symptom: `capture.py:118 _close_stream` →
  `capture.py:136 stream.stop()` → `ReentrantTeardown`.
- **The sharpest trap was caught at plan time, not build time.** `capture.py`
  swallows `Exception` around `stream.stop()`/`close()`, so a plain-`Exception`
  tripwire would have been silently eaten and Task 3's regression would have
  passed with the defect still live. The plan flagged it; Task 2 raised a
  `BaseException` subclass; Task 2's test proves the escape empirically by
  wrapping `deliver()` in the same blanket handler.
- **`torchaudio` stayed ruled out on evidence.** The calibration note had
  suggested it as the zero-cost answer, but `torchaudio.load` on 2.11.0 raises
  `ImportError: TorchCodec is required`, so it would have added a genuinely new
  dependency. Settled at TECH-PICK time; nothing re-litigated during the build.

## Pending guardrail — NONE. Approved and written 2026-07-26.

Task 3's `learn` compound scan was the first in this feature to clear the bar
(Tasks 1 and 2 both recorded "none"). The human **approved** it after the
feature-end checkpoint, and it is now the repo's **third** earned guardrail in
`constitution/project.md`, listed first. Nothing is pending.

Task 3's verdict file still reads `"lesson": "proposed — pending approval"` —
that is correct and deliberate: verdicts are append-only and record what was
true at the moment of the scan. This section is the record of the resolution.

The written entry:

> - **[Forbidden]** A test double for a stream or device must deliver data
>   through the **real callback it was handed** — a fake that only exposes a
>   polling method leaves the callback path at zero coverage. `warn` ·
>   expires: 2027-01-31
>   - _Evidence:_ F1's `FakeStream` never invoked the callback it was
>     constructed with (the word `callback` did not appear in
>     `tests/test_capture.py`), so `_on_audio` shipped with **zero** coverage and
>     a self-deadlock — `_close_stream()` → `stream.stop()` from inside the
>     callback, where `Pa_StopStream` blocks until the callback returns. It
>     survived F2, F3 and F4 undetected and cost a whole inserted feature
>     (F4.5) to close. F5 adds a camera stream with its own frame callback and
>     was going to copy the same fake-stream pattern — which is the stated
>     reason F4.5 was inserted before F5 at all.
>   - _Added:_ 2026-07-26

Why prose and not enforcement (the `learn` skill asks this first): the natural
mechanism is a shared fake-stream base class in `tests/`, but F5's camera fake
does not exist yet, so extracting that abstraction now would be speculative and
would trip the code-quality floor. The narrower enforcement — spec §5's
`assert 'callback' in <test file>` — already exists for `test_capture.py` and
can be repeated per-module in F5's own spec. Judging what counts as "the real
callback" for a not-yet-chosen camera library needs judgment, which is what
prose is for.

Overlap-checked against both existing guardrails: the 2026-07-26
"no unexercised helper, method, or branch" rule shares the *symptom* (untested
surface) but not the root cause — that one is about speculative production code
being added; this one is about a test harness structurally unable to reach a
real production path. Different fix, different files. An addition, not an edit.
The UI-state-mirror rule is unrelated.

## next_action

**F4.5 is closed. Nothing is outstanding — both human items are resolved:**
the feature-end checkpoint was approved and committed (`93bc887`), and the
guardrail was approved and written.

1. **`/spec` for F5 — Camera booth.** It starts with a **TECH-PICK** (offline
   face detect / landmark / embedding stack) — that is a new dependency, so it
   needs `formats/TECH-PICK.md` and your sign-off before anything is installed.
   Not started here.
2. **Carry into F5:** Task 2's fake-stream shape is what F5's camera fake
   should copy — deliver through the real callback, halt on `CallbackStop`,
   trip a `BaseException` wire on re-entrant teardown. Making that inheritance
   possible is the entire reason F4.5 existed, and it is now a guardrail.
3. **Also carry into F5's spec:** a per-module `assert 'callback' in <test
   file>` line in its Verification section — the narrow enforcement the
   guardrail names as its complement.
4. F5's spec will need a fresh Mode line and a fresh box-2 approval from you;
   F4.5's Mode 3 does not reach past the feature.

## Where the rest lives

- Per-task evidence and the resolved handoff doubts → the three verdict files.
- What was deliberately NOT fixed (calibration findings 3 and 4, both
  `voiceprint.py` surface, filed for F9) →
  `.out-of-scope/2026-07-26-calibration-findings.md`.
- The dependency decision and its rejected alternatives → `memory/decisions.md`.

## Commits

`727fbbc` (base) → `da7b8f9` `0ae0fd3` `b48f546` `8f86fc7` (Task 1) →
`0106418` `f2a1013` `fc7f5c8` `f12dd19` (Task 2) → `a130ac5` `8267878`
`99573c9` `ca6004e` (Task 3 build + escalation) → the wrap-up commit awaiting
your approval.
Curate check: **22** verdict `.json` files vs `project.md`'s "verdicts then: 19"
→ 3 since the last curate; **not due** (threshold 10).
Remote: **none** — local history only, nothing pushed.

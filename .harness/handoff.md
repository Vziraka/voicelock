# Handoff — F5 Task 5 rebuilt after REJECT #1, now `REVIEW`

Session of 2026-07-26. Tasks 1–4 `DONE`. Task 5 was **rejected once** on review,
both findings are fixed, and it is back at `REVIEW` with `rejects: 1`.
Tasks 6–7 `TODO`.

## The REJECT, and what changed

Gate passed 6/6 both times; the REJECT was on review, and both findings were
correct. No part of the verdict was re-litigated.

**Finding 1 — `_loop`'s falsy-read branch was untested dead surface.** The first
earned guardrail, which `spec.md` §4 binds this feature to verbatim. It also had
a real consequence: `break` left `status == RUNNING` with the camera still held,
so a transient read failure killed the preview silently and a restart would have
orphaned the device.

Now:

```python
self._fail("Camera stopped delivering frames")
return
```

The status becomes ERROR, `stop()` releases the device and refuses to erase the
error, and the next `start()` opens a fresh camera. **`start()` now calls
`stop()` first**, so a camera that died mid-loop can never be orphaned by a
restart — that is the leak the old `break` would have caused.

**Finding 2 — the drop-don't-queue behaviour was not pinned at the loop level.**
The verifier proved it: replacing `wait(pacing_delay(...))` with a flat
`wait(FRAME_INTERVAL)` deleted the behaviour outright and all 23 tests still
passed. Right shape, empty substance.

Replaced with two tests that discriminate in **opposite** directions:

- an **overrun** frame must cost **zero** extra delay — a flat-interval loop
  would need ≥ 5 × 33 ms and fails;
- an **under-budget** frame must actually be paced — a no-wait loop finishes
  instantly and fails.

Neither passes unless `_loop` consults `pacing_delay`, so the injected `clock`
is finally used for its purpose.

## Verified by mutation, not by assertion alone

Because the whole finding was that passing tests can be hollow, I broke the
implementation three ways and confirmed each test catches it. Source restored
byte-identical afterwards.

| Mutation | Result |
|---|---|
| flat `wait(FRAME_INTERVAL)` — deletes drop-don't-queue | **CAUGHT** |
| `wait(0)` — deletes pacing entirely | **CAUGHT** |
| `break` — the original rejected behaviour | **CAUGHT** |

`3/3 mutations caught`.

## Changed

- **`src/voicelock/facedetect.py`** — the falsy-read path now fails loudly;
  `start()` cleans up before acquiring.
- **`tests/test_facedetect.py`** — **26** tests: the two discriminating pacing
  tests, the mid-loop camera-death test, and the restart-releases-the-dead-camera
  test replace the tautological one.
- **`.harness/plan.md`** — Task 5 `REVIEW → TODO (rejects: 1) → DOING → REVIEW`,
  with the full REJECT feedback recorded on the task.

Suite: **114 passed** in 35.68 s. Throughput floor re-measured: **8.7 ms/frame**
against the 33 ms budget, so **`TARGET_FPS` stays at 30** and the fallback ladder
is still not needed. That measures the engine only — the `evaluate_js` bridge
half is Task 7's live check.

## Disclosure — exactly which Gate commands I ran (measurement exception)

`ruff` → 0; `pytest tests/test_facedetect.py -q` → 26 passed; `pytest` → 114
passed; the throughput floor → 0 at 8.7 ms/frame; plus the mutation run above,
which is failure evidence for the retry rather than a Gate command.

## Doubts, flagged rather than buried

1. **The two pacing tests are wall-clock timing tests.** Margins are wide (~25 ms
   observed against a 99 ms bound; ~100 ms observed against a 66 ms bound), but
   they are the one place in this suite where a heavily loaded machine could
   cause a flake. I judged a discriminating timing test better than a
   non-discriminating logical one — that was the whole finding — but a verifier
   may want the margins wider still.
2. **`test_a_camera_that_stops_delivering_mid_loop_surfaces_an_error` depends on
   `acquire_camera` consuming exactly one probe frame** (it supplies two frames
   and expects one delivered). If the probe read is ever removed, this test
   changes meaning rather than failing loudly.
3. **The mid-loop failure leaves the camera held until `stop()`.** That is
   deliberate — releasing from inside the worker would race `stop()`'s
   join-then-release ordering — but it means the device stays open between the
   failure and whatever calls `stop()`. Task 7 owns that call.
4. Carried from before, unchanged: `_wait_for` polls with a deadline;
   `JOIN_TIMEOUT = 5.0` was chosen rather than measured; tests read
   `engine._thread`.
5. **For Task 7, from the verifier:** if `stop()`'s join times out, `release()`
   runs anyway while the worker may still be mid-read — a 5 s window that only
   opens if a frame hangs.

## Carried forward into Tasks 6–7

- **Task 6 is UI-only**: an `<img>` in `.face-wrap`, `setFaceFrame` /
  `setFaceIdle` on `window.voicelockBooth`, **no camera state in JS**, **no
  `getUserMedia`**, **no CSS `scaleX(-1)`**. Gate is pytest with zero JS tests,
  so its criteria pin presence and export; the real proof is Task 7's live check.
- **Task 7** wires `BoothApi` (`start_record` starts the camera, `stop_record`
  stops it), must keep **audio recording working when the camera fails**, and
  adds the window-close handler `main()` currently lacks. `ready()` stays
  untouched — no startup probe.
- **Task 7 is LAST**: its done-criterion is the FULL `spec.md` Verification list
  and it will return `ESCALATE_HUMAN` on the manual demo. Do **not** mark it
  `DONE` until the human attests the live check.

## Also open

- **A guardrail UPDATE is parked** (Task 3's `learn` scan): check an asset's own
  embedded metadata (EXIF/XMP) first, as an update to the existing `[Approval]`
  rule. **Not written.** Blocks nothing.
- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*).

## next_action

**Re-verify Task 5** — clean-context verifier via `formats/VERIFIER-PROMPT.md`,
verbatim, spawned by this session. `rejects: 1`, below the 3-cap.

## Commits

- Tasks 1–4: `878186c`…`fab7a30`
- Task 5: `80a95ca` → `0eeac3f` (first build) → `571cfb8` (REJECT recorded) →
  `f069fa0` (DOING, retry) → **`11d5a1d` (retry build)**
- Base for the Gate diff: **`f069fa0`** · head: **`11d5a1d`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

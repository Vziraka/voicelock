# Handoff — F5 Task 5 built, now `REVIEW`

Session of 2026-07-26. Tasks 1–4 `DONE`, every one APPROVE on the first pass
with `rejects: 0`. Task 5 — the camera lifecycle — is built and `REVIEW`.
Tasks 6–7 `TODO`.

## Changed

- **`src/voicelock/facedetect.py`** — the stateful half: `TARGET_FPS` /
  `FRAME_INTERVAL` / `JOIN_TIMEOUT`, `start()`, `stop()`, `_loop()`,
  `pacing_delay()`, and an injectable `clock`.
- **`tests/test_facedetect.py`** — 9 more tests (**23** total in the file).
- **`.harness/plan.md`** — Task 5 `TODO → DOING → REVIEW`, with the measured
  throughput recorded on the task.

Suite: **111 passed** in 35.54 s.

## THE MEASUREMENT — `TARGET_FPS` stays at 30

**Throughput floor: 8.1 ms/frame** against the 33 ms budget — about **123 fps**
engine-side, ~4× headroom. Detect + overlay + crop + flip + JPEG encode, 30
consecutive 640×480 frames, real vendored model, real fixture.

**The fallback ladder was not needed.** `TARGET_FPS` remains 30, on evidence
rather than aspiration. **This measures the engine only** — passing it means the
engine *can* feed 30 fps, not that 30 fps reaches the screen. The `evaluate_js`
bridge half is still unmeasured and is Task 7's live check.

## What it does

- **Its own daemon thread**, not `app.py`'s 50 ms pump — that loop serves audio
  levels and must not be made to wait on a JPEG encode.
- **`stop()` ordering is the point**: halt the loop → **join** the worker →
  *then* `release()`. A frame read after release is a bug.
- **`stop()` is idempotent and safe after a failed start** — a window-close
  handler (Task 7) cannot know what state it is in. It also **refuses to erase a
  camera ERROR**, so a failure stays visible.
- **`pacing_delay()` is the drop-don't-queue rule made testable**: an overrun
  yields **zero** delay, so the loop goes straight back to `read()` for the
  newest frame instead of buffering the ones it missed. A queueing pipeline does
  not merely run slow, it drifts.
- **The loop waits on the stop event rather than sleeping**, so Stop is felt
  immediately instead of after the remainder of the frame budget.
- **A successful open sets `RUNNING`**, which clears any `ERROR` left by an
  earlier failed start — this is the observation Task 4's verifier carried
  forward, and it bears directly on criterion (6).

## The release tripwire, and why it is shaped this way

`CameraUsedAfterRelease` is a **`BaseException` subclass**, exactly as F4.5's
`ReentrantTeardown`, so a blanket `except Exception` on a teardown path cannot
swallow it. It **also sets a flag**, because an exception raised inside a daemon
worker thread dies with that thread and would otherwise never reach an
assertion — the flag is what makes a leak visible from the test.

`test_read_after_release_trips_a_wire_a_blanket_handler_cannot_swallow` proves
both halves: the wire is armed, *and* `except Exception` misses it.

## Disclosure — exactly which Gate commands I ran (measurement exception)

`ruff` → 0; `pytest tests/test_facedetect.py -q` → 23 passed; `pytest` → 111
passed; the `TARGET_FPS`-is-named assertion → 0; the `release`/`read`
per-module tripwire assertion → 0; and **the throughput floor** → 0 at
8.1 ms/frame. The floor is a measurement whose result decides `TARGET_FPS`, so
it had to be run to know the task was done.

## Doubts, flagged rather than buried

1. **The threaded tests poll with a deadline** (`_wait_for`, 5 s) rather than
   synchronising on an event. It is the simplest shape that does not deadlock a
   suite, and every such test also asserts the tripwire flag, so a hang or a
   leak fails rather than passing quietly. A verifier may still consider polling
   a smell.
2. **`test_worker_paces_itself_with_the_injected_clock` asserts
   `read_count >= len(received)`**, not equality — the worker may be mid-read
   when `stop()` lands, so equality would be flaky. The claim it actually pins
   is "no frame is processed that was not read", which is the backlog property.
3. **`JOIN_TIMEOUT = 5.0` is a new constant** with one caller (`stop()`). It is
   exercised by every lifecycle test through that path, but it is a number I
   chose rather than measured; 5 s is generous against an 8 ms frame.
4. **`_loop` breaks out on a falsy `read()`** rather than setting ERROR. A
   camera unplugged mid-recording therefore ends the loop quietly and leaves
   `status` RUNNING until `stop()`. That is not covered by any §5 criterion, and
   Task 7 owns what the Booth shows; flagging it rather than inventing scope.
5. **The tests reach into `engine._thread`** to assert the worker was cleared.
   Private-attribute access in a test, deliberate: there is no public surface
   that proves the join happened.

## Carried forward into Task 6 (UI) and Task 7 (wiring)

- **Task 6 is UI-only** and independent of everything above: an `<img>` inside
  `.face-wrap`, `setFaceFrame` / `setFaceIdle` on `window.voicelockBooth`, no
  camera state in JS, **no `getUserMedia`**, **no CSS `scaleX(-1)`** (the flip
  belongs in Python, after the overlay). This repo's Gate is pytest with zero JS
  tests, so its criteria pin presence and export; the real proof is Task 7's
  live check.
- **Task 7** wires `BoothApi`: `start_record` starts the camera, `stop_record`
  stops it, **a camera failure must NOT prevent audio recording**, and
  `main()` gains a window-close handler pointing at `stop()` (it currently has
  none). `ready()` stays untouched — no startup camera probe.
- **Task 7 is the LAST task**: its done-criterion is the FULL `spec.md`
  Verification list, and it will return `ESCALATE_HUMAN` on the manual demo
  line. Do **not** mark it `DONE` until the human attests the live check.

## Also open

- **A guardrail UPDATE is parked** (from Task 3's `learn` scan): check an
  asset's own embedded metadata (EXIF/XMP) first, as an update to the existing
  `[Approval]` rule rather than a fourth guardrail. **Not written.** Blocks
  nothing.
- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*).

## next_action

**Verify Task 5** — clean-context verifier via `formats/VERIFIER-PROMPT.md`,
verbatim, spawned by this session (subagent path, human-authorized). Task 5's
done-criteria are its `plan.md` list; it is an intermediate task.

## Commits

- Tasks 1–4: `878186c`…`fab7a30` (all `DONE`, verdicts in `memory/verdicts/`)
- Task 5: `80a95ca` (DOING) → **`0eeac3f` (build)**
- Base for the Gate diff: **`80a95ca`** · head: **`0eeac3f`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

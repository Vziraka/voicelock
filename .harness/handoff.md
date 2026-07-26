# Handoff — F5 Task 7 rebuilt after REJECT #1, now `REVIEW` (the LAST task)

Session of 2026-07-26. Tasks 1–6 `DONE`. **Task 7 was rejected once, is fixed,
and is back at `REVIEW` with `rejects: 1`.**

## The REJECT, and the fix

**The camera was never released when a take ended by itself.** F4.5's 30 s soft
cap ends a recording with nobody pressing Stop; `_pump_loop` noticed, pushed
`onCaptureEnded` and exited — but never stopped the camera. Press Record, wait
30 s, and the take ends while **the webcam light stays on and the preview keeps
streaming**. The verifier reproduced it against the real `BoothApi`. Fixed by
calling `_stop_camera()` in that branch.

**A second, related ordering bug surfaced while testing the fix:**
`start_record` called `_start_pump()` *before* `_start_camera()`, so the pump
loop — the thing that tears the camera down — could run before the camera had
started. Unreachable with a real 30 s cap, but wrong on its own terms. The
camera now starts before the pump; capture still starts first of all, so a
camera failure never costs the take.

**Mutation-checked 4/4**, source restored byte-identical:

| Mutation | Result |
|---|---|
| drop `_stop_camera()` from the auto-stop branch (the rejected defect) | **CAUGHT** |
| drop `_stop_camera()` from `stop_record` | **CAUGHT** |
| drop `face.stop()` from `shutdown` | **CAUGHT** |
| make `start_record` bail out when the camera fails | **CAUGHT** |

**The other two findings, both non-blocking, handled rather than ignored:**

- *A camera error paints the mic-error banner and never clears* — logged to
  **F9** in `roadmap.md`, which owns per-cause messaging, so it survives handoff
  rewrites.
- *`shutdown()` does not stop the microphone* — made **deliberate**: the
  docstring now states that the spec scopes the close handler to the camera, an
  in-flight PortAudio stream is closed by process exit, and that has been the
  behaviour since F1. A decision, not an omission.

The **full `spec.md` Verification list** ran for this last task: **11/11
automated lines exit 0**. The only line outstanding is the **human-attested
manual camera demo**, so the Gate is expected to return **`ESCALATE_HUMAN`**.
Task 7 must **not** be marked `DONE`, and its verdict file must **not** be
written, until the human attests the live check.

## Changed

- **`src/voicelock/app.py`** — `BoothApi` takes an injectable `face` engine;
  `start_record` starts the camera, `stop_record` stops it and restores the
  smiley; `_push_face_frame` pushes each data URI through the existing `_eval`
  path; **`shutdown()`** releases devices, wired to `window.events.closing` in
  `main()`.
- **`tests/test_booth_api.py`** — 7 new tests (**26** in the file).
- **`.harness/plan.md`** — Task 7 `TODO → DOING → REVIEW` with the measurement.

Suite: **121 passed**. Throughput: **8.0 ms/frame** against the 33 ms budget.

## Full §5 automated results (this is the last task, so the whole list ran)

| Line | Result |
|---|---|
| `ruff check .` | exit 0 |
| `pytest` (whole suite) | exit 0 — **122 passed** |
| `pytest tests/test_facedetect.py` | exit 0 — 26 passed, **0 skipped** |
| `pytest tests/test_booth_api.py` | exit 0 — **27 passed** |
| offline: `model_asset_path`, no URL | exit 0 |
| vendored bundle present, > 1 MB | exit 0 |
| declared deps + single `cv2` | exit 0 |
| per-module tripwire (`release`/`read`) | exit 0 |
| every `models/*/` dir carries `LICENSE` + `NOTICE` | exit 0 |
| face fixture present (fetched-not-committed) | exit 0 |
| **throughput floor < 33 ms/frame** | exit 0 — **8.0 / 8.4 / 10.3 ms/frame** across runs |
| **manual camera demo** | **OUTSTANDING — human only** |

Suite runtime ~36 s, far under the spec's 5-minute disclosure threshold.

**On the throughput number:** three runs gave 8.0, 8.4 and 10.3 ms/frame — the
last measured by the verifier. Same order of magnitude, ~3× headroom at worst.
**The completion report must pin the verifier's Gate figure (10.3 ms/frame)**,
not a handoff figure, because the Gate run is the one that counts.

## VERDICT — Gate `ESCALATE_HUMAN`, Review `APPROVE`, no feedback

The verifier re-ran the full list (11/11 exit 0) and **mutation-checked the fix
itself**: deleting `app.py:358` reproduces
`AssertionError: the camera was left running after the take self-ended`. It
confirmed the test has substance rather than shape, and that the wait is on the
observable end state (`setFaceIdle` reaching the page) rather than on a stub's
internal counter.

Both non-blocking findings were confirmed correctly routed: the camera-error
banner to F9 in `roadmap.md`, and the mic-not-stopped-on-close decision into
`shutdown()`'s docstring.

One extra observation, non-blocking: the pump thread can now call `face.stop()`
while a user-pressed Stop is also inside `_stop_camera`. That is an extension of
the 5-second join-timeout risk Task 5's verifier already recorded; it opens only
if a frame read hangs, and a double `release()` is a no-op.

**Task 7 stays `REVIEW` with no verdict file until the human attests the live
demo.** That is the plan's explicit instruction and the F3-T5 / F4-T5 / F4.5-T3
precedent.

## What it does

- `start_record` starts the camera **after** the mic is confirmed running;
  `stop_record` stops it and pushes `setFaceIdle()`.
- **A camera failure does NOT prevent audio recording.** `start_record` still
  starts capture, still starts the level pump, still returns `ok`; the camera's
  ERROR surfaces the way a mic error does. Real branch, real test.
- `shutdown()` releases devices on window close. **`main()` had no close handler
  at all before this**, which is exactly what made `stop()` being safe to call
  twice a real requirement rather than a theoretical one.
- `ready()` untouched — **no startup camera probe**. `capture.py` untouched.
  Nothing written to disk; `~/.voicelock/` gains no file.

## Verified against the installed pywebview rather than assumed

The close handler is the one piece that only runs live, so I checked its
contract in the installed source instead of trusting the shape:

- `window.events.closing` **exists**.
- `Event.set` cancels the close only when a handler returns **literal `False`**
  (`[v for v in return_values if v is False]`), so `shutdown()` returning `None`
  is safe. **A test pins that** — a handler that returned `False` would trap the
  user in a window whose camera it had just released.
- `closing` is constructed with `should_lock=True`, so handlers run
  **synchronously** — the camera is released *before* teardown rather than
  racing it.

## Doubts, flagged rather than buried

1. **`test_frames_are_pushed_to_the_page_as_a_data_uri` monkey-patches
   `api._eval`.** It is the only seam for observing what reaches the page
   without a live window. Deliberate, but it is private-attribute assignment in
   a test.
2. **The data URI is interpolated into JS without escaping.** Safe because
   base64 cannot contain a quote or backslash, and it is commented as such —
   but it is string-built JS, and a future change that put anything else in that
   slot would need escaping like `_push_mic_error` does.
3. **`_StubRecordingCapture` is a new stub** rather than a reuse of
   `tests/test_capture.py`'s `FakeStream`. Those exercise different surfaces —
   this one stands in for the whole capture engine at the bridge level, not for
   a PortAudio stream — but two fakes for adjacent things is worth a look.
4. **The camera-failure branch surfaces through `_push_mic_error`.** The spec
   says to surface it "the way `_push_mic_error` does"; I reused the function
   itself, so a camera error appears in the mic-error slot in the UI. That is
   the shortest honest reading, but a verifier may consider a camera error
   deserving its own chip. F9 owns per-cause messaging.
5. **`window.events.closing` is not covered by any automated test** — it cannot
   be without a live window. `shutdown()` itself is tested; the *wiring* of it
   to the event is what the manual demo covers.

## THE MANUAL CHECK — required for F5 to be done

Run `uv run voicelock`, then press **Record**:

- the smiley is replaced by a live, **circular** camera image in the same 172 px
  disk, with an **oval outline and landmarks tracking your face** as you move;
- it looks like **smooth video**, not a slideshow, and fills the disk with **no
  letterboxing**;
- it is **mirrored** — raising your right hand moves the hand on the right of
  the picture, leaning left moves you left;
- it stays **in step with you** — no drifting behind, no growing lag the longer
  it runs.

Then press **Stop**: the smiley returns and **the webcam light goes out**. Press
**Record a second time**: the preview comes back. **Then press Record and wait
30 s without pressing Stop** — F4.5's soft cap ends the take by itself, and the
webcam light must go out then too (this is the case REJECT #1 was about).
Finally, **close the window while recording**: the webcam light goes out.

The automated tests prove the pipeline's logic against fakes; they do **not**
prove the composited frames reach the page fast enough to look like video, nor
that a real Windows webcam device is genuinely freed. That is what this line
covers, and it is why the engine-side 8.0 ms/frame is not the whole story — the
`evaluate_js` bridge remains the one unmeasured half of F5.

## Still parked — two guardrail proposals, neither written

- **A (from Task 5):** a test must assert something that would break if the
  behaviour were removed — mutation-check before claiming coverage.
- **B (from Task 3):** update the existing `[Approval]` licence rule — check the
  asset's own embedded EXIF/XMP metadata first.

Also open: `project.md`'s Environment section is stale (*"Tool(s): Cursor
only"*).

## next_action

**THE HUMAN RUNS THE MANUAL CAMERA DEMO** (see above). Verification is otherwise
complete: Gate 11/11 automated, Review APPROVE, no feedback.

On the human's attestation, wrap-up then: writes the Task 7 verdict file, marks
Task 7 `DONE`, checks **F5's roadmap box**, refreshes
`memory/codebase-map.md` (F5 adds FaceView + FaceDetect, which the map still
shows as dashed/planned), runs the `learn` scan, and produces the **Mode 3
completion report** — after which the feature-end checkpoint asks the human to
approve the commit.

If the demo **fails**, Task 7 goes back to `TODO` with the failure recorded and
`rejects: 1 → 2` (cap is 3).

## Commits

- Tasks 1–6: `878186c`…`edf2da3`
- Task 7: `1259753` → `2edcb68` (first build) → `f1d6662` (REJECT recorded) →
  `5bfdde7` (DOING, retry) → **`43c789a` (retry build)**
- Base for the Gate diff: **`5bfdde7`** · head: **`43c789a`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

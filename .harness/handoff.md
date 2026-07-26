# Handoff — F5 Task 7 built, now `REVIEW` (the LAST task)

Session of 2026-07-26. Tasks 1–6 `DONE`. **Task 7 — the wiring that makes the
demo real — is built and `REVIEW`.**

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
| `pytest` (whole suite) | exit 0 — **121 passed in 36.21 s** |
| `pytest tests/test_facedetect.py` | exit 0 — 26 passed |
| `pytest tests/test_booth_api.py` | exit 0 — 26 passed |
| offline: `model_asset_path`, no URL | exit 0 |
| vendored bundle present, > 1 MB | exit 0 |
| declared deps + single `cv2` | exit 0 |
| per-module tripwire (`release`/`read`) | exit 0 |
| every `models/*/` dir carries `LICENSE` + `NOTICE` | exit 0 |
| face fixture present (fetched-not-committed) | exit 0 |
| **throughput floor < 33 ms/frame** | exit 0 — **8.0 ms/frame** |
| **manual camera demo** | **OUTSTANDING — human only** |

Suite runtime 36.21 s, well under the spec's 5-minute disclosure threshold.

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
**Record a second time**: the preview comes back. Finally, **close the window
while recording**: the webcam light goes out.

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

**Verify Task 7** — clean-context verifier via `formats/VERIFIER-PROMPT.md`,
verbatim. As F5's **last** task its list is the FULL `spec.md` Verification
section, and it should return **`ESCALATE_HUMAN`** on the manual demo line.
After that, the human runs the live check; only then does wrap-up write the
verdict, mark Task 7 `DONE`, check F5's roadmap box, refresh the codebase map,
and produce the Mode 3 completion report.

## Commits

- Tasks 1–6: `878186c`…`edf2da3`
- Task 7: `1259753` (DOING) → **`2edcb68` (build)**
- Base for the Gate diff: **`1259753`** · head: **`2edcb68`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

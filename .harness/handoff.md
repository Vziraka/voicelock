# Handoff — F5 Task 4 `DONE`; Task 5 (camera lifecycle) is next

Session of 2026-07-26. Tasks 1-4 are all `DONE`, every one APPROVE on the
first pass with `rejects: 0`. Task 4 - `facedetect.py`, F5's first engine
code - closed with Gate 5/5 exit 0 and Review APPROVE on both axes; verdict
`memory/verdicts/2026-07-26-F5-T4.json`. Tasks 5-7 `TODO`.

## Changed

- **`src/voicelock/facedetect.py`** (new) — the engine's pure half.
- **`tests/test_facedetect.py`** (new) — 14 tests, no real webcam.
- **`.harness/plan.md`** — Task 4 `TODO → DOING → REVIEW → DONE`.

Suite: **102 passed** (88 existing + 14 new) in 35.90 s.

## What it does

`process_frame()` runs the pipeline `spec.md` §4 fixes, in that exact order:
detect on the **full** 640×480 frame → draw ellipse + landmark subset →
centre-crop to a square → downscale to 172 px → `cv2.flip(img, 1)` → JPEG →
base64 data URI. **The flip is last, after the overlay**, so the oval and points
flip *with* the pixels and no landmark coordinate is ever flipped.

`acquire_camera()` handles both failure shapes `cv2.VideoCapture` actually
produces — `isOpened()` False, and `read()` returning `(False, None)` — because
treating a falsy `read()` as "no frame yet" would spin forever. Failures set
`FaceStatus.ERROR` with a human-readable message, mirroring `_mic_error_message`.

`VIDEO` running mode with an engine-owned monotonic timestamp counter.

## Two findings worth a verifier's attention

1. **`mediapipe` 0.10.35 ships ONLY the `tasks` package.** There is no
   `mediapipe.solutions` in this build — `import mediapipe.solutions` raises
   `ImportError`, and `pkgutil` lists exactly one submodule, `tasks`. The usual
   `FACEMESH_LIPS` / `FACEMESH_FACE_OVAL` constants therefore **do not exist**
   here. The module uses the Tasks API equivalent,
   `mediapipe.tasks.python.vision.face_landmarker.FaceLandmarksConnections`,
   which exposes 11 groups. **Landmark index groups come from the vendor's own
   constants, not hand-copied numbers**, so the drawn subset cannot silently
   drift from the model's topology.
2. **Overlay stroke weights are sized for the downscale, not the capture
   frame.** The overlay is drawn on 640×480 and then shrunk ~2.8× into the
   172 px disk, so `ELLIPSE_THICKNESS = 5` / `POINT_RADIUS = 3` render as ~2 px.
   A 1 px stroke would average away to nothing before reaching the page. This is
   a real consequence of the spec's fixed draw-then-crop order, and is commented
   in the source.

## Deliberately NOT in this diff

- **`TARGET_FPS` / `FRAME_INTERVAL`** — Task 5's, per the plan. A named constant
  introduced here would have no caller and no test, which is exactly the first
  earned guardrail's failure mode.
- **`start()` / `stop()` / the worker thread / the release tripwire** — Task 5.
- **The `release()`-after-`read()` tripwire on the fake camera** — Task 5, where
  teardown exists. The fake records `release()` (used by the two failure tests)
  but does not yet raise on use-after-release.
- **Any `app.py` change, and any startup camera probe** — Task 7; `ready()` is
  untouched by design (`spec.md` §3).

## Evidence a verifier should re-check rather than take

- **The real-model tests genuinely run and genuinely assert.** `pytest -v -k
  "vendored or reference"` → 2 passed, not skipped. Measured deviation against
  MediaPipe's committed vendor reference, **in VIDEO mode**: `0.005645` — the
  same as the IMAGE-mode figure Task 3 recorded, so the pipeline's mode change
  did not move the landmarks. Test tolerance is `0.02` (~3.5× headroom).
- **`FrameResult.landmarks` carries all 478 though only a subset is drawn.**
  This is required by `spec.md` §4 (later face features consume these points)
  and is pinned by `test_engine_returns_all_478_landmarks_though_only_a_subset_is_drawn`.
  **It is not unexercised surface** — please read it against the first earned
  guardrail before flagging it.
- **The geometry test is a real check, not a smoke test.** It places the face
  left of centre and asserts the overlay centroid lands right of centre at the
  predicted pixel, deriving the expectation from the crop offset (80 px) and
  scale (172/480). A normalized-vs-pixel bug, a crop-offset bug, or a missing
  mirror each break it.
- **The mirror test uses the module's own helpers** to build the *unflipped*
  composite, so only the flip is under test rather than the pipeline being
  re-implemented in the test.

## Disclosure — exactly which Gate commands I ran (measurement exception)

`uv run ruff check .` → exit 0; `uv run pytest tests/test_facedetect.py -q` →
14 passed; `uv run pytest` → 102 passed; and the `model_asset_path` / no-URL
source assertion → exit 0. The vendor-reference deviation was measured because
the test's tolerance had to be chosen from evidence rather than guessed.

## Doubts, flagged rather than buried

1. **The tests import two private helpers** (`_centre_crop_square`,
   `_draw_overlay`) to build the expected unflipped composite. The alternative
   was re-implementing the crop and draw in the test, which would let the test
   and the module drift apart silently. I judged importing the real helpers the
   honest choice; a verifier may disagree.
2. **`acquire_camera()` has no production caller yet** — Task 5's `start()` will
   call it. It is exercised by four tests and required by `spec.md` §5's
   criterion (7), which the plan explicitly assigns to Task 4 ("camera-open
   failure is handled here too, because it is pure-ish and cheap to test").
   Flagging it because "no production caller" is a guardrail trigger shape.
3. **The JPEG encode flag is deliberately ignored.** `cv2.imencode` raises
   `cv2.error` on a genuinely bad image rather than returning `False` for a valid
   3-channel `uint8` frame, so checking it would add a branch no test could
   reach — the guardrail forbids exactly that. Commented in the source.
4. **`_fail()` returns `None` and is typed `-> None`** while being used in
   `return self._fail(...)` position. Intentional and readable, but it is the
   kind of thing a reviewer may want as two statements.

## Carried forward into Task 5

- **F4.5's fake-stream shape**, translated: `read()` is the real path the fake
  must deliver through, `release()` the teardown it must trip on — with a
  **`BaseException`** subclass, since F4.5 proved a plain `Exception` is
  swallowed by blanket handlers. `tests/test_capture.py`'s `ReentrantTeardown`
  is the precedent to copy.
- **`stop()` ordering is the whole point**: loop stops → thread joined → *then*
  `release()`. A frame read after release is a bug the fake must trip on.
- **Drop frames, never queue them** — a queueing pipeline drifts, which reads as
  a freeze rather than a low frame rate.
- **The throughput floor lands in Task 5** and is set **at** the 30 fps target
  (<33 ms/frame). If it fails, the answer is `spec.md` §4's ladder — lower
  `TARGET_FPS` to 20, then 15, **on measured evidence** — never loosening the
  assertion, and never reopening the rejected loopback-MJPEG transport.

## Also open

- **A guardrail UPDATE is parked** (from Task 3's `learn` scan): check an
  asset's own embedded metadata (EXIF/XMP) first. Proposed as an update to the
  existing `[Approval]` rule, not a fourth guardrail. **Not written.** Does not
  block anything.
- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*).

## next_action

**`/implement` F5 Task 5 — camera lifecycle: 30 fps worker,
drop-don't-queue, release tripwire, throughput floor.** `Mode: Mode 3` is the
standing "go" and Task 4's wrap-up completed, so no further human "go" is
needed. **Carry in the verifier's status-reset observation** — it is recorded
in Task 5's notes in `plan.md`.

## Commits

- Tasks 1–3: `878186c`…`65f6d33` (see git log; all three `DONE` with verdicts)
- Task 4: `5418499` (DOING) → **`f610e04` (build)**
- Base for the Gate diff: **`5418499`** · head: **`f610e04`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

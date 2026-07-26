# Handoff — F5 Tasks 1–3 `DONE`; Task 4 (`facedetect.py`) is next

Session of 2026-07-26. All three asset/manifest tasks are `DONE`, each APPROVE
on the first pass with `rejects: 0`. Both designed licence STOP points fired;
both are resolved. **Task 4 begins F5's engine code.**

One guardrail **update** is parked below and needs a yes/no. It does not block
Task 4.

## Where the feature stands

| Task | State | Note |
|---|---|---|
| 1 — declare deps | `DONE` | `mediapipe==0.10.35`, `opencv-contrib-python==4.13.0.92`; `numpy`/`torch` unmoved |
| 2 — vendor the bundle | `DONE` | Apache-2.0, LICENSE + NOTICE, hash-verified |
| 3 — face fixture | `DONE` | fetched-not-committed + committed vendor reference |
| 4 — `facedetect.py` per-frame composite | `TODO` | **next** |
| 5 — camera lifecycle | `TODO` | 30 fps worker, drop-don't-queue, release tripwire |
| 6 — Booth `<img>` | `TODO` | UI only |
| 7 — `BoothApi` wiring | `TODO` | LAST; full §5 + human-attested manual demo |

Verdicts: `memory/verdicts/2026-07-26-F5-T1.json`, `-F5-T2.json`, `-F5-T3.json`.

## What Task 3 settled, since Task 4 depends on it

- `tests/fixtures/face/portrait.jpg` — **present on this machine, ignored at
  `.gitignore:39`, never committed** (verified: not in any commit on any branch,
  and `git add -A` leaves it behind).
- `tests/fixtures/face/portrait_expected_face_landmarks.pbtxt` — **committed**,
  Apache-2.0, 478 `landmark { x: … y: … }` blocks, **no `z`** (so Task 4's
  comparison is 2-D).
- **Measured agreement between the vendored bundle and the vendor reference** —
  reproduced independently by the verifier:
  ```
  reference landmarks: 478   detected: 478
  max abs diff: 0.005645     mean: 0.001051   (normalized coords)
  ```
  **Task 4's tolerance must sit above `0.005645`, not at it.** Suggest `0.02`,
  which is ~4× headroom and still tight enough to catch a real regression.
- Task 4's real-model test must **`pytest.skip` with an explicit reason naming
  the README** when the fixture is absent — never fail silently, never fabricate
  landmarks. `spec.md` §5's pinned presence check is what stops a skipping test
  turning the Gate green.

## PENDING — a guardrail UPDATE needing your yes/no

The `learn` scan found a lesson that clears the bar, but it **overlaps heavily**
with the `[Approval]` guardrail added by Task 2's scan. Per the `learn` skill's
overlap rule, it is proposed as an **update to that existing rule**, not a fourth
guardrail. **Nothing was written to `project.md`.**

> Append to the existing `[Approval]` per-asset licence rule:
> **Check the asset's own embedded metadata first (EXIF/XMP for images, bundle
> metadata for models) — it is the most authoritative statement available and
> the cheapest to read.**
>
> _Evidence to append:_ F5 Task 3 (2026-07-26). Eight external sources were
> consulted for the model bundle before the answer was found in Google's model
> cards. For the image fixture, the answer was **inside the file**: two lines of
> EXIF (`Artist`, `Copyright`) settled it immediately and decisively, where the
> hosting bucket, the docs and the Apache-2.0 `BUILD` file all said the wrong
> thing or nothing. Reading EXIF first would have reached the same verdict in
> one step.

Declining is a fine answer; I will record it as declined.

## Doubts carried from Task 3

1. **This inverts F3's committed-fixture precedent.** `.gitignore` carries
   `!tests/fixtures/voiceprint/*.wav` with the comment "Gate needs them on a
   clean checkout". `portrait.jpg` is the first asset this Gate needs but the
   repo cannot ship, so a fresh clone skips the real-model test until it is
   fetched. Documented in `tests/fixtures/face/README.md`.
2. **The licence position is unchanged** by the arrangement — it keeps the photo
   out of permanent history, which is a narrower claim than "it is licensed".
   Recorded as the human's decision in `memory/decisions.md`.
3. **Verifier's non-blocking observation:** `tests/fixtures/face/README.md:82`
   cites the vendor reference's source branch as `master` without a commit SHA,
   where `tests/fixtures/voiceprint/README.md` pins a rev. Not required by spec
   or plan, and the file is pinned three other ways (size, landmark count,
   reproducible agreement) — but a SHA would cost nothing if F6 revisits it.

## Carried forward into Task 4 — read before building

- **The module contract is pinned in `plan.md`'s Active context** —
  `FaceEngine` / `FrameResult` / `FaceStatus` / `TARGET_FPS`. Several later
  done-criteria name that surface, so it is fixed, not discovered.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit**, translated to a polling
  device: `cv2.VideoCapture` has no callback, so **`read()` is the real path**
  the fake must deliver through and **`release()` is the teardown** it must trip
  on — with a **`BaseException`** subclass, since F4.5 proved a plain
  `Exception` is swallowed by blanket handlers. `tests/test_capture.py`'s
  `ReentrantTeardown` is the working precedent to copy.
- **The pipeline order is fixed** (`spec.md` §4): `read()` → `detect_for_video`
  on the **full 640×480 frame** → draw ellipse + landmark subset →
  centre-crop to square → downscale to 172 px → `cv2.flip(img, 1)` →
  `imencode('.jpg')` → base64. **The flip is last, after the overlay** — no
  landmark coordinate is ever flipped.
- **`FrameResult.landmarks` carries all 478** though only a subset is drawn.
  This is required by `spec.md` §4 and pinned by a test, so it is **not**
  unexercised surface under the first earned guardrail — Task 4's notes say so
  explicitly, for the verifier's benefit.
- **`VIDEO` running mode, not `LIVE_STREAM`** — synchronous and deterministic;
  needs a monotonically increasing timestamp the engine owns.
- **No startup camera probe** — `ready()` in `app.py` is untouched. A deliberate
  divergence from `_probe_mic`, not an oversight.
- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback if 30 fps is
  unreachable: `TARGET_FPS` 30 → 20 → 15 **on measured evidence**, never by
  loosening the assertion, and never by reopening the rejected loopback-MJPEG
  transport without a fresh human decision.

## Also open

- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*,
  *"Setup run: 2026-07-21"*). Re-running `setup` refreshes it. Cosmetic.

## next_action

**`/implement` F5 Task 4 — "`facedetect.py`: the per-frame composite path, on
injectable fakes".** `Mode: Mode 3` is the standing "go" and Task 3's wrap-up
completed, so no further human "go" is needed. No escalation is expected in
Tasks 4–7; the next required human touchpoint is Task 7's manual camera demo.

## Commits

- Task 1: `878186c` → `19b63e5` → `79b022e` → `b21b8ae`
- Task 2: `be938c1` → `e533720` → `6585761` → `1ddf831` → `bded558` → `8aa1e62`
- Amendments: `5522bd3` (1) · `2876e6f` (2, revised)
- Task 3: `c230109` → `b926819` → `0fbadeb` → `d7465da` → `5b7670f` →
  `fe35882` → this wrap-up commit
- Task 3's Gate diff was `d7465da..5b7670f`

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

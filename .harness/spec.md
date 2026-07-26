# Spec: F5 — Camera booth

Feature: Feature 5 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [ ] Approved by human

- **Mode:** Mode 3 (Spec-to-done). Set by the human 2026-07-26. The two
  dependencies this feature introduces were locked by a TECH-PICK + human
  approval BEFORE drafting (`memory/decisions.md`, 2026-07-26), and the two
  architecture forks — who owns the camera, and where the preview lives — were
  put to the human and answered before the Constraints section was written. Mode
  3's autonomy is therefore bounded to an already-approved design.
  F4.5's Mode 3 does not reach past its own feature; this line is F5's own.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Give the Booth an eye. A live webcam preview appears **inside the Booth's
existing 172 px face disk** — the decorative smiley at
`src/voicelock/ui/index.html:590-600` — while a recording is running, with an
oval outline around the detected face and facial landmarks drawn on it, tracking
in real time. On Stop the smiley returns and the camera is released.

The preview is **circular**, because the slot it takes over is:
`.face-wrap` is 172×172 and `.face-disk` carries `border-radius: 50%`. The
webcam's 4:3 frame is therefore **centre-cropped to a square** and masked to the
circle — the left and right edges of the camera's field of view are not shown.
Detection still runs on the **full** frame, so a face near the edge is found even
when the crop hides it. It is also **mirrored**, like every video-call self-view,
because an unmirrored preview makes people move the wrong way when centring
themselves — and centring your face is the interaction this feature exists to
support.

This is the visual analog of F1: F1 proved the microphone reaches the Booth and
the Visualizer reacts; F5 proves the camera does the same. It is the prefactor
for every face feature that follows — F6 (faceprint on screen), F7 (face as the
inner lock) and F8 (lip-sync liveness) all consume the frames and landmarks this
feature establishes.

Three things must be true when this is done:

1. **The camera reaches the Booth.** Pressing Record opens the webcam, and the
   face disk shows a live image instead of the smiley SVG. Pressing Stop reverts
   the disk to the smiley and **releases the camera** — the webcam light goes
   out and a second Record works.
2. **The face is found and drawn.** Each delivered frame is run through the
   vendored MediaPipe Face Landmarker; an **oval** outline around the detected
   face and a landmark overlay — deliberately including the **lip contour** —
   are composited onto the frame in Python before it reaches the page. An
   ellipse rather than the conventional rectangle because the preview is a
   circle: a rectangle's corners clip against the mask when a face nears the
   edge (human's call, 2026-07-26). When no face is in view, the preview stays
   live and the overlay simply is not drawn.
3. **It stays offline.** The `.task` model bundle is vendored into the repo and
   loaded from a local path, exactly as F3 vendored ECAPA. No runtime network
   call, on any path.

Demo: press Record → your face appears in the round disk → an oval and landmarks
track it as you move → press Stop → the smiley comes back and the camera light
goes out.

## 2. Grilling record — ambiguity scan

**Status: CLEAR** — every category resolved; zero clarification markers remain
(2026-07-26).

| Category                           | Verdict | Resolved by |
| ---------------------------------- | ------- | ----------- |
| Functional scope & behavior        | Clear   | Three items, listed in §1 and bounded in §3. Camera lifecycle is tied to the existing Record/Stop path — the human's answer, 2026-07-26 ("turn into a camera screen when recording happens"). |
| Domain & data model                | Clear   | No persisted state, no file format, no vault or crypto surface touched. Frames are transient; nothing is written to disk. Faceprints, distances and keys are F6/F7, not here. |
| Interaction & UX flow              | Clear   | The preview replaces the decorative smiley **in place**, in its existing 172 px circle, with **zero layout shift** — human's answer, 2026-07-26. The preview is therefore **round**: the 4:3 frame is centre-cropped to a square and masked, and the detected face is outlined with an **ellipse**, not a rectangle whose corners would clip (human's answer, 2026-07-26). It is **mirrored** (selfie view), flipped after drawing so no coordinate is flipped. Expanding to a larger rectangle was explicitly kept open as a later change and is a §3 non-goal here. |
| Non-functional (perf, security)    | Clear   | Offline-only preserved by vendoring (§4); no crypto surface. Target **30 fps** (human's call, 2026-07-26), with a Gate floor set **at** the target (<33 ms/frame engine-only) and an evidence-driven fallback ladder if the hardware cannot meet it; frames are dropped, never queued. The bridge half is covered by the required live check. |
| Integration & dependencies         | Clear   | Two dependencies, `mediapipe` and `opencv-contrib-python`, chosen by a TECH-PICK run and human-approved 2026-07-26 (`memory/decisions.md`; research in `memory/research/2026-07-26-f5-face-stack.md`). InsightFace, facenet-pytorch and OpenCV-only were evaluated and ruled out on evidence. |
| Edge cases & failure modes         | Clear   | No camera / camera in use by another app; no face in frame; Stop while a frame is mid-flight; a second Record after Stop; camera released on window close (§4). |
| Completion signals                 | Clear   | §5 pinned: fake-camera tests through the real read path, a camera-release tripwire, an offline-load assertion, two declared-dependency assertions, a measured throughput floor, plus the required human-attested live check. |
| Terminology (matches `CONTEXT.md`) | Clear   | Uses **FaceView** and **Booth** as the glossary defines them. No new terms. **Faceprint** is deliberately NOT used — this feature computes no identity signal. |

**Mode 3 "if every gate passed but it were still wrong" (RESOLVED 2026-07-26):**
the fake-camera tests prove the *pipeline*, but a fake that always yields a frame
and always releases cleanly proves nothing about the two ways this feature can be
live-broken: the preview updating too slowly to be watchable, and the camera
never being released on Stop (light stays on, second Record fails). The second is
the **F4.5 defect class exactly** — a resource-teardown bug that fakes pass
happily. The human chose **both** mitigations (a required check, not accepted
risk): a human-attested live check **and** an automated release tripwire, plus a
Gate-measurable throughput floor. This follows the F1–F4.5 precedent, where every
feature made its live Booth check required.

## 3. Non-goals

- **No faceprint, no identity, no matching.** No embedding is computed, no
  distance is shown, no cutoff is calibrated. That is F6, and it will need its
  own model-vendoring decision (OpenCV's SFace — named in the TECH-PICK, not
  built here). A landmark is not an identity.
- **No lock, vault, crypto or key change.** The inner lock is F7. `vault.py`,
  `middlelock.py` and the v2 vault format are untouched, and F4's measured
  `CORRECTION_RADIUS = 110` and F3's `ACCEPT_CUTOFF = 0.45` must remain valid —
  which the TECH-PICK protected by proving the resolution leaves `numpy` at
  2.2.6 and `torch` at 2.13.0.
- **No liveness, challenge, or lip-sync.** That is F8. The lip contour is drawn
  in F5 **only** so it is visibly present and known-good before F8 depends on
  it; nothing measures it.
- **No video recording or storage.** Frames are transient. Nothing is written to
  disk, nothing is added to the vault, nothing is played back. `~/.voicelock/`
  gains no new file.
- **No expanded preview.** The 172 px circle is what F5 builds. Growing it into a
  440 px rectangle on Record is a real option the human deliberately deferred
  ("we can try 172px and we can expand if i want") — it is a later change, not
  scope hidden in this one.
- **No restyling of the overlay.** The oval and landmarks are drawn by OpenCV and
  will look like OpenCV, not like the Booth's CSS. Matching the Booth's visual
  language is F9 polish.
- **No change to audio capture.** `capture.py` is not touched. The camera is a
  sibling of the microphone, not a modification of it; F4.5's `sd.CallbackStop`
  fix and its tests stay exactly as they are.
- **No startup camera probe.** Unlike `_probe_mic`, the camera is not opened at
  `ready()` — see §4 for why.
- Out-of-scope discoveries during build (Mode 3 default): record in
  `.out-of-scope/`, never build.

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv (no bare pip);
  engine in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in `tests/`;
  **offline-only — no network at runtime**; snake_case; `tests/test_<module>.py`;
  Python owns state, JS renders only.
- Honor all three earned guardrails in `project.md`, each of which this feature
  is in direct range of:
  - *no unexercised helper, method, or branch* — every branch added here must
    have a caller and a test, including the no-face-in-frame branch;
  - *a test double for a stream or device must deliver through the real callback
    it was handed* — see "The test harness" below for how this reads against a
    **polling** device;
  - *the UI must not keep its own copy of state the engine owns* — the page
    holds no camera state; it renders what Python pushes and nothing else.

**The dependencies (RESOLVED 2026-07-26, human-approved TECH-PICK):**
`uv add mediapipe "opencv-contrib-python>=4.13,<5"` — both as **main**
dependencies.

- `mediapipe` — face detection + 478 landmarks. Liveness quoted: wheel
  `mediapipe-0.10.35-py3-none-win_amd64.whl` uploaded
  `2026-04-27T17:45:33.946332Z` (PyPI JSON), 2,515,402 downloads last month,
  Apache-2.0.
- `opencv-contrib-python` — camera frames via `cv2.VideoCapture`, plus the JPEG
  encode and the overlay drawing. Liveness quoted: 4.13.0.92 released
  2026-02-05, 8,487,096 downloads last month.
- **`opencv-contrib-python`, never `opencv-python`.** Both install a top-level
  `cv2` and installing both shadows. MediaPipe pulls the contrib build as a
  transitive, so declaring *that* one keeps a single `cv2` **and** closes the
  undeclared-transitive gap before it bites — the F4.5 `soundfile` lesson applied
  in advance rather than in arrears.
- **Pinned below OpenCV 5 on purpose.** 5.0.0.93 is real and live (2026-07-02)
  but three weeks old and a major-version bump; F5 uses nothing from it.
- Resolution proved before approval, not assumed: `uv pip compile
  --python-version 3.11` against the current eight dependencies plus these two
  resolves to `mediapipe==0.10.35`, `opencv-contrib-python==4.13.0.92`,
  `numpy==2.2.6`, `torch==2.13.0` — nothing moves. Nothing was installed;
  `git status --porcelain` was empty before and after.
- **No dependency beyond these two** — anything else needs a fresh TECH-PICK and
  human sign-off. In particular F6's SFace model is *named* in the decision but
  is **not** installed or vendored here.

**The model (RESOLVED 2026-07-26 — follows the F3 ECAPA precedent):**
the Face Landmarker `.task` bundle is **vendored into the repo** at
`src/voicelock/models/face_landmarker/`, beside `models/ecapa/`, and loaded via
`BaseOptions(model_asset_path=...)`. Canonical source, fetched **once at build
time** (not at runtime, ever):
`https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`

- The bundle's exact byte size and its own licence text are **unconfirmed** at
  spec time — the model page states neither. **Both must be checked at download,
  before the file is committed.** If the licence is not permissive, STOP and
  escalate; do not vendor it and do not substitute a different model silently.
- Running mode is **`VIDEO`** (`detect_for_video`), not `LIVE_STREAM`.
  `LIVE_STREAM` is asynchronous and would deliver through a `result_callback`,
  which reads closer to the earned guardrail's wording — but it makes frame
  ordering nondeterministic and can drop frames, which turns a Gate test into a
  flaky one. `VIDEO` is synchronous and deterministic. It requires
  **monotonically increasing timestamps**; the engine owns that counter.

**Who owns the camera (RESOLVED 2026-07-26 — a fact, not a preference):**
**Python.** `app.py:405` loads the Booth with `url=UI_PATH.as_uri()`, a `file://`
URL, and Microsoft's WebView2 documentation (page `updated_at` 2026-06-12) states
that secure-context APIs "are not available to documents loaded by file URLs.
This includes APIs such as `navigator.mediaDevices.getUserMedia()`". The
JS-owned-camera architecture therefore does not exist in this Booth without
rebuilding F1's window bootstrap onto virtual host name mapping. See
`memory/research/2026-07-26-f5-camera-preview-transport.md`.

**How frames reach the page (RESOLVED 2026-07-26, human-chosen):**
Python composites and pushes one image per frame.

    cv2.VideoCapture.read()  ->  MediaPipe detect_for_video  ->
    cv2 draws the oval + landmarks  ->  centre-crop to a square  ->
    cv2.flip(img, 1)  ->  cv2.imencode('.jpg')  ->  base64  ->
    evaluate_js("...setFaceFrame('data:image/jpeg;base64,...')")  ->  <img>

The page's only job is assigning that data URI to an `<img>` inside `.face-wrap`,
and swapping back to the smiley SVG on `setFaceIdle()`. Chosen over pushing raw
frames plus landmark coordinates for JS to draw, because this repo's Gate is
**pytest with zero JS tests** — compositing in Python is the only option whose
visible output the Gate can assert on, and it makes overlay-vs-frame drift
structurally impossible. A loopback MJPEG server was rejected: better throughput,
but it adds a listening socket to an app whose rule is "offline-only".

- Capture at **640×480** (landmark quality benefits from the larger frame).
  Detection runs on the **full** frame; the composited image is then
  **centre-cropped to a square** and downscaled to the **172 px** the disk shows,
  since the page masks it to a circle. Cropping after detection is deliberate: a
  face at the edge of the field of view is still found, it is simply not shown.
- **The preview is mirrored** (selfie view), because an unmirrored self-view makes
  people move the wrong way when centring themselves — and centring your face is
  the interaction this feature exists to support. Every video-call app mirrors
  self-view for the same reason.
  **The flip is the LAST step before encoding, applied after the overlay is
  drawn** — so the oval and landmarks are already painted into the pixels and
  flip with them. **No landmark coordinate is ever flipped**, which is what keeps
  this a one-line change instead of a source of mirror bugs. Detection runs on
  the unflipped frame, so the landmark *data* F6/F7/F8 consume is unmirrored and
  unaffected; only the display is mirrored.
  Consequence to honor: **any text drawn on the frame must be drawn after the
  flip**, or it renders backwards. F5 draws no text; this is written down so a
  later feature does not discover it the hard way.
- **The engine returns all 478 landmarks even though only a subset is drawn.**
  Drawing is a display concern — the face oval, eyes and lip contour, because 478
  dots on a 172 px disk is a blob. But the engine's returned structure carries the
  full set, so F6 and F8 do not have to reopen `facedetect.py` to reach the points
  they need. F5's stated purpose is being the prefactor those features build on;
  a display decision must not narrow the data contract. The full set is exercised
  by the fixture test below, so this is not untested surface under the earned
  guardrail.
- Target **30 fps** (human's call, 2026-07-26 — 15 read as too choppy), on its
  **own daemon thread** — not folded into `app.py`'s existing 50 ms `_pump_loop`,
  which serves audio levels and must not be made to wait on a JPEG encode. The
  rate is a **named module constant**, not a scattered literal, so the fallback
  below is a one-line change.
- **Drop frames, never queue them.** At 30 fps the per-frame budget is **33 ms**
  for detect + draw + crop + flip + encode + `evaluate_js`. If a frame overruns
  it, the next frame is **skipped**, not buffered. This matters more than the
  target number: a queueing pipeline does not merely run slow, it drifts —
  the preview falls seconds behind reality and keeps falling, which looks like a
  freeze rather than like a low frame rate. Always render the **latest** frame.
- **Honest fallback ladder if 30 is not reachable** (measured, never guessed):
  lower the constant to 20, then 15, recording the **measured** per-frame cost in
  the completion report. A target the hardware cannot meet must be lowered on
  evidence, not left aspirational while the preview stutters. Do **not** reach for
  the rejected loopback-MJPEG transport without a fresh human decision — that
  rejection is recorded with its reason in `memory/decisions.md`.
- The 172 px target is a material risk reduction, not only an aesthetic choice: a
  172 px JPEG is roughly 8 KB where a 440 px one is ~5× that, and `evaluate_js`
  throughput across pywebview's WebView2 bridge is the one thing in this feature
  that cannot be measured until it is built.

**The engine (`src/voicelock/facedetect.py`), shaped after `capture.py`:**
injectable `open_camera` (default `cv2.VideoCapture`) and an injectable
landmarker, so **no Gate test ever touches a real webcam** — the same contract
`CaptureEngine`'s `open_input` established in F1. A status enum with an ERROR
state and a human-readable message, mirroring `_mic_error_message`.

Edge cases this must hold under:
- **No camera, or the camera is held by another app.** `VideoCapture` does not
  raise — it returns an object whose `isOpened()` is False, and/or `read()`
  returns `(False, None)`. **Both** must be handled; treating a falsy `read()` as
  merely "no frame yet" would spin forever. Surface an ERROR status with a
  message ("No camera available" / "Camera permission denied"), push it to the
  page the way `_push_mic_error` does, and do not start the loop.
- **No face in the frame.** The preview stays live; the overlay is not drawn.
  This is a normal state, not an error — and it is a branch, so it needs a test.
- **Stop while a frame is mid-flight.** Releasing the device must not race the
  worker: the loop stops, is joined, and only then is `release()` called. A frame
  read after release is a bug, and the fake camera trips on it.
- **A second Record after Stop** must reopen the camera and work. This is the
  observable half of "the camera was actually released".
- **Window close** while recording must release the camera too — a stuck webcam
  light after the app exits is the same defect wearing a different hat.
- **No startup probe.** Unlike `_probe_mic`, the camera is *not* opened at
  `ready()`. Opening a webcam costs seconds on Windows, and paying that on every
  launch — including launches that never record — is a worse trade than learning
  about a missing camera when Record is pressed. This is a deliberate divergence
  from the audio path, recorded here so a verifier does not read it as an
  oversight.

**The test harness — how the callback guardrail reads for a polling device:**
the earned guardrail says a test double "must deliver data through the **real
callback it was handed**". `cv2.VideoCapture` has **no callback** — it is a
polling API (`read()`). The equivalent, and what this feature must do, is: the
fake camera delivers frames through the **real `read()` the engine calls**, and
those frames must flow through the engine's real frame-handling path into the
real composited output. A test that fabricates landmarks and skips the engine's
frame path is exactly the hole F4.5 was inserted to close, in a different shape.
The fake must additionally **raise immediately** if `read()` is called after
`release()` — the release tripwire the human required. As in F4.5, that tripwire
must raise a **`BaseException` subclass** if the engine's teardown path wraps
anything in a blanket `except Exception`, so it cannot be silently swallowed;
verify that deliberately rather than assuming.

**Fixture provenance (RESOLVED 2026-07-26):** at least one test runs the **real**
vendored model against a real face image, so the bundle is proven to *detect*
rather than merely to exist. The fixture is **MediaPipe's own canonical face test
image**, `portrait.jpg`, from the same project as the vendored bundle:
`https://storage.googleapis.com/mediapipe-assets/portrait.jpg`

This follows F3's precedent exactly — its voice fixtures were "derived offline
from the SpeechBrain `spkrec-ecapa-voxceleb` model repo's own example clips
(Apache-2.0), the same source as the vendored model"
(`tests/fixtures/voiceprint/README.md`). Same reasoning, same shape.

- **Bonus, and a reason to prefer it over any other image:** MediaPipe publishes
  its own **expected output** for this exact image —
  `portrait_expected_face_landmarks.pbtxt` and
  `portrait_expected_blendshapes.pbtxt` in `mediapipe/tasks/testdata/vision/`. The
  test can therefore assert landmarks match a **vendor reference**, not merely
  that "some landmarks appeared". Use it if the format is practical to parse; if
  it is not, say so in the fixture README rather than silently asserting less.
- Provenance and licence go in `tests/fixtures/face/README.md`, in the shape
  `tests/fixtures/voiceprint/README.md` already established. **The licence must be
  verified at download**, exactly as for the `.task` bundle; if it does not check
  out, STOP and escalate rather than substituting another image.
- **That check has teeth — "it comes from Google's MediaPipe project" is NOT
  sufficient evidence.** Verified 2026-07-26: MediaPipe's own face_detector
  sample notebook does not ship an Apache-2.0 asset at all — it downloads
  `https://i.imgur.com/Vu2Nqwb.jpeg`, credited in the notebook to **Pixabay**,
  whose licence restricts redistributing images unaltered. Committing a fixture
  into a repo *is* redistributing it unaltered. So the provenance of each
  individual asset must be established on its own terms, not inherited from the
  project that references it. `portrait.jpg`'s own licence is **`unconfirmed`** at
  spec time and is exactly what the download-time check exists to settle.
- **Explicitly NOT a photo of the repo's owner.** A biometrics project committing
  its owner's face as a permanent fixture is a poor default even with no remote,
  and a fixture must be stable — one that can be withdrawn later is a test that
  breaks later. The owner's face is proven **live**, in the required manual check
  below, never in git. This mirrors what already happens for voice: the repo holds
  two VoxCeleb strangers, and the owner's actual voice exists only at runtime in
  `~/.voicelock/`.
- If no licensed image can be obtained at all, the real-model test is **replaced
  by an explicitly written limitation in the Verification section**, never by a
  silent proxy that fabricates landmarks and calls it coverage.
- **Flagged inheritance for F6, not solved here:** F6 needs *two* faces — a
  same-person-close and a different-person-far probe — and `portrait.jpg` is one
  image. This is the same wall F3 hit (its model repo shipped one clip per
  speaker, which is why its same-speaker probe is a window of the same recording,
  disclosed as a caveat). A photo cannot be split that way, so **F6's spec must
  say where face B comes from**. Named here so it surfaces at spec time rather
  than mid-build.

- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
  `uv run pytest` → exit 0.

## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Harness rules find this
section by its NAME ("Verification"). Two parts, both required.

Runtime budget: `uv run pytest` already loads torch + the vendored ECAPA model
and pays Argon2id twice per middlelock unlock — F4.5's final Gate measured
**88 passed in 50.42 s**. MediaPipe's landmarker adds a model load, the
`portrait.jpg` detection test, and the 30-frame throughput probe below.
Whole-suite budget: **within the 10-minute default**; if the suite exceeds 5
minutes, say so in the completion report rather than quietly accepting it.

Standing (project regression net, from `project.md`), pinned:
- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed — the whole existing
  suite, including all F1–F4.5 tests, still green)

Feature-specific (proves THIS feature works), pinned:

- `uv run pytest tests/test_facedetect.py -q` → exit 0; final summary reports 0
  failed. Must cover, using only injectable fakes (**no real webcam**):
  (1) **frames flow through the real read path** — frames handed back by the
  fake camera's `read()` reach the engine's real frame-handling method and come
  out as a composited JPEG; no test fabricates landmarks and skips that path;
  (2) **the overlay is drawn from real landmark output** — with an injected
  landmarker returning known normalized coordinates, the oval and the landmark
  points land on the expected **pixel** coordinates, and the centre-crop maps
  them correctly into the square that is finally shown (this is where a mirror,
  a normalized-vs-pixel scaling bug, or a crop-offset bug would show);
  (3) **the lip contour is among the drawn points, and the engine returns all
  478** — F8 depends on both, so the drawn subset and the full returned set are
  pinned now, while it is cheap;
  (3b) **the preview is mirrored, and only the pixels are** — the composited
  output is the horizontal mirror of the unflipped composite, while the landmark
  coordinates the engine returns are **unflipped**. An asymmetric synthetic frame
  makes this unambiguous. This is the test that catches someone "fixing" the
  mirror by flipping coordinates instead of pixels;
  (4) **no face in frame is a normal state** — the preview still produces a
  frame, the overlay is absent, and no ERROR is raised;
  (5) **Stop releases the camera** — `release()` is called exactly once, the
  worker thread is joined first, and the fake **raises** if `read()` happens
  afterwards, so a leak fails **fast** instead of hanging the suite;
  (6) **a second start after stop works** — a fresh camera is opened and frames
  flow again;
  (7) **camera-open failure surfaces as ERROR** — both `isOpened()` False and
  `read()` returning `(False, None)` produce an ERROR status with a
  human-readable message, and no crash and no spin.

- **The real model detects a real face** — a test in `tests/test_facedetect.py`
  that runs the **vendored bundle** (no injected landmarker) against
  `tests/fixtures/face/portrait.jpg` and asserts a face is found with 478
  landmarks, and that a plain-colour image yields **no** face. This is the line
  that separates "the bundle is on disk" from "the bundle works". Where
  MediaPipe's published `portrait_expected_face_landmarks.pbtxt` is practical to
  parse, assert against that **vendor reference** rather than against a
  self-generated expectation; if it is not practical, say so in
  `tests/fixtures/face/README.md`.

- `uv run pytest tests/test_booth_api.py -q` → exit 0; final summary reports 0
  failed. Must additionally cover that `start_record` starts the camera and
  `stop_record` stops it, and that a camera failure does **not** prevent audio
  recording — the microphone path must survive a broken webcam.

- `uv run python -c "import inspect; from voicelock import facedetect; s = inspect.getsource(facedetect); assert 'model_asset_path' in s, 'model is not loaded from a local path'; assert 'http://' not in s and 'https://' not in s, 'facedetect.py references a URL'"`
  → exit 0. Pins the offline guarantee at the source level.

- `uv run python -c "import pathlib; p = pathlib.Path('src/voicelock/models/face_landmarker/face_landmarker.task'); assert p.is_file(), 'the model bundle is not vendored'; assert p.stat().st_size > 1_000_000, f'vendored bundle is implausibly small: {p.stat().st_size} bytes'"`
  → exit 0. Pins that the bundle is really in the repo, not a stub.

- `uv run python -c "import tomllib, pathlib; deps = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['dependencies']; low = [d.replace(' ', '').lower() for d in deps]; assert any(d.startswith('mediapipe') for d in low), 'mediapipe is not a declared dependency'; assert any(d.startswith('opencv-contrib-python') for d in low), 'opencv-contrib-python is not a declared dependency'; assert not any(d.startswith('opencv-python') for d in low), 'opencv-python is declared alongside the contrib build — two cv2 installs shadow each other'"`
  → exit 0. Pins both declarations **and** the single-`cv2` rule.

- `uv run python -c "import pathlib; t = pathlib.Path('tests/test_facedetect.py').read_text(encoding='utf-8'); assert 'release' in t, 'the camera tests never mention release'; assert 'read' in t, 'the camera tests never drive the real read path'"`
  → exit 0. The per-module analog of F4.5's `assert 'callback' in <test file>`
  tripwire, adapted honestly to a **polling** device: `cv2.VideoCapture` exposes
  no callback, so `read()` **is** the real path a fake must deliver through, and
  `release()` is the teardown a fake must trip on.

- **Throughput floor**, run against the **real** vendored model and the
  `portrait.jpg` fixture: `uv run python -c "..."` → exit 0, asserting that
  detect + overlay + crop + flip + JPEG encode for 30 consecutive 640×480 frames
  averages **under 33 ms per frame** — i.e. the engine alone sustains the 30 fps
  target before the bridge is involved. Pin the measured number in the completion
  report.
  The floor is deliberately set **at** the target, not below it: if the engine
  cannot hit 30 fps on its own, a 30 fps target is a fiction, and it is better to
  learn that from a red Gate than from a stuttering demo. If this line fails, the
  answer is §4's fallback ladder — lower the constant on the measured evidence
  and record the number — **not** loosening the assertion to match whatever the
  code happens to do.
  This measures the **engine**, not the `evaluate_js` bridge. The bridge half is
  what the live check below covers, and the split is stated here rather than
  blurred: passing this line means the engine can feed 30 fps, not that 30 fps
  reaches the screen.

Proof surface: the highest real surface this feature touches is the live
pywebview Booth driving a real webcam. The automated tests prove the pipeline's
logic against injectable fakes; they do **not** prove that the composited frames
reach the page fast enough to look like video, nor that a real Windows webcam
device is genuinely freed on release. Those gaps are covered by the required
manual line below (a required check, not accepted risk) — the human's explicit
answer to the Mode 3 blind-spot question.

- **Manual (required for F5 done, human-attested):** run `uv run voicelock` →
  press **Record**. The smiley is replaced by a live, **circular** camera image
  in the same 172 px disk, with an oval outline and landmarks **tracking your
  face as you move**, and the preview looks like smooth video rather than a
  slideshow. The image fills the disk with no letterboxing. It is **mirrored**:
  raising your right hand moves the hand on the right of the picture, and leaning
  left moves you left — the way a mirror behaves, not the way a stranger's camera
  does. The preview must also stay **in step with you** — no drifting behind, no
  growing lag the longer it runs (the frame-dropping requirement in §4). Press
  **Stop**: the
  smiley returns, **the webcam light goes out**, and pressing **Record a second
  time** brings the preview back. Close the window while recording: the webcam
  light goes out. Observable: the camera is genuinely opened, genuinely drawn on,
  and genuinely released.

Out-of-scope discoveries during build (Mode 3 default): record in
`.out-of-scope/`, never build.

---

*Spec-anchored: amendments follow the F2/F3/F4/F4.5 path — update this file,
re-scan changed sections, human re-checks box 2, re-plan.*

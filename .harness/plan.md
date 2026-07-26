# Plan — F5 — Camera booth

## Active context
- Updated: 2026-07-26
- Feature: Feature 5 from `roadmap.md` · Mode: Mode 3 · Phase: **BUILDING — Task 1
  `DONE` (verdict `memory/verdicts/2026-07-26-F5-T1.json`, APPROVE first pass,
  `rejects: 0`) and **Task 2 `DONE`** (verdict `…-F5-T2.json`, APPROVE first
  pass, `rejects: 0`) — its licence STOP condition fired, was RESOLVED by the
  human 2026-07-26 (Apache-2.0 per Google's three model cards,
  `memory/research/2026-07-26-f5-face-landmarker-licence-resolved.md`), and the
  bundle is vendored with LICENSE + NOTICE.
  **Task 3 `DONE`** (verdict `…-F5-T3.json`, APPROVE first pass, `rejects: 0`) —
  its licence STOP condition fired and did **not** clear: `portrait.jpg` is a
  White House press photograph whose notice forbids reproduction/dissemination.
  Resolved as **fetched-not-committed** — the image is `.gitignore`d and never
  entered git, while the Apache-2.0 `portrait_expected_face_landmarks.pbtxt` IS
  committed, preserving the **vendor reference** that exists for this image and
  no other. **Task 4 `DONE`** (verdict `…-F5-T4.json`, APPROVE first pass,
  `rejects: 0`) — `facedetect.py` exists: the per-frame composite path on
  injectable fakes, 14 new tests, suite at **102 passed**. `TARGET_FPS` and the
  camera lifecycle are deliberately NOT there — they are **Task 5's**, so no
  constant lands without a caller. **Task 5 `DONE`** (verdict `…-F5-T5.json`,
  **`rejects: 1`** — the feature's first REJECT, earned: an untested falsy-read
  branch, and drop-don't-queue pinned only as a pure function so deleting it
  from the loop still passed). Both fixed and **mutation-checked 4/4 by the
  verifier**, including the `wait(FRAME_INTERVAL)` mutation that exposed the
  original gap. **Throughput ~8 ms/frame** against the 33 ms budget, so
  `TARGET_FPS` stays at **30**. Suite: **114 passed**.
  **Task 6 `DONE`** (verdict `…-F5-T6.json`, APPROVE first pass, `rejects: 0`) —
  the Booth `<img>` sits in the existing 172 px disk with zero layout shift, no
  page-side cropping/scaling/mirroring, and **no camera state in JS**.
  **Task 7 is the LAST task** — `BoothApi` wiring + window-close release, whose
  done-criterion is the FULL `spec.md` Verification list and which will
  **`ESCALATE_HUMAN`** on the human-attested manual demo.
  Two amendments were made 2026-07-26, **both human-approved via box 2**: (1)
  the enforcement check for the per-asset licence guardrail; (2) the fixture
  change.**
  Verification runs on the **subagent** path for this feature — human-authorized
  2026-07-26 at the top of the implement session (`memory/decisions.md`), which
  resolves `handoff.md`'s open item 1 in favour of the Environment section's
  already-recorded `Verifier path: subagent`.
  (the Mode here is a convenience copy — `spec.md`'s Approval gate is the
  authoritative one on any disagreement, per the universal [State] precedence)
- Spec: `spec.md` holds F5's spec, `Status: CLEAR`, zero clarification markers,
  **both boxes checked** — box 2 re-approved 2026-07-26 after the fixture
  amendment. F4.5's ledger is closed and lives in git (`93bc887`); this file
  replaces it.

### The two escalation points, both now fired (Mode 3, mid-build)
Tasks 2 and 3 each downloaded an asset and **verified its licence at download**.
The spec forbids substituting a different model or image silently (`spec.md` §4).
Both fired, exactly as designed — **Task 2's cleared** (Apache-2.0, established
from Google's three model cards) and **Task 3's did not** (a White House press
photograph; resolved on the human's decision by keeping the image but **never
committing it**, via amendment). Splitting them into separate tasks earned its
keep: the model was not held hostage by the fixture.

### The module contract, pinned here so later tasks' criteria are runnable
Task 4 introduces `src/voicelock/facedetect.py` with this surface; Tasks 5–7 and
several done-criteria below name it, so it is fixed at plan time rather than
discovered:

```python
TARGET_FPS = 30                      # named constant — §4's fallback ladder is a one-line edit
FRAME_INTERVAL = 1.0 / TARGET_FPS
CAPTURE_WIDTH, CAPTURE_HEIGHT = 640, 480
PREVIEW_PX = 172

class FaceStatus(Enum): IDLE / RUNNING / ERROR

@dataclass
class FrameResult:
    data_uri: str                    # 'data:image/jpeg;base64,...' — 172 px, cropped, mirrored
    landmarks: list                  # ALL 478, unflipped, full-frame normalized coords

@dataclass
class FaceEngine:
    open_camera: Callable[..., Any]  # default cv2.VideoCapture — injectable, like CaptureEngine.open_input
    landmarker: Any | None           # injectable; default lazily loads the vendored .task bundle
    status: FaceStatus
    error_message: str | None
    def process_frame(self, frame) -> FrameResult   # Task 4: the pure per-frame transform
    def start(self, on_frame) -> None               # Task 5: opens camera + worker thread
    def stop(self) -> None                          # Task 5: stop → join → release, in that order
```

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [x] **Task 1** — Declare `mediapipe` + `opencv-contrib-python` (manifest only, no code)
  - state: DONE
  - rejects: 0
  - files: `pyproject.toml`, `uv.lock`
  - notes: `uv add mediapipe "opencv-contrib-python>=4.13,<5"` — nothing else. **No
    bare pip** (project convention). The TECH-PICK is already run and
    **human-approved** (`spec.md` §4 "The dependencies"; `memory/decisions.md`
    2026-07-26), so this task executes an approved choice; it does NOT re-open it.
    `uv.lock` is regenerated by `uv add` — the only other manifest edit.
    **`opencv-contrib-python`, never `opencv-python`** (`spec.md` §4): both install
    a top-level `cv2` and installing both shadows. MediaPipe pulls the contrib
    build transitively, so declaring *that* one keeps a single `cv2` and closes the
    undeclared-transitive gap in advance — the F4.5 `soundfile` lesson applied
    early rather than in arrears.
    First because everything after it needs `cv2` and `mediapipe` importable, and
    because once it lands every later `uv run pytest` in this feature also
    exercises the new resolution.
    **The risk this task actually carries** is not "does it install" but "does it
    move anything underneath F4": the TECH-PICK proved `uv pip compile` leaves
    `numpy==2.2.6` and `torch==2.13.0` in place. The done-criteria assert that
    outcome rather than trusting it — if the real `uv add` resolves differently
    from the compile-only dry run, F4's measured `CORRECTION_RADIUS = 110` and
    F3's `ACCEPT_CUTOFF = 0.45` are in range, and that must surface as a red Gate.
    No `facedetect.py` yet, no model, no fixture — this task adds zero code.
  - done-criteria:
    - `uv run python -c "import tomllib, pathlib; deps = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['dependencies']; low = [d.replace(' ', '').lower() for d in deps]; assert any(d.startswith('mediapipe') for d in low), 'mediapipe is not a declared dependency'; assert any(d.startswith('opencv-contrib-python') for d in low), 'opencv-contrib-python is not a declared dependency'; assert not any(d.startswith('opencv-python') for d in low), 'opencv-python is declared alongside the contrib build — two cv2 installs shadow each other'"` → exit 0 (`spec.md` §5's pinned command, verbatim — pins both declarations **and** the single-`cv2` rule)
    - `uv run python -c "import cv2, mediapipe; print(cv2.__version__, mediapipe.__version__)"` → exit 0 (the declared deps actually resolve in the synced environment, not just in the TOML)
    - `uv run python -c "import numpy, torch; assert numpy.__version__ == '2.2.6', f'numpy moved to {numpy.__version__} — F4 constants are out of range'; assert torch.__version__.split('+')[0] == '2.13.0', f'torch moved to {torch.__version__}'"` → exit 0 (pins the TECH-PICK's proved resolution — the guarantee `spec.md` §3 relies on)
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed — the whole F1–F4.5 suite still green after the lock regeneration)
  - feedback: (none)

- [x] **Task 2** — Vendor the Face Landmarker `.task` bundle, licence verified at download
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/models/face_landmarker/face_landmarker.task`,
    `src/voicelock/models/face_landmarker/LICENSE` (+ `NOTICE` if the source
    ships one)
  - notes: Assets only — **no engine code in this task.** Follows the F3 ECAPA
    precedent exactly: `models/ecapa/` carries its own `LICENSE` and `NOTICE`
    beside the weights, and this dir does the same. Canonical source, fetched
    **once at build time** (`spec.md` §4):
    `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`
    A build-time download is not a violation of "offline-only" — that rule is
    about **runtime**, and F3 established the shape. Nothing in `src/` may fetch
    this at run time; Task 4's source-level assertion pins that.
    **STOP condition — this is the escalation point, not a formality.** The
    bundle's byte size and its licence text are **unconfirmed** at spec time
    (`spec.md` §4). Both are checked at download, **before the file is
    committed**. If the licence is not permissive: set this task `BLOCKED`,
    report, and stop. Do **not** vendor it and do **not** substitute a different
    model silently. `spec.md` §4 is explicit, and the F5 spec's own §4 warns that
    "it came from Google's MediaPipe project" is **not** sufficient evidence —
    MediaPipe's own face_detector sample downloads a Pixabay-licensed image, so
    provenance must be established per-asset.
    Record the resolved licence, the URL, the fetch date and the measured byte
    size in the vendored `LICENSE`/`NOTICE` (or a short header comment beside
    them), so a verifier can check the claim rather than take it.
    `.task` is not matched by any `.gitignore` rule, so no ignore-exception is
    needed (unlike the `.wav` fixtures).
  - done-criteria:
    - `uv run python -c "import pathlib; p = pathlib.Path('src/voicelock/models/face_landmarker/face_landmarker.task'); assert p.is_file(), 'the model bundle is not vendored'; assert p.stat().st_size > 1_000_000, f'vendored bundle is implausibly small: {p.stat().st_size} bytes'"` → exit 0 (`spec.md` §5's pinned command, verbatim)
    - `uv run python -c "import pathlib; d = pathlib.Path('src/voicelock/models/face_landmarker'); assert (d / 'LICENSE').is_file(), 'the vendored model carries no licence file'; assert (d / 'LICENSE').stat().st_size > 100, 'the licence file is a stub'"` → exit 0 (the ECAPA precedent, made checkable)
    - `uv run python -c "import mediapipe as mp; from mediapipe.tasks.python import vision, BaseOptions; o = vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path='src/voicelock/models/face_landmarker/face_landmarker.task'), running_mode=vision.RunningMode.VIDEO); lm = vision.FaceLandmarker.create_from_options(o); lm.close(); print('bundle loads')"` → exit 0 (the bundle is a real, loadable Face Landmarker in **VIDEO** mode — not merely a file of the right size; no network is involved, `model_asset_path` is local)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed — adding an asset regresses nothing)
  - feedback:
    - **2026-07-26 — `BLOCKED` at the designed STOP condition. This is the
      planned behaviour, not a defect: the licence check ran and did not
      clear.** `rejects:` is deliberately left at 0 — the 3-attempt retry
      budget counts *failed fix attempts*, and nothing here is fixable by
      building differently.
      **Finding: the bundle's licence is `unconfirmed`, not "permissive".**
      Full evidence with sources and dates:
      `memory/research/2026-07-26-f5-face-landmarker-licence.md`. In short —
      the artifact carries no licence text (all four zip entries scanned, zero
      hits); the hosting bucket has no `LICENSE` (404 at three paths); the
      official guide states a licence only for *page content and code
      samples*; the `mediapipe` wheel is Apache-2.0 but ships **zero** model
      files; the `google-ai-edge/mediapipe` repo is Apache-2.0 but ships only
      `.pbtxt` graphs for this module and **zero** `.task` bundles; Kaggle's
      page is JS-gated; and web results trace back to Apache-2.0 headers in
      *code samples* — the exact evidence class `spec.md` §4 rules
      insufficient ("it comes from Google's MediaPipe project" is NOT
      sufficient evidence).
      The bundle **was downloaded** (3 758 596 bytes, SHA-256
      `64184E22…4E0BC9FF` — the size clears §5's `> 1_000_000` assertion) but
      was **not committed**, and was moved out of the repo tree so no
      `git add -A` can vendor it accidentally.
      **Most likely resolution, and it needs a human, not another tool call:**
      the three linked model cards are image-only PDFs with no extractable
      text and no OCR available here. They are downloaded and ready to read;
      a human opening them settles this in a minute. Second avenue: the Kaggle
      model page in a real browser.
      Substituting a different model is **forbidden** (`spec.md` §4), and
      changing the vendoring approach (e.g. fetching to `~/.voicelock/` at
      first run instead of committing) would be a **spec amendment** — §4
      mandates vendoring into the repo and §5 asserts the file exists at
      `src/voicelock/models/face_landmarker/face_landmarker.task`. Human-only
      in every mode.

- [x] **Task 3** — Face fixture: fetch `portrait.jpg` (gitignored) + commit the vendor reference and provenance README
  - state: DONE
  - rejects: 0
  - files: `tests/fixtures/face/README.md`,
    `tests/fixtures/face/portrait_expected_face_landmarks.pbtxt`, `.gitignore`
    (**not** `tests/fixtures/face/portrait.jpg` — that is fetched locally and
    deliberately never committed)
  - notes: Assets only again — **still no engine code.** Separated from Task 2 on
    purpose: the two licence checks can fail independently, and a blocked fixture
    must not also block the model. That separation earned its keep — Task 2
    cleared and this one did not.
    **REWRITTEN by the 2026-07-26 fixture amendment.** `portrait.jpg` **failed**
    its download-time licence check: it is a White House press photograph (EXIF
    `Artist = Pete Souza`) whose notice forbids reproduction or dissemination
    without written permission. Its "personal use only" clause is granted to
    **the subjects of the photograph**, not to whoever is using it for a personal
    project — the human weighed exactly that and chose **fetched-not-committed**
    over both committing it and substituting a CC0 image.
    So this task does NOT vendor the photo. It:
    1. adds `tests/fixtures/face/portrait.jpg` to `.gitignore`;
    2. fetches the image locally from
       `https://storage.googleapis.com/mediapipe-assets/portrait.jpg` so the
       Gate can run here (176 561 bytes, SHA-256 `A6F11EFA…2749DE3E`);
    3. **commits** `portrait_expected_face_landmarks.pbtxt` from
       `mediapipe/tasks/testdata/vision/` in the Apache-2.0
       `google-ai-edge/mediapipe` repo — that file genuinely ships there and is
       freely redistributable; **only the photograph is restricted**;
    4. writes the provenance README.
    **Why keep this image at all:** MediaPipe publishes expected landmarks for
    `portrait.jpg` and for **no other image**, so it is the only fixture against
    which Task 4's real-model test can assert **Google's own published
    coordinates** rather than a self-generated expectation. A fully-vendored CC0
    alternative was researched and verified (the Met's c.1850 daguerreotype,
    1 face / 478 landmarks) and is the **documented fallback**, but it cannot
    carry that reference.
    **The skip must not be silent** (`spec.md` §4, §5): a test that quietly
    skips when the fixture is absent is the F4.5 defect class in a new shape — a
    green Gate proving nothing. Task 4's real-model test `pytest.skip`s with an
    explicit reason naming the README, and the **presence check below** is what
    stops the Gate passing while it skips.
    The README follows the shape `tests/fixtures/voiceprint/README.md` already
    established, and must carry: the **exact fetch command**, the **full quoted
    copyright notice**, why the file is absent from git, and the note that this
    **inverts F3's precedent** — `.gitignore` already carries
    `!tests/fixtures/voiceprint/*.wav` precisely so "the Gate needs them on a
    clean checkout", and this is the first asset the Gate needs but the repo
    cannot ship.
    **Explicitly NOT a photo of the repo's owner** (`spec.md` §4): committing the
    owner's biometrics is a poor default and makes the fixture withdrawable, i.e.
    a test that breaks later. The owner's face is proven **live**, in Task 7's
    required manual check, never in git.
    Flagged forward: **F6 needs a second face** and now inherits this
    arrangement as well as the gap, plus a researched CC0 shortlist
    (`memory/research/2026-07-26-f5-fixture-replacement-candidates.md`).
  - done-criteria:
    - `uv run python -c "import pathlib; p = pathlib.Path('tests/fixtures/face/portrait.jpg'); assert p.is_file(), 'the face fixture is not present — fetch it per tests/fixtures/face/README.md; it is licence-restricted and deliberately not committed'; assert p.stat().st_size > 10_000, f'fixture is implausibly small: {p.stat().st_size} bytes'"` → exit 0 (`spec.md` §5's pinned presence check, verbatim — the thing that stops a skipping test turning the Gate green)
    - `uv run python -c "import subprocess; out = subprocess.run(['git', 'check-ignore', 'tests/fixtures/face/portrait.jpg'], capture_output=True, text=True); assert out.returncode == 0, 'the licence-restricted fixture is NOT gitignored'; out2 = subprocess.run(['git', 'ls-files', '--error-unmatch', 'tests/fixtures/face/portrait.jpg'], capture_output=True, text=True); assert out2.returncode != 0, 'the licence-restricted fixture is TRACKED by git — it must never be committed'"` → exit 0 (**both halves matter**: ignored *and* not already tracked. This is the criterion that actually enforces the human's decision; without it the arrangement is a comment, not a guarantee)
    - `uv run python -c "import pathlib; r = pathlib.Path('tests/fixtures/face/README.md'); assert r.is_file(), 'the fixture has no provenance README'; t = r.read_text(encoding='utf-8'); low = t.lower(); assert 'mediapipe-assets' in low, 'the README does not state the source URL'; assert 'white house' in low, 'the README does not quote the copyright notice'; assert 'gitignore' in low, 'the README does not explain why the file is absent from git'; assert 'portrait_expected_face_landmarks' in low, 'the README does not mention the committed vendor reference'"` → exit 0
    - `uv run python -c "import pathlib; p = pathlib.Path('tests/fixtures/face/portrait_expected_face_landmarks.pbtxt'); assert p.is_file(), 'the Apache-2.0 vendor reference is not committed'; assert p.stat().st_size > 10_000, f'vendor reference is implausibly small: {p.stat().st_size} bytes'"` → exit 0 (the reference IS redistributable and must be in the repo — it is what Task 4 asserts against)
    - `uv run python -c "import cv2; img = cv2.imread('tests/fixtures/face/portrait.jpg'); assert img is not None, 'the fixture is not a decodable image'; print(img.shape)"` → exit 0 (a real image, not a truncated download)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback:
    - **2026-07-26 — `BLOCKED` at the second designed STOP condition, and this
      one did NOT clear.** `rejects:` stays 0: the retry budget counts failed
      *fix attempts*, and no way of building differently makes a copyright
      notice go away.
      **Finding: `portrait.jpg` is NOT permissively licensed.** Its own EXIF
      carries `Artist = Pete Souza` and a White House copyright notice reading
      that the photograph *"may be printed by the subject(s) in the photograph
      for personal use only … may not be manipulated in any way and may not
      otherwise be reproduced, disseminated or broadcast, without the written
      permission of the White House Photo Office."* Committing a fixture **is**
      reproducing and disseminating it. Evidence:
      `memory/research/2026-07-26-f5-portrait-fixture-licence.md`.
      The Apache-2.0 BUILD file lists `portrait.jpg`, but the repo ships only
      the `portrait_expected_*.pbtxt` **outputs** — no `.jpg` at all — and a
      package-level Bazel licence cannot override an asset's own embedded
      notice. This is `spec.md` §4's predicted failure mode, more severe than
      predicted, and a textbook instance of the `[Approval]` per-asset
      guardrail approved the same day.
      The image was downloaded, its metadata read, and the file **deleted**.
      `tests/fixtures/face/` was never created; nothing is in git.
      **A verified replacement is ready and needs one human decision** —
      `-Elderly Man; Full Face- MET 37.14.52.jpg`, **CC0 1.0**, a c.1850
      daguerreotype donated by the Metropolitan Museum, which the vendored
      bundle detects at **1 face / 478 landmarks** (plain grey → 0 faces).
      Candidates, method and the rejected options:
      `memory/research/2026-07-26-f5-fixture-replacement-candidates.md`.
      **Adopting it is a spec amendment** — §4 names `portrait.jpg` explicitly
      and §5's pinned commands use the filename — so it is human-only, and the
      vendor-reference assertion against MediaPipe's published expected
      landmarks is lost (disclosed, per §5's own instruction to say so rather
      than silently assert less).
      **This blocks Tasks 4, 5 and 7**, whose criteria all name the fixture.
      Task 6 (UI) is the only later task independent of it.

- [x] **Task 4** — `facedetect.py`: the per-frame composite path, on injectable fakes
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/facedetect.py` (new), `tests/test_facedetect.py` (new)
  - notes: The engine's **pure** half — one frame in, one composited data URI plus
    all 478 landmarks out. **No thread, no start/stop lifecycle** (Task 5), so
    this task is verifiable by calling one method.
    Shaped after `capture.py`: injectable `open_camera` (default
    `cv2.VideoCapture`) and an injectable `landmarker`, so **no Gate test ever
    touches a real webcam** — the contract `CaptureEngine.open_input` established
    in F1. A `FaceStatus` enum with an ERROR state and a human-readable message,
    mirroring `_mic_error_message`.
    The pipeline, in this exact order (`spec.md` §4):
    `read()` → MediaPipe `detect_for_video` on the **full 640×480 frame** → cv2
    draws the **ellipse** + landmark subset → **centre-crop to a square** →
    downscale to 172 px → `cv2.flip(img, 1)` → `cv2.imencode('.jpg')` → base64.
    - **An ellipse, not a rectangle** — the preview is masked to a circle, so a
      rectangle's corners clip when a face nears the edge (human's call).
    - **Detection runs before the crop**, so a face at the edge of the field of
      view is still found; it is simply not shown.
    - **The flip is the LAST step before encoding, after the overlay is drawn**,
      so the oval and landmarks flip *with* the pixels and **no landmark
      coordinate is ever flipped**. That is what keeps this a one-line change
      instead of a source of mirror bugs. Any text drawn later must be drawn
      **after** the flip or it renders backwards — F5 draws no text; this is
      written down so a later feature does not learn it the hard way.
    - **`VIDEO` running mode, not `LIVE_STREAM`** (`spec.md` §4): synchronous and
      deterministic, so Gate tests cannot go flaky. It requires **monotonically
      increasing timestamps** — the engine owns that counter.
    - **`FrameResult.landmarks` carries all 478 even though only a subset is
      drawn.** Read this against the earned guardrail before flagging it: it is
      not unexercised surface — done-criterion (3) below pins it, and `spec.md`
      §4 requires it so F6/F8 do not have to reopen this module. Drawing is a
      display concern; the data contract must not narrow to match it.
    - **The no-face branch is a branch, so it gets a test** (criterion 4): the
      preview stays live, the overlay is simply not drawn, and no ERROR is raised.
    Camera-open failure is handled here too, because it is pure-ish and cheap to
    test: `cv2.VideoCapture` does **not** raise — it returns an object whose
    `isOpened()` is False, and/or `read()` returns `(False, None)`. **Both** must
    be handled; treating a falsy `read()` as merely "no frame yet" would spin
    forever (`spec.md` §4).
    **No startup camera probe** — `ready()` in `app.py` is untouched. This is a
    deliberate divergence from `_probe_mic` (`spec.md` §3, §4): opening a webcam
    costs seconds on Windows and every launch would pay it. A verifier should read
    its absence as intended, not as an oversight.
    The test file inherits **F4.5 Task 2's fake-stream shape**, translated to a
    polling device: the fake camera delivers frames through the **real `read()`
    the engine calls**, and those frames flow through the engine's real
    frame-handling path into the real composited output. A test that fabricates
    landmarks and skips that path is the F4.5 hole in a different shape.
    (The `release()` tripwire itself belongs to Task 5, where teardown exists.)
  - done-criteria:
    - `uv run pytest tests/test_facedetect.py -q` → exit 0; final summary reports 0 failed. Must cover, using only injectable fakes (**no real webcam**):
      (1) **frames flow through the real read path** — frames handed back by the fake camera's `read()` reach the engine's real frame-handling method and come out as a composited JPEG data URI; no test fabricates landmarks and skips that path;
      (2) **the overlay is drawn from real landmark output** — with an injected landmarker returning known normalized coordinates, the ellipse and the landmark points land on the expected **pixel** coordinates, and the centre-crop maps them correctly into the square that is finally shown (this is where a normalized-vs-pixel scaling bug or a crop-offset bug would show);
      (3) **the lip contour is among the drawn points, and the engine returns all 478** — F8 depends on both;
      (3b) **the preview is mirrored, and only the pixels are** — the composited output is the horizontal mirror of the unflipped composite, while `FrameResult.landmarks` is **unflipped**. An asymmetric synthetic frame makes this unambiguous. This is the test that catches someone "fixing" the mirror by flipping coordinates instead of pixels;
      (4) **no face in frame is a normal state** — a frame is still produced, the overlay is absent, no ERROR;
      (7) **camera-open failure surfaces as ERROR** — both `isOpened()` False and `read()` returning `(False, None)` produce an ERROR status with a human-readable message, and no crash and no spin
    - **The real model detects a real face** — a test in `tests/test_facedetect.py` that runs the **vendored bundle** (no injected landmarker) against `tests/fixtures/face/portrait.jpg` and asserts a face is found with 478 landmarks, and that a plain-colour image yields **no** face. This is the line that separates "the bundle is on disk" from "the bundle works". Assert against MediaPipe's committed `portrait_expected_face_landmarks.pbtxt` — a **vendor reference**, not a self-generated expectation — where the format is practical to parse; if not, say so in the README. **Amended 2026-07-26:** the image is fetched-not-committed, so this test must `pytest.skip` with an explicit reason naming the README when it is absent — never silently, never with fabricated landmarks as a proxy; the pinned presence check is what keeps the Gate honest
    - `uv run python -c "import inspect; from voicelock import facedetect; s = inspect.getsource(facedetect); assert 'model_asset_path' in s, 'model is not loaded from a local path'; assert 'http://' not in s and 'https://' not in s, 'facedetect.py references a URL'"` → exit 0 (`spec.md` §5's pinned command, verbatim — the offline guarantee at source level)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [x] **Task 5** — `facedetect.py`: camera lifecycle — 30 fps worker, drop-don't-queue, release tripwire
  - state: DONE
  - rejects: 1
  - measured: **throughput floor 8.0–8.7 ms/frame** across four runs (8.1 and
    8.7 by the implementor, 8.2 and 8.0 by the two verifiers) against the 33 ms
    budget — roughly **4x headroom**. **`TARGET_FPS` stays at 30**; the fallback
    ladder was not needed and the assertion was not loosened. Task 7's
    completion report pins the number from the final Gate run. This measures the
    **engine only** — the `evaluate_js` bridge half is Task 7's live check.
  - files: `src/voicelock/facedetect.py`, `tests/test_facedetect.py`
  - notes: The stateful half: `start(on_frame)` opens the camera and runs a
    **daemon thread**; `stop()` halts the loop, **joins**, and only then calls
    `release()`.
    **Carried in from Task 4's verifier (2026-07-26), non-blocking there but
    load-bearing here:** `acquire_camera()` clears `error_message` on entry
    (`facedetect.py:114`) but never resets `status` on success, so a successful
    re-acquire after a prior failure would leave `status == FaceStatus.ERROR`
    with no message. `capture.py:79` sets `status` on its success path; the
    analog is `start()`, which this task owns. It bears directly on
    criterion (6) below — "a second start after stop works" — and on a Record
    that follows a failed Record.
    - **Its own thread — not `app.py`'s 50 ms `_pump_loop`** (`spec.md` §4). That
      loop serves audio levels and must not be made to wait on a JPEG encode.
    - **`TARGET_FPS` is a named module constant**, so §4's fallback ladder is a
      one-line edit rather than a hunt for scattered literals.
    - **Drop frames, never queue them.** If a frame overruns its 33 ms budget the
      next frame is **skipped**, not buffered. This matters more than the target
      number: a queueing pipeline does not merely run slow, it **drifts** — the
      preview falls seconds behind and keeps falling, which reads as a freeze
      rather than as a low frame rate. Always render the **latest** frame.
    - **Ordering is the whole point of `stop()`**: loop stops → thread joined →
      `release()`. A frame read after release is a bug, and the fake trips on it.
    - `on_frame` is the callback the engine hands each `FrameResult` to; Task 7
      supplies the one that pushes to the page. Keeping the push out of the
      engine is what keeps `app.py` thin and the page a pure renderer.
    **The release tripwire, per `spec.md` §4 and the F4.5 lesson:** the fake
    camera must **raise immediately** if `read()` is called after `release()`, and
    that exception must be a **`BaseException` subclass** if the engine's teardown
    path wraps anything in a blanket `except Exception` — otherwise it is
    swallowed and the test passes over a live defect. **Verify that deliberately
    rather than assuming**; F4.5 proved a plain `Exception` tripwire is silently
    eaten by `capture.py`'s `except Exception: pass` handlers. `tests/test_capture.py`'s
    `ReentrantTeardown` is the working precedent to copy.
    **Window close** is not wired here — that is Task 7, where `app.py` owns the
    window. This task only guarantees `stop()` is correct and idempotent enough to
    be called from a close handler.
    **The throughput floor lands here**, because the constant it justifies lives
    here. It is set **at** the target, not below it: if the engine cannot hit
    30 fps on its own, a 30 fps target is a fiction, and it is better to learn
    that from a red Gate than from a stuttering demo. **If it fails, the answer is
    §4's fallback ladder** — lower `TARGET_FPS` to 20, then 15, on the **measured**
    evidence, and pin the number in the completion report. It is **not** to loosen
    the assertion to match whatever the code happens to do, and **not** to reach
    for the rejected loopback-MJPEG transport (that rejection is recorded with its
    reason in `memory/decisions.md`; reopening it needs a fresh human decision).
    Note honestly what this measures: the **engine**, not the `evaluate_js`
    bridge. Passing it means the engine can feed 30 fps, not that 30 fps reaches
    the screen — the bridge half is Task 7's manual check.
  - done-criteria:
    - `uv run pytest tests/test_facedetect.py -q` → exit 0; final summary reports 0 failed. Must additionally cover, using only injectable fakes (**no real webcam**):
      (5) **Stop releases the camera** — `release()` is called exactly once, the worker thread is joined **first**, and the fake **raises** if `read()` happens afterwards, so a leak fails **fast** instead of hanging the suite;
      (6) **a second start after stop works** — a fresh camera is opened and frames flow again;
      plus: **frames are dropped, not queued** — with a fake clock or a deliberately slow frame path, the engine skips the overrun frame rather than accumulating a backlog, and the callback receives the **latest** frame;
      and every Task 4 test still passes unchanged
    - `uv run python -c "import pathlib; t = pathlib.Path('tests/test_facedetect.py').read_text(encoding='utf-8'); assert 'release' in t, 'the camera tests never mention release'; assert 'read' in t, 'the camera tests never drive the real read path'"` → exit 0 (`spec.md` §5's pinned command, verbatim — the per-module analog of F4.5's `assert 'callback' in <test file>`, adapted honestly to a **polling** device)
  - feedback:
    - **2026-07-26 — REJECT #1** (Gate PASS 6/6 incl. throughput 8.2 ms/frame;
      Review REJECT on both axes). Two findings, both accepted without
      argument:
      **(1) `_loop`'s falsy-read branch is untested dead surface.**
      `facedetect.py:194-196` breaks on `not ok or frame is None`, but every
      `engine.start(...)` in the suite either uses a `repeat=True` fake that can
      never return falsy or fails at `isOpened()` so no thread starts. This is
      the **first earned guardrail** — the one that cost F4 three REJECTs — and
      `spec.md` §4 binds F5 to it verbatim ("every branch added here must have a
      caller and a test", explicitly including the no-face branch). It also has
      a real consequence I flagged the semantics of but not the coverage gap:
      the `break` leaves `status == RUNNING` with `_camera` still held, so a
      transient read failure kills the preview silently, with no ERROR and no
      recovery path — and `start()` would then leak the held camera.
      **Fix:** drive `start()` with a finite-frame `repeat=False` fake, decide
      the end state deliberately (ERROR, not a silent RUNNING), and make
      `start()` unable to leak a stale camera.
      **(2) The drop-don't-queue behaviour is not pinned at the loop level.**
      `test_frames_are_dropped_not_queued...` tests `pacing_delay` as a pure
      function only, and `test_worker_paces_itself_with_the_injected_clock`'s
      sole pacing assertion (`read_count >= len(received)`) holds **by
      construction** of `_loop`. The verifier proved the gap: replace
      `self._stop_event.wait(pacing_delay(...))` with a fixed
      `wait(FRAME_INTERVAL)` — deleting the drop behaviour outright — and all 23
      tests still pass. Right shape, empty substance; the injected `clock`
      existed with no test using it for its purpose.
      **Fix:** discriminate on observed cadence — an overrun clock must produce
      no wait, an under-budget clock must produce one — so a fixed-wait
      implementation fails.
      Non-blocking, recorded not actioned: `_wait_for` polling, `JOIN_TIMEOUT`
      chosen rather than measured, tests touching `engine._thread`. And for
      **Task 7**: if `stop()`'s join times out, `release()` runs anyway while
      the worker may still be mid-read — a 5 s window that only opens if a frame
      hangs.
    - `uv run python -c "import inspect; from voicelock import facedetect; s = inspect.getsource(facedetect); assert 'TARGET_FPS' in s, 'the frame rate is not a named constant'"` → exit 0 (pins §4's one-line-fallback requirement)
    - **Throughput floor**, against the **real** vendored model and the `portrait.jpg` fixture: `uv run python -c "import time, cv2, numpy as np; from voicelock import facedetect; eng = facedetect.FaceEngine(); frame = cv2.resize(cv2.imread('tests/fixtures/face/portrait.jpg'), (facedetect.CAPTURE_WIDTH, facedetect.CAPTURE_HEIGHT)); [eng.process_frame(frame) for _ in range(3)]; t0 = time.perf_counter(); [eng.process_frame(frame) for _ in range(30)]; ms = (time.perf_counter() - t0) / 30 * 1000; print(f'{ms:.1f} ms/frame'); assert ms < 33, f'engine cannot sustain the 30 fps target: {ms:.1f} ms/frame'"` → exit 0, and **the printed number goes in the completion report**. Covers detect + overlay + crop + flip + JPEG encode for 30 consecutive 640×480 frames, averaging under 33 ms
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed)
  - feedback: (none)

- [x] **Task 6** — Booth UI: the `<img>` preview in the face disk, `setFaceFrame` / `setFaceIdle`
  - state: DONE
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: The page's **only** job (`spec.md` §4): assign the pushed data URI to an
    `<img>` inside `.face-wrap`, and swap back to the smiley SVG on
    `setFaceIdle()`. Both go on `window.voicelockBooth`, next to `setLevel` /
    `setRecording`, which is how every Python→page call in this app already works.
    Placed **before** the bridge task on purpose: the page function exists before
    anything calls it, so Task 7's wiring is never calling into a hole. (`_eval`'s
    existing `window.voicelockBooth && … &&` guard would make it a silent no-op
    either way, but "define the receiver first" is the honest order.)
    - The preview replaces the decorative smiley **in place**, in its existing
      **172 px** circle (`index.html:296-316` `.face-wrap` 172×172 / `.face-disk`
      `border-radius: 50%`), with **zero layout shift** — the human's placement.
    - The `<img>` is masked to the circle and fills the disk with **no
      letterboxing**; Python already delivers a 172 px square, so the page does no
      cropping and no scaling maths of its own.
    - **The page holds no camera state** — the third earned guardrail
      (`project.md`, "the UI must not keep its own copy of state the engine
      owns"). It renders what Python pushes and nothing else: no frame counter, no
      "is the camera on" boolean, no mirroring in CSS. `setRecording()` already
      exists for recording state; do not add a parallel camera flag beside it.
    - **No restyling** (`spec.md` §3): the oval and landmarks are drawn by OpenCV
      and will look like OpenCV. Matching the Booth's visual language is F9 polish.
    - **No expanded preview** (`spec.md` §3): 172 px is what F5 builds. The 440 px
      rectangle is deferred, not hidden here.
    Honest note on the criteria below: this repo's Gate is **pytest with zero JS
    tests**, so a UI-only task cannot be proven by unit test — the runnable
    criteria pin *presence and export*, and the real proof is Task 7's
    human-attested live check. That is the same shape F3's and F4's UI tasks used;
    it is stated rather than papered over.
  - done-criteria:
    - `uv run python -c "import pathlib; h = pathlib.Path('src/voicelock/ui/index.html').read_text(encoding='utf-8'); assert h.count('setFaceFrame') >= 2, 'setFaceFrame is missing or defined but never exported on window.voicelockBooth'; assert h.count('setFaceIdle') >= 2, 'setFaceIdle is missing or defined but never exported'; assert 'face-frame' in h, 'there is no <img> element for the camera preview'; assert 'face-wrap' in h, 'the preview is not in the existing 172 px face disk'"` → exit 0
    - `uv run python -c "import pathlib; h = pathlib.Path('src/voicelock/ui/index.html').read_text(encoding='utf-8'); assert 'getUserMedia' not in h, 'the page tries to open the camera itself — Python owns the camera (file:// has no secure context)'; assert 'scaleX(-1)' not in h, 'the page mirrors in CSS — the flip belongs in Python, after the overlay is drawn'"` → exit 0 (pins the two architecture decisions the page could quietly violate)
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (final summary reports 0 failed — the UI change regresses no Python test)
  - feedback: (none)

- [ ] **Task 7** — Wire `BoothApi` to Record/Stop + release on window close (LAST task — FULL §5)
  - state: DOING
  - rejects: 0
  - files: `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: The wiring that makes the demo real. `start_record` starts the camera,
    `stop_record` stops it, and the engine's `on_frame` callback pushes each data
    URI to the page via the existing `_eval` path — the same shape `_pump_loop`
    already uses for `setLevel`.
    - **A camera failure must NOT prevent audio recording** (`spec.md` §5). The
      microphone path survives a broken webcam: `start_record` still starts
      capture, still starts the level pump, still returns `ok`. The camera's ERROR
      status is surfaced the way `_push_mic_error` surfaces a mic error, not by
      failing the take. This is a real branch and it gets a test.
    - **Window close while recording must release the camera** — a stuck webcam
      light after the app exits is the same defect wearing a different hat
      (`spec.md` §4). `main()` currently has **no** close handler at all
      (`app.py:399-412`), so this task adds one and points it at `stop()`. That
      makes `stop()` needing to be safe to call twice a real requirement, not a
      theoretical one.
    - **`ready()` is untouched** — no startup camera probe (`spec.md` §3).
    - **`capture.py` is not touched** (`spec.md` §3): the camera is a sibling of
      the microphone, not a modification of it. F4.5's `sd.CallbackStop` fix and
      its tests stay exactly as they are.
    - Nothing is written to disk: frames are transient, `~/.voicelock/` gains no
      new file, the vault and crypto surface are untouched (`spec.md` §3).
    This is the feature's LAST task — its done-criterion is the FULL `spec.md`
    **Verification** list, including the required human-attested manual demo.
    **Expect the Gate to return `ESCALATE_HUMAN` on that line** (the F3-T5 / F4-T5
    / F4.5-T3 precedent): do NOT mark the task `DONE` and do NOT write its verdict
    file until the human attests the demo.
  - done-criteria: FULL list from `spec.md` **Verification** section:
    - `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
    - `uv run pytest` → exit 0 (final summary reports 0 failed — the whole existing suite, including all F1–F4.5 tests, still green). Runtime budget: F4.5's final Gate measured **88 passed in 50.42 s**; MediaPipe adds a model load, the real-model detection test and the throughput probe. Whole-suite budget is **within the 10-minute default**; **if the suite exceeds 5 minutes, say so in the completion report** rather than quietly accepting it
    - `uv run pytest tests/test_facedetect.py -q` → exit 0; final summary reports 0 failed. Covers, using only injectable fakes (no real webcam), items (1) (2) (3) (3b) (4) (5) (6) (7) from `spec.md` §5 — built in Tasks 4 and 5
    - **The real model detects a real face** — the vendored bundle (no injected landmarker) against `tests/fixtures/face/portrait.jpg`: a face with 478 landmarks asserted against the committed vendor reference; a plain-colour image yields none. Skips explicitly if the fetched-not-committed fixture is absent, and the pinned presence check below fails the Gate in that case
    - `uv run pytest tests/test_booth_api.py -q` → exit 0; final summary reports 0 failed. Must **additionally** cover that `start_record` starts the camera and `stop_record` stops it, and that a camera failure does **not** prevent audio recording
    - `uv run python -c "import inspect; from voicelock import facedetect; s = inspect.getsource(facedetect); assert 'model_asset_path' in s, 'model is not loaded from a local path'; assert 'http://' not in s and 'https://' not in s, 'facedetect.py references a URL'"` → exit 0
    - `uv run python -c "import pathlib; p = pathlib.Path('src/voicelock/models/face_landmarker/face_landmarker.task'); assert p.is_file(), 'the model bundle is not vendored'; assert p.stat().st_size > 1_000_000, f'vendored bundle is implausibly small: {p.stat().st_size} bytes'"` → exit 0
    - `uv run python -c "import tomllib, pathlib; deps = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['dependencies']; low = [d.replace(' ', '').lower() for d in deps]; assert any(d.startswith('mediapipe') for d in low), 'mediapipe is not a declared dependency'; assert any(d.startswith('opencv-contrib-python') for d in low), 'opencv-contrib-python is not a declared dependency'; assert not any(d.startswith('opencv-python') for d in low), 'opencv-python is declared alongside the contrib build — two cv2 installs shadow each other'"` → exit 0
    - `uv run python -c "import pathlib; t = pathlib.Path('tests/test_facedetect.py').read_text(encoding='utf-8'); assert 'release' in t, 'the camera tests never mention release'; assert 'read' in t, 'the camera tests never drive the real read path'"` → exit 0
    - `uv run python -c "import pathlib; dirs = [d for d in pathlib.Path('src/voicelock/models').iterdir() if d.is_dir()]; assert dirs, 'no vendored model dirs found'; missing = [f'{d.name}/{n}' for d in dirs for n in ('LICENSE', 'NOTICE') if not (d / n).is_file() or (d / n).stat().st_size <= 100]; assert not missing, f'vendored model dir missing a non-stub LICENSE/NOTICE: {missing}'"` → exit 0 (**added by the 2026-07-26 spec amendment** — the enforcement half of `project.md`'s per-asset licence-provenance guardrail; standing, so it is part of the full list this task runs)
    - **Throughput floor** (Task 5's pinned command, re-run here as part of the full list) → exit 0, averaging **under 33 ms/frame**; the measured number goes in the completion report
    - **Manual (required for F5 done, human-attested):** run `uv run voicelock` → press **Record**. The smiley is replaced by a live, **circular** camera image in the same 172 px disk, with an oval outline and landmarks **tracking your face as you move**, and the preview looks like smooth video rather than a slideshow. The image fills the disk with **no letterboxing**. It is **mirrored**: raising your right hand moves the hand on the right of the picture, and leaning left moves you left — the way a mirror behaves, not the way a stranger's camera does. The preview must also stay **in step with you** — no drifting behind, no growing lag the longer it runs. Press **Stop**: the smiley returns, **the webcam light goes out**, and pressing **Record a second time** brings the preview back. Close the window while recording: **the webcam light goes out.** (Observable: the camera is genuinely opened, genuinely drawn on, and genuinely released. The automated tests prove the pipeline's logic against fakes; they do **not** prove the composited frames reach the page fast enough to look like video, nor that a real Windows webcam device is genuinely freed — that is what this line covers.)
  - feedback: (none)

## Memory spine
≤5 bullets — the compressed truth of where we are. Prune resolved items every session.

1. 2026-07-26 — **F5 is BUILDING: Tasks 1–6 `DONE`, only Task 7 remains.** Five
   of six landed APPROVE on the first pass; **Task 5 took one REJECT**
   (`rejects: 1`) for an untested branch and a tautological pacing test, both
   since fixed and mutation-checked 4/4. Dependencies declared
   (`mediapipe==0.10.35`, `opencv-contrib-python==4.13.0.92`) with **nothing
   moved underneath F4** — `numpy` 2.2.6, `torch` 2.13.0 — so
   `CORRECTION_RADIUS = 110` and `ACCEPT_CUTOFF = 0.45` are undisturbed; the
   Face Landmarker bundle is vendored (Apache-2.0, LICENSE + NOTICE); the face
   fixture is **fetched-not-committed** with its Apache-2.0 vendor reference
   committed beside it; and **`facedetect.py` now does the per-frame composite**
   — detect on the full frame, ellipse + landmarks, crop, flip last — verified
   against MediaPipe's published coordinates at 0.005645 max deviation; and the
   **camera lifecycle** runs on its own daemon thread with halt→join→release
   ordering, drop-don't-queue pacing and a `BaseException` release tripwire, at
   **~8 ms/frame** against the 33 ms budget; and the **Booth `<img>`** renders
   what Python pushes, in the existing disk, holding no camera state of its own.
   Suite: **114 passed**. Remaining: **Task 7 only** — `BoothApi` wiring,
   window-close release, the FULL §5 list, and the human-attested live demo.
   **Verification runs on the subagent path** for F5 — human-authorized
   2026-07-26, which closed the previous handoff's open item 1.
   **A guardrail UPDATE is parked in `handoff.md`**, unwritten pending human
   approval.
2. Shape of the build: **1** declare the two approved deps → **2** vendor the
   `.task` bundle → **3** fetch (not commit) `portrait.jpg` + commit the vendor reference → **4**
   `facedetect.py` per-frame composite on fakes → **5** camera lifecycle
   (30 fps worker, drop-don't-queue, release tripwire, throughput floor) → **6**
   the Booth `<img>` → **7** `BoothApi` wiring + window close (**LAST**, FULL §5,
   human-attested manual check).
3b. **The SECOND designed STOP point fired and did NOT clear (Task 3,
   2026-07-26).** `portrait.jpg` is a **White House press photograph** (EXIF
   `Artist = Pete Souza`) whose embedded notice forbids reproduction or
   dissemination without written permission — committing a fixture is exactly
   that. Its "personal use only" clause is granted to **the subjects of the
   photograph**, not to whoever is using it for a personal project. The
   Apache-2.0 repo ships only the `portrait_expected_*.pbtxt` outputs, never the
   image, so the BUILD file's package licence does not reach it.
   **Resolution (human, 2026-07-26): fetched-not-committed.** Keep
   `portrait.jpg`, `.gitignore` it, fetch it locally, and **commit** the
   Apache-2.0 `portrait_expected_face_landmarks.pbtxt` beside it — preserving
   the **vendor reference**, which exists for this image and no other. A
   fully-vendored **CC0** alternative was researched and verified end-to-end
   (the Met's c.1850 `-Elderly Man; Full Face-`, 1 face / 478 landmarks) and is
   the documented fallback. The arrangement's own risk — a silently skipping
   test turning the Gate green — is closed by an explicit `pytest.skip` reason
   plus a pinned **presence check** in §5. Adopting it is a **spec amendment**,
   human-only, awaiting box 2. Blocks Tasks 4, 5, 7.
   Evidence: `memory/research/2026-07-26-f5-portrait-fixture-licence.md` and
   `…-f5-fixture-replacement-candidates.md`.

3. **The FIRST designed STOP point fired and was RESOLVED (Task 2,
   2026-07-26).** Eight primary sources — the artifact, the bucket, the docs,
   the wheel, the repo, Kaggle, web search — said **nothing** about the model
   weights' licence, so the bundle was not committed and the task went
   `BLOCKED`. The human then read Google's three model cards (image-only PDFs,
   no OCR available here) and found the **Apache-2.0** link, corroborated
   mechanically by extracting each PDF's link annotations: all three cite
   `apache.org/licenses/LICENSE-2.0.html`, and they map 1:1 onto the bundle's
   three `.tflite` models. Provenance is therefore established **per asset**,
   the standard `spec.md` §4 sets. Evidence:
   `memory/research/2026-07-26-f5-face-landmarker-licence-resolved.md`.
   **Task 3's own licence STOP point is still ahead and unrelated** — and the
   spec's cited counter-example (MediaPipe's own sample ships a *Pixabay*-licensed
   image) says it may well not clear as easily. Substituting a different model
   or image silently is forbidden; changing the vendoring approach, or replacing
   the real-model test with a written limitation, is a **spec amendment** —
   human-only.
4. **F4.5's fake-stream shape is what Tasks 4–5 inherit**, translated to a
   polling device: `cv2.VideoCapture` has no callback, so **`read()` is the real
   path** the fake must deliver through and **`release()` is the teardown** it
   must trip on — with a **`BaseException`** subclass, as F4.5 proved is
   necessary against blanket `except Exception` handlers.
5. **Known unmeasured risk carried into the build:** nobody has measured what
   frame rate `evaluate_js` sustains across pywebview's WebView2 bridge on this
   machine. The 172 px preview (~8 KB/frame) is the mitigation; Task 5's
   throughput floor covers the **engine** half and Task 7's live check covers the
   **bridge** half. Fallback if 30 fps is not reachable: lower `TARGET_FPS` to 20,
   then 15, **on measured evidence** — never loosen the assertion, and never
   reopen the rejected loopback-MJPEG transport without a fresh human decision.

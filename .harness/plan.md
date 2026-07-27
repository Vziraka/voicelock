# Plan — F6 — Faceprint on screen

## Active context
- Updated: 2026-07-27
- Feature: Feature 6 from `roadmap.md` · Mode: **Mode 3 — Spec-to-done** ·
  Phase: **Ready to build.** Spec approved (both boxes checked 2026-07-27),
  Grilling record `CLEAR`, zero `NEEDS-CLARIFICATION` hits (grep-verified this
  session). This is the first task ledger for F6 — `/implement` starts Task 1.
- Spec: `spec.md` holds F6's spec, `Status: CLEAR`, both approval boxes
  checked, `Mode: Mode 3` set 2026-07-27 by the human.
- One plan-time design gap the spec deliberately left open (`§5 cmd 3` note:
  "exact call shape... set at `/plan`") was resolved with the human this
  session — see memory spine item 1 and `memory/decisions.md`'s 2026-07-27
  entry.

### Why this feature exists, in one line
The visual analog of F3 for the face — a diagnostic meter, not a lock (F7
wires it in). Two hard sub-problems (a genuine same-person fixture pair, and
getting SFace its aligned crop from MediaPipe's landmark scheme instead of
YuNet's) were already resolved by dedicated `research` runs during grilling,
so this ledger builds on settled ground rather than open questions.

### The dependency that fixes the task order
Tasks 1 and 2 are independent of each other (model vendoring vs. fixture
commit) but both must land before Task 3, which is the first task that
imports real weights and reads real fixture files in its done-criteria. Task 3
must precede Task 4 (the Booth bridge calls `faceprint.py`), which must
precede Task 5 (the UI calls the bridge). WIP=1 makes the ordering below the
actual build sequence, not just a dependency note.

### Named architecture decisions carried into this ledger
1. **`REJECT_CUTOFF = ACCEPT_CUTOFF = 1.128` (L2 distance), decided this
   session.** OpenCV's two published SFace numbers (cosine ≥ 0.363, L2 ≤
   1.128) are the *same* operating point in two metrics, not two independent
   bars (L2² = 2(1−cosine) for unit vectors: √(2−2×0.363) = 1.1287 ≈ 1.128).
   Q5 gives exactly one number and explicitly forbids deriving a second,
   repo-measured one. Put to the human with two options; the human chose the
   one that invents nothing: the meter still renders as F3's three-colour
   gradient, but the borderline band has zero width in practice. `compare()`
   returns raw **L2 distance** (OpenCV's `DIS_TYPE_L2`, usable as-is, no unit
   conversion), not cosine. Full writeup: `memory/decisions.md` (2026-07-27
   entry). **Task 3's done-criteria depend on this — do not re-derive or
   widen it.**
2. **`faceprint.py`'s public `embed_frame`/`embed_file` are self-contained** —
   each runs its own MediaPipe detection (a **second**, `IMAGE`-mode
   `FaceLandmarker` instance, loaded from the SAME already-vendored
   `models/face_landmarker/face_landmarker.task` — no new model, no new
   package) rather than accepting pre-computed landmarks. This matches §5 cmd
   4's pinned call shape exactly (`embed_frame(img720)` — a raw array, no
   landmarks argument) and mirrors `voiceprint.embed`'s self-containedness
   (raw audio in, nothing pre-extracted). `IMAGE` mode (synchronous,
   one-shot, no timestamp bookkeeping) is the right choice for a standalone
   frame/file — it is intentionally a *different* landmarker instance from
   `facedetect.py`'s `VIDEO`-mode one, which stays untouched (non-goal:
   "does not re-cut the F5 composite").
3. **The live Booth path needs one small additive read from `FaceEngine`: the
   last raw (pre-overlay) frame.** `FrameResult` only carries the composited
   `data_uri` (already mirrored + annotated — unusable for embedding, and
   re-decoding it would double-encode a JPEG for no reason) and `landmarks`
   (facedetect's own detection, from a different landmarker instance per
   decision 2). Task 4 adds a `last_frame` field to `FaceEngine`, set each
   loop tick to the raw frame `FaceEngine._loop` already holds, with a small
   accessor. This is additive only — it changes no cropping, mirroring,
   threading, or lifecycle behavior, so it does not conflict with §3's
   non-goal about `facedetect.py`'s composite/lifecycle.
4. **On-demand timing (Q6):** the live meter recomputes on a low fixed
   interval (JS-side `setInterval`, mirroring how F3's meter updates once per
   take rather than every frame) calling a bridge method that embeds
   `FaceEngine.last_frame` — never inside the 30 fps preview loop itself.

### Memory spine (≤5)
1. **`REJECT_CUTOFF == ACCEPT_CUTOFF == 1.128`, L2 distance — human-decided
   this session, do not invent a second number.** See decision above and
   `memory/decisions.md`.
2. **Fixtures are already sourced by research, not by this ledger:** A1 =
   Douglass 1870 (LOC), A2 = Douglass c.1879 (NARA), B = MET elderly-man
   daguerreotype (CC0) — `memory/research/2026-07-26-f6-same-person-fixture-pair.md`.
   Task 2 fetches and commits them (unlike `portrait.jpg`, all three are
   Public domain/CC0 with no redistribution restriction, so — like the voice
   fixtures — they are committed, not `.gitignore`d).
3. **The MediaPipe→SFace alignment is verified, not experimental:**
   5-point YuNet-shaped row from landmark indices 33/133 (eye), 263/362 (eye),
   4 (nose), 61/291 (mouth corners), confirmed by real embeddings on the Q1
   fixtures (same-person 0.7325 cosine/0.7314 L2; different-person 0.10–0.14
   cosine/1.31–1.34 L2). `memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md`.
   Task 3 implements this exact scheme — it is not a research task.
4. **Convert, never refuse, is the whole point of this feature's inherited
   blind spot.** `voiceprint.py`'s refuse-on-mismatch pattern is correct only
   because `capture.py` pins the mic; camera frames vary legitimately, so
   `faceprint.py` resizes/converts. §5 cmd 4 and cmd 5 make this runnable —
   Task 3 must not reproduce F5.5's original mistake.
5. **No lock wiring, no liveness claim.** `faceprint.py` never touches
   `vault.py` (that's F7); the Booth panel must visibly disclose "match, not
   liveness" (§5 cmd 7, Task 5) — a photo held to the camera is *expected* to
   pass this feature's meter, on purpose.

## Task ledger
One task `DOING` at a time (**WIP=1**). States: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`.
A task is `DONE` only per `constitution/universal.md`'s [Done] rules — Gate exited 0,
Reviewer approved, **and** a matching verdict file exists in `memory/verdicts/`.
The `DOING` write is committed BEFORE building starts (implement skill step 3).
`rejects:` is the durable retry count — 3 failed fix attempts set the task `BLOCKED`.

- [ ] **Task 1** — Vendor the SFace ONNX weights and establish their per-asset licence
  - state: DOING
  - rejects: 0
  - files: `src/voicelock/models/sface/*.onnx`, `src/voicelock/models/sface/LICENSE`,
    `src/voicelock/models/sface/NOTICE`
  - notes: Q7's research already downloaded
    `face_recognition_sface_2021dec.onnx` (opencv_zoo, ~38.7 MB) to a session
    scratchpad for testing only — **nothing from that session was committed**,
    per its own closing note. This task re-fetches it properly and, before
    anything lands under `src/`, runs the SAME per-asset licence protocol that
    cleared `models/ecapa/` and `models/face_landmarker/`
    (`project.md`'s guardrail 1): embedded metadata first (ONNX files carry a
    `metadata_props`/`doc_string` — check with the `onnx` library or a manual
    protobuf read before assuming there is none, the way the `.task` bundle's
    four zip entries were scanned), then primary sources that name **this
    asset** specifically (opencv_zoo's own per-model licence declaration,
    not just "opencv_zoo is Apache-2.0" as a repo-level inference — that is
    exactly the reasoning `project.md`'s guardrail forbids). Verify the fetch
    with a SHA-256 comparison against a second independent fetch, mirroring
    `models/face_landmarker/NOTICE`'s "re-fetched and compared" verification.
    **If the licence does not clear cleanly** (an asset naming gap, an
    unclear or restrictive term), this is a Mode 3 rule you cannot resolve
    unsupervised: STOP, set this task `BLOCKED`, and report — do not guess or
    substitute a different model (§4 forbids substitution outright, same as
    F5's Q2).
    `LICENSE`/`NOTICE` follow the exact shape of `models/face_landmarker/`'s
    (a NOTICE that states what was actually checked, not more than that).
  - done-criteria:
    - §5 cmd 1 — verbatim, exit 0:
      ```
      uv run python -c "import pathlib; d = pathlib.Path('src/voicelock/models/sface'); assert d.is_dir(); assert (d / 'LICENSE').stat().st_size > 200; assert (d / 'NOTICE').stat().st_size > 200"
      ```
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed; count unchanged from F5.5's 124 — this task adds no tests)

- [ ] **Task 2** — Commit the three face fixtures (personA_1, personA_2, personB) with provenance README
  - state: TODO
  - rejects: 0
  - files: `tests/fixtures/face/personA_1.jpg`, `tests/fixtures/face/personA_2.jpg`,
    `tests/fixtures/face/personB.jpg`, `tests/fixtures/face/README.md` (append a
    new section — do not remove the existing `portrait.jpg` section)
  - notes: All three are already identified and licence-verified by Q1's
    research (`memory/research/2026-07-26-f6-same-person-fixture-pair.md`) —
    this task fetches and commits, it does not re-research. Locate each via
    Wikimedia Commons (same method the research used: search, then read that
    specific file's `imageinfo&extmetadata` for `LicenseShortName`/`UsageTerms`
    naming *that* file, not a category-level inference) and re-confirm the
    licence field before committing, since a filename can drift between
    research and build. **Unlike `portrait.jpg`, these ARE committed** — all
    three are Public domain/CC0 with no redistribution restriction, so this
    follows the voice-fixtures precedent (`tests/fixtures/voiceprint/`'s
    `.gitignore` exception), not `portrait.jpg`'s fetch-only one.
    The README addition documents, per file: source URL, credit/custodian
    (LOC / NARA / MET), date, licence field exactly as Commons states it, and
    — critically — **why A1/A2 is an honest same-person pair and not a
    derived probe** (different photographer, different negative, 9-year gap,
    different custodial chain — the reasoning already written in the Q1
    research file, restated at the fixture so a future reader does not have
    to find the research doc to trust the test).
  - done-criteria:
    - Save as a throwaway script (e.g. `scripts/_check_face_fixtures.py` or
      inline in the test suite) rather than forcing this into a `-c`
      one-liner:
      ```python
      import pathlib
      import cv2
      import mediapipe as mp
      from voicelock.facedetect import load_landmarker

      lm = load_landmarker()
      base = pathlib.Path("tests/fixtures/face")
      for i, name in enumerate(("personA_1.jpg", "personA_2.jpg", "personB.jpg"), start=1):
          img = cv2.imread(str(base / name))
          assert img is not None, f"{name}: image missing"
          rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
          frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
          result = lm.detect_for_video(frame, i)
          assert len(result.face_landmarks) == 1, f"{name}: expected 1 face, got {len(result.face_landmarks)}"
          assert len(result.face_landmarks[0]) == 478, f"{name}: expected 478 landmarks"
      print("ok")
      ```
      run as `uv run python scripts/_check_face_fixtures.py` → exit 0. The
      intent that must hold: **each of the three fixtures, loaded through the
      vendored `face_landmarker` bundle, detects exactly one face with all
      478 landmarks.** (Deleting the throwaway script after Task 2 is fine —
      Task 3's own §5 cmd 3 re-proves detection through `faceprint.embed_file`
      anyway, so this check does not need to survive as permanent surface.)
    - `uv run python -c "import pathlib; t = pathlib.Path('tests/fixtures/face/README.md').read_text(encoding='utf-8'); assert 'personA_1.jpg' in t and 'personA_2.jpg' in t and 'personB.jpg' in t; assert 'Public domain' in t or 'CC0' in t"` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, count unchanged)

- [ ] **Task 3** — `faceprint.py`: alignment, embed/compare, cutoffs, convert-not-refuse, mutation-sensitive test
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/faceprint.py` (new), `tests/test_faceprint.py` (new)
  - notes: The largest single task — the module itself. Mirror
    `voiceprint.py`'s shape wherever Q3/Q4/Q8 say to, and deliberately
    **diverge** wherever the inherited blind spot (memory spine item 4) says
    to.
    - **Detection + alignment** (decision 2 above): a lazily-loaded, module-cached
      `IMAGE`-mode `FaceLandmarker` from `models/face_landmarker/face_landmarker.task`
      (a second instance from `facedetect.py`'s `VIDEO`-mode one — do not
      share or import `facedetect.py`'s cached landmarker). Build the 5-point
      YuNet-shaped row exactly per
      `memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md`: eye
      centres = midpoint of 33+133 and 263+362, nose tip = 4, mouth corners =
      61 and 291, confidence hardcoded 1.0. Feed through
      `cv2.FaceRecognizerSF.alignCrop` then `.feature()`. No face detected →
      `NoFaceError` (mirrors `NeedMoreAudioError`'s role). Several faces → if
      MediaPipe's config surfaces more than one, pick the largest by
      bounding-box area of the detected landmarks and say so in a comment
      (Q6) — do not silently take the first.
    - **Convert, never refuse** (§1 blind spot, §4 constraint): resize/convert
      whatever resolution arrives — no `ValueError` on an unexpected frame
      shape anywhere in this module. The code must explain why, **mentioning
      `voiceprint` by name** (§5 cmd 5's literal check), e.g. a module
      docstring line: "Unlike `voiceprint.py`'s `load_wav`, which refuses
      non-16kHz-mono audio because `capture.py` pins the microphone to one
      format, camera frames legitimately vary in resolution — this module
      converts rather than refusing."
    - **Public API** (names fixed by §5's pinned commands — do not rename):
      `embed_frame(frame: np.ndarray) -> np.ndarray` (raises `NoFaceError`),
      `embed_file(path) -> np.ndarray` (`cv2.imread` + `embed_frame`),
      `compare(a: np.ndarray, b: np.ndarray) -> float` (raw **L2** distance —
      decision 1; NOT a `(distance, band)` tuple, cmd 3 uses the return value
      as a bare float), `ACCEPT_CUTOFF = 1.128`, `REJECT_CUTOFF = 1.128`
      (decision 1 — do NOT set these to different values). Additionally add,
      for Task 4 to consume (not pinned by spec, but needed for the Booth to
      mirror F3's shape): `band_for(distance) -> str`, `default_reference_path()`
      → `~/.voicelock/faceprint.ref` (Q3), `set_reference(frames: list[np.ndarray],
      path=None)` averaging `REFERENCE_TAKES = 3` frames (Q4 — note in the
      docstring the honest asymmetry Q4 names: three frames seconds apart are
      far more correlated than F3's three separate spoken sentences, so this
      buys less noise-reduction than voice's average did), `load_reference(path=None)`,
      `NoReferenceError`.
    - **Mutation-sensitivity test** (§5 cmd 6): write a dummy embedder (e.g.
      mean-pixel-value tiled into a vector, zero face modelling) and assert
      it does **not** separate personA_1/personA_2 from personB at
      `ACCEPT_CUTOFF`/`REJECT_CUTOFF` — proving the real test's pass is load-
      bearing on the actual SFace model, not on the assertion being trivially
      satisfiable (same method as F5.5 §5 cmd 4, adapted to images).
  - done-criteria: **the FULL list from `spec.md`'s Verification section is
    NOT owed here** (this is not the last task) — the following, drawn from
    §5 cmds 2–6 (verbatim where the spec gives an exact command, plan-authored
    where it doesn't):
    - §5 cmd 3 — verbatim, exit 0:
      ```
      uv run python -c "from voicelock.faceprint import embed_file, compare, ACCEPT_CUTOFF, REJECT_CUTOFF; d_same = compare(embed_file('tests/fixtures/face/personA_1.jpg'), embed_file('tests/fixtures/face/personA_2.jpg')); d_diff = compare(embed_file('tests/fixtures/face/personA_1.jpg'), embed_file('tests/fixtures/face/personB.jpg')); assert d_same <= ACCEPT_CUTOFF, d_same; assert d_diff >= REJECT_CUTOFF, d_diff"
      ```
    - §5 cmd 4 — verbatim, exit 0:
      ```
      uv run python -c "import numpy as np; from voicelock.faceprint import embed_frame; import cv2; img720 = cv2.imread('tests/fixtures/face/personA_1.jpg'); img720 = cv2.resize(img720, (1280, 720)); img320 = cv2.resize(img720, (320, 240)); assert embed_frame(img720) is not None; assert embed_frame(img320) is not None"
      ```
    - §5 cmd 5 — verbatim, exit 0:
      ```
      uv run python -c "import inspect; from voicelock import faceprint as f; s = inspect.getsource(f); assert 'voiceprint' in s, 'the module does not record WHY it converts where voiceprint.py refuses'"
      ```
    - §5 cmd 2, plan-authored (no exact command pinned in spec — mirror
      `tests/test_voiceprint.py::test_model_loads_offline_from_vendored_path`'s
      socket-blocking technique as a new pytest test, e.g.
      `test_faceprint_loads_offline_from_vendored_path`): `uv run pytest tests/test_faceprint.py -k offline` → exit 0
    - §5 cmd 6, plan-authored (mutation-sensitivity, mirroring F5.5 §5 cmd 4's
      pattern as a new pytest test, e.g. `test_dummy_embedder_fails_to_separate`):
      `uv run pytest tests/test_faceprint.py -k mutation` → exit 0
    - `ACCEPT_CUTOFF == 1.128 and REJECT_CUTOFF == 1.128` (the anti-drift pin
      for decision 1): `uv run python -c "from voicelock.faceprint import ACCEPT_CUTOFF, REJECT_CUTOFF; assert ACCEPT_CUTOFF == 1.128; assert REJECT_CUTOFF == 1.128, 'REJECT_CUTOFF must equal ACCEPT_CUTOFF per the 2026-07-27 decision — do not invent a second threshold'"` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises from F5.5's 124, 0 failed)

- [ ] **Task 4** — Booth bridge: `~/.voicelock/faceprint.ref`, on-demand set/compare/reset
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/facedetect.py` (additive only — see decision 3),
    `src/voicelock/app.py`, `tests/test_booth_api.py`
  - notes: **`facedetect.py` change is additive and minimal** (decision 3):
    add a `last_frame` field to `FaceEngine`, set to the raw (pre-overlay)
    frame each `_loop` tick, plus a small accessor. Do not touch
    `process_frame`'s crop/mirror/overlay order, `start`/`stop`'s
    halt→join→release sequence, or `pacing_delay` — those are the non-goal's
    "camera lifecycle or preview pipeline" and stay exactly as F5 left them.
    `app.py`'s `BoothApi` gains three methods, distinctly named from the
    existing voice ones (`set_reference`/`compare`/`reset_reference` are
    already taken):
    - `set_face_reference()` — banks `self.face.last_frame` as one of
      `REFERENCE_TAKES` (3) reference frames via `faceprint.embed_frame`
      (validating before accepting, same pattern as `set_reference`'s voice
      counterpart); on the 3rd, calls `faceprint.set_reference(frames,
      path=self.face_ref_path)`. A frame with no face raises `NoFaceError` —
      surface as `{"ok": False, "error": "no_face"}`, progress not advanced,
      mirroring `need_more_audio`'s shape.
    - `compare_face()` — embeds `self.face.last_frame`, compares to the
      loaded reference via `faceprint.compare` + `faceprint.band_for`, returns
      `{"ok": True, "distance": ..., "band": ...}`. No reference yet →
      `{"ok": False, "error": "no_reference"}`. No face in the current frame →
      `{"ok": False, "error": "no_face"}`. **Called on a low fixed interval
      from JS** (decision 4) — never from inside `FaceEngine`'s 30 fps loop.
    - `reset_face_reference()` — clears `self._face_reference_takes` and
      unlinks `self.face_ref_path`, mirroring `reset_reference`.
    - `self.face_ref_path` defaults to `faceprint.default_reference_path()`,
      injectable via `BoothApi.__init__` the same way `ref_path` already is.
  - done-criteria:
    - New tests in `tests/test_booth_api.py`, mirroring
      `test_bridge_set_reference_then_compare_separates_speakers` /
      `test_bridge_compare_without_reference` / `test_bridge_reset_reference_clears_a_set_reference`'s
      shape but for faces (inject a fake/stub `FaceEngine` exposing
      `last_frame` set to a loaded fixture array, no real camera): at least
      one test proving `set_face_reference` → `compare_face` separates
      personA vs personB through the real `faceprint` module end to end via
      the bridge, and one test each for the `no_reference` and `no_face`
      edges. Exact test names set by the implementor; the intent (bridge
      methods work, both edges surfaced without crashing) is what is pinned
      here.
    - `uv run python -c "import inspect; from voicelock.app import BoothApi; for name in ('set_face_reference','compare_face','reset_face_reference'): assert hasattr(BoothApi, name), name"` → exit 0
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (count rises, 0 failed)

- [ ] **Task 5** — Booth UI: faceprint panel + liveness-honesty copy *(LAST task — full spec Verification)*
  - state: TODO
  - rejects: 0
  - files: `src/voicelock/ui/index.html`
  - notes: Mirror the existing `.voiceprint`/`#voiceprint-panel` block (Q8)
    almost verbatim — a `.faceprint`/`#faceprint-panel` block: 3-band meter
    (`#fp-distance`, `#fp-meter`, `#fp-needle`), "Set face reference" /
    "Reset" buttons, take-progress dots, a hint line — placed beside the
    existing `.face-wrap` disk. Wire buttons to `call('set_face_reference')` /
    `call('reset_face_reference')`; wire a `setInterval` (decision 4, e.g.
    every 1000 ms, only while `recording` is true and a face reference
    exists) calling `call('compare_face')` to refresh the meter. **Page holds
    no face-match state of its own** — Python computes distance + band, JS
    only renders them (same guardrail the voiceprint panel already follows).
    **Liveness-honesty copy (§6, §5 cmd 7):** visible text on this panel (not
    buried in a comment) stating plainly that this is a face **match**, not a
    liveness check — e.g. "matches a face — does not prove a live person;
    liveness arrives in F8." The exact wording is free; it must contain the
    words the Gate checks for.
  - done-criteria: **the FULL list from `spec.md`'s Verification section**, namely —
    - `uv run ruff check .` → exit 0
    - `uv run pytest` → exit 0 (0 failed, ≥124 passing, count risen by Tasks 3–4's new tests)
    - §5 cmd 1 — SFace model + licence present → exit 0
    - §5 cmd 2 — faceprint loads/embeds offline → exit 0
    - §5 cmd 3 — same face close, different face far → exit 0
    - §5 cmd 4 — convert-not-refuse at two resolutions → exit 0
    - §5 cmd 5 — the justification mentions `voiceprint` → exit 0
    - §5 cmd 6 — the mutation-sensitivity proof → exit 0
    - §5 cmd 7 — verbatim, exit 0:
      ```
      uv run python -c "import pathlib; t = pathlib.Path('src/voicelock/ui/index.html').read_text(encoding='utf-8'); assert 'liveness' in t.lower() and ('match' in t.lower()), 'the faceprint panel does not disclose match-not-liveness'"
      ```
    - §5 cmd 8 — **manual check, required (Q9).** Human points the camera at
      their own face with a reference set, confirms the meter reads
      **accept**; then holds up a different face (a photo, or a second
      person) and confirms **reject**. Attested by the human at the
      feature-end checkpoint — this is the only live-camera evidence for the
      same-face half of this feature (Q1's fixtures are two static
      photographs, never a live capture).

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in spec §1 gets recorded in `.out-of-scope/` and is never built.

# F6 — Faceprint on screen · Task 3 BLOCKED — needs human input

**Session date: 2026-07-27.** Task 3 is built and almost entirely passing.
One spec-pinned verification command cannot be satisfied by an honest
implementation, on evidence, not on a hunch. Stopped per Mode 3's rule
rather than reinterpreted unsupervised.

## What's built and passing

`src/voicelock/faceprint.py` (new) and `tests/test_faceprint.py` (new, 14
tests). Public API matches `plan.md`'s pinned shape: `embed_frame`,
`embed_file`, `compare` (raw L2), `band_for`, `set_reference`,
`load_reference`, `default_reference_path`, `ACCEPT_CUTOFF`/`REJECT_CUTOFF`
(both `1.128`), `NoFaceError`, `NoReferenceError`.

Verified this session:
- **§5 cmd 3 (verbatim)** → exit 0. Real numbers on the committed fixtures:
  same-person (A1↔A2) **0.727** L2; different-person **1.315** (A1↔B) and
  **1.345** (A2↔B) — both comfortably on the correct side of the `1.128`
  cutoff, consistent with the Q7 research's earlier measurement (0.73 /
  1.31–1.34) on the same alignment scheme.
- **§5 cmd 5 (verbatim)** → exit 0. The module docstring names `voiceprint`
  and explains why this module converts where `voiceprint.py` refuses.
- **§5 cmd 2** (plan-authored, `pytest -k offline`) → exit 0.
  `test_faceprint_loads_offline_from_vendored_path` blocks `socket.getaddrinfo`
  and forces a fresh load of both vendored models.
- **§5 cmd 6** (plan-authored, `pytest -k mutation`) → exit 0.
  `test_dummy_embedder_fails_to_separate_mutation_check`: a mean-pixel-value
  "embedder" with zero face modelling does NOT reproduce the real
  separation — proving the real test's pass is load-bearing on the SFace
  model, not on the assertion being trivially satisfiable.
- **Cutoff anti-drift pin** (`ACCEPT_CUTOFF == REJECT_CUTOFF == 1.128`) →
  exit 0.
- `uv run ruff check .` → exit 0.
- `uv run pytest` → **138 passed** (up from 124, 0 failed) — the full suite,
  not just the new file.
- Also covered, beyond the pinned commands, because the guardrail on
  unexercised branches applies to the several-faces path (Q6) too:
  `test_several_faces_picks_largest_by_bbox_area` and
  `test_no_face_returns_none` exercise `_detect_largest_face` directly via a
  stub landmarker (deterministic, no dependence on a real 2-face fixture,
  which this repo doesn't have).

## What's blocked

**§5 cmd 4, verbatim:**
```
uv run python -c "import numpy as np; from voicelock.faceprint import embed_frame; import cv2; img720 = cv2.imread('tests/fixtures/face/personA_1.jpg'); img720 = cv2.resize(img720, (1280, 720)); img320 = cv2.resize(img720, (320, 240)); assert embed_frame(img720) is not None; assert embed_frame(img320) is not None"
```
Actual exit code: **1**. `embed_frame(img720)` raises `NoFaceError` — the
command never reaches `img320`.

**Root cause, confirmed by elimination, not assumed:**
- `personA_1.jpg` is **816×1024 (portrait)**. `cv2.resize(img, (1280, 720))`
  with no aspect-ratio preservation **stretches it non-uniformly** into a
  landscape frame — a ~1.57x horizontal stretch combined with a ~0.70x
  vertical squash, net face distortion ~2.24x.
- This is **not** an implementation bug: the exact same distorted array run
  through F5's own already-shipped, completely unmodified
  `voicelock.facedetect.load_landmarker()` (same model, `VIDEO` mode) also
  detects **0 faces**.
- It is **not** a confidence-threshold issue: `min_face_detection_confidence`
  swept from 0.5 down to 0.01 made no difference (still 0 faces).
- It **is** the aspect distortion specifically: resizing the SAME source
  image to a **comparable scale but preserving aspect ratio** (574×720,
  scaled by height like the 720 target) detects the face fine, on the same
  model, same code path.

**Conclusion:** no code change inside `embed_frame` can fix this. By the
time a frame reaches `embed_frame`, the squashing has already happened in
the test's own setup code — there is no way to recover an already-destroyed
aspect ratio from pixel content alone. `embed_frame` is behaving exactly as
designed: it does not raise on frame *shape* (no `ValueError`, the
convert-never-refuse contract §4 requires), it genuinely attempts detection
on whatever pixels arrive, and correctly raises `NoFaceError` when no face
is actually findable — which, for this specific distorted array, is the
honest answer. Forcing a pass here would require either fabricating an
embedding for a frame with no detectable face (forbidden — this is exactly
the "never invent identity values" territory) or silently changing the
pinned command (forbidden without a spec amendment).

This is a **Mode 3 "rule you cannot follow literally"** under
`constitution/universal.md`'s [Modes] section: "STOP — set the task
`BLOCKED` and report; unsupervised interpretation is forbidden."

## Recommendation (not applied — needs your decision)

The likely fix is a **spec amendment to §5 cmd 4**, not a code change.
Options, roughly in order of how little they change the command's intent:
1. **Aspect-preserving resize.** Replace the two hard-coded target sizes
   with aspect-preserving resizes at comparable scales (e.g. resize by
   height to 720, then by height to 240 — mirroring `facedetect.py`'s own
   discipline of centre-cropping to square *before* any resize, never
   stretching non-uniformly). Confirmed above to detect fine.
2. **Different fixture.** Use a landscape or square-ish source image for
   this specific check (none of F6's three committed fixtures are; all are
   portrait 19th-century photographs) — bigger change, touches fixture
   provenance again.
3. **A real camera frame is never non-uniformly stretched** — the sensor's
   aspect is fixed; only its resolution changes. So option 1 is also the
   more *realistic* test of "convert never refuse" — a genuine camera
   frame at any `TARGET_FPS`/resolution never arrives pre-distorted the way
   this command's resize distorts a still photo.

I have not touched `spec.md` — that's your call, not mine to make
unsupervised (Modes 3–4 rule; a spec amendment needs fresh box-2 approval
per `constitution/universal.md`'s [Modes] rule on raising/changing a spec
mid-feature).

## Pending guardrail (unrelated, carried from Task 2, still unresolved)

**Proposed, awaiting approval** (learn scan, F6 Task 2, 2026-07-27):

> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. It carries face-tracker state (an ROI prior) across
> `detect_for_video` calls, so feeding it unrelated stills back-to-back
> silently drops the face (0 detections, no error) on any frame after the
> first whose face falls outside the prior frame's tracked region. Use a
> fresh instance per unrelated image, or `IMAGE` mode outright, for any
> script/test that compares or checks multiple independent photographs.
> `warn` · expires: 2027-01-31
> - _Evidence:_ F6 Task 2 (2026-07-27) — see that task's build commit
>   (`4c8f880`) and `tests/fixtures/face/README.md`'s "Detection re-verified"
>   section for the full reordering-based confirmation.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

## next_action

**STOP for human input.** Two things need you:
1. **Task 3's blocker** — approve one of the §5 cmd 4 recommendations
   above (or a different fix), so Task 3 can finish and move to `REVIEW`.
   Nothing else in Task 3 is in question.
2. **The pending guardrail** — approve, decline, or amend.

Once §5 cmd 4 is resolved, the remaining work is small: re-run the fixed
command, confirm exit 0, set Task 3 `REVIEW`, and spawn the clean-context
verifier — unattended again from there per Mode 3.

## Commits

Session base → head: `dd4a975` → (Task 3 DOING commit `3885e79`, then this
BLOCKED state + the full build, committed together below). Nothing pushed.

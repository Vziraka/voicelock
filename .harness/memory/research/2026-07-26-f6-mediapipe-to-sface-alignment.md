# Research — does hand-built YuNet-format alignment from MediaPipe landmarks work? (Q7)

Date: 2026-07-26 · Asked by: F6 spec.md Q7 — an architecture question under the
universal [Uncertainty] rule, so it required verification before approval, not
just a recommendation.

**Finding: yes.** `cv2.FaceRecognizerSF.alignCrop` accepts a hand-built
detection row derived from MediaPipe's 478 landmarks (no YuNet vendoring
needed), and the resulting SFace embeddings cleanly separate the F6 fixture
pair. Both parts of Q7's stated verification bar are met.

## Setup (scratchpad only, nothing committed)

- SFace ONNX weights (`face_recognition_sface_2021dec.onnx`, opencv_zoo,
  38.7 MB) downloaded to the session scratchpad for this test only — vendoring
  it into `src/voicelock/models/sface/` is F6 build work gated on Q2's licence
  task, not done here.
- Fixtures: the three images from
  `2026-07-26-f6-same-person-fixture-pair.md` (Douglass A1/A2,
  MET elderly-man B).
- MediaPipe landmark indices used (5-point YuNet-shaped row, all from the
  478-point `FrameResult.landmarks` F5 already returns, unflipped/full-frame
  normalized): eye centers as the midpoint of each eye's outer+inner corner
  (33+133 → point 1, 263+362 → point 2), nose tip = index 4, mouth corners =
  61 (point 4) and 291 (point 5). Confidence field hardcoded to 1.0 (SFace
  does not use it).

## Test 1 — which point order does `alignCrop` expect?

Two orderings were tried (point-1/point-2 swapped, mouth corners swapped to
match) and both fed through `alignCrop` on `douglass_a1.jpg`, producing two
112×112 crops, visually inspected:

- **Order `[33/133 eye, 263/362 eye, nose(4), mouth(61), mouth(291)]`** →
  upright, correctly centred, eyes level — a well-aligned frontal crop.
- **The reversed order** → visibly wrong: face off-centre, smaller, rotated —
  clearly not what SFace's training-time alignment template expects.

The correct order matches the commonly documented YuNet row layout
(`x_re, y_re, x_le, y_le, x_nt, y_nt, x_rcm, y_rcm, x_lcm, y_lcm`) where "re"
(right eye) is the eye that appears on the **left side of a front-facing
image** — i.e., indices 33/133 first. This was confirmed empirically (by
looking at the aligned output), not assumed from the naming.

## Test 2 — does the resulting embedding actually separate the fixtures?

Ran `feature()` on the correctly-aligned crops for A1, A2, B and compared with
`FaceRecognizerSF.match`:

| Pair | Relationship | Cosine similarity (OpenCV accept ≥ 0.363) | L2 distance (OpenCV accept ≤ 1.128) |
|---|---|---|---|
| A1–A2 | same person (Douglass, 1870 vs c.1879) | **0.7325** | **0.7314** |
| A1–B | different person | 0.1358 | 1.3147 |
| A2–B | different person | 0.0970 | 1.3439 |

Both metrics separate cleanly and by a wide margin — the same-person score
sits well inside OpenCV's own published accept region on both metrics, the
different-person scores sit well outside it on both. No threshold-straddling
ambiguity in this single measurement.

## What this resolves, and what it doesn't

- **Resolves Q7 outright**: no YuNet vendoring is needed; the hand-built row
  works and the embedding discriminates. This also removes Q7's stated
  fallback (vendor YuNet, reopening Q2 for a second asset) — it is not needed.
- **Feeds Q5** (measured cutoffs vs. vendor default) with real numbers, but
  is not a substitute for Q5's own measurement: this is one same-person pair
  and one different-person subject (two comparisons), not a fixture-set-sized
  calibration. The margin here is wide enough that adopting OpenCV's published
  thresholds outright (rather than re-deriving new ones from two data points)
  is defensible — that judgment call belongs to Q5, not this file.
- Does **not** test multiple faces in-frame, extreme pose, or low-resolution
  input — those are Q6's concerns (on-demand computation, several-faces
  handling), not this alignment question.

## Nothing was committed

The SFace ONNX file and both aligned-crop test images exist only in
`…/scratchpad/f6fixtures/`. `src/voicelock/models/sface/` does not exist yet;
creating it (with `LICENSE`/`NOTICE`) is F6 implementation work gated on Q2.

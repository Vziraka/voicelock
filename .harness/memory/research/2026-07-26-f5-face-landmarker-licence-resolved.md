# Research — `face_landmarker.task` licence: RESOLVED as Apache-2.0

Date: 2026-07-26 · Asked by: F5 Task 2 · **Supersedes**
`2026-07-26-f5-face-landmarker-licence.md` (which recorded `unconfirmed`).

Findings files are never edited, so this is a new file rather than a correction
to that one. Its eight negative results all still stand — they are why this
question needed a human at all.

**Answer: Apache License 2.0**, established from Google's own model cards for
the three models the bundle repackages.

## The evidence that closed it

The earlier file's blocker was that the three model cards — the single most
likely place the licence is written — are **image-only PDFs** with no
extractable text, and no OCR exists in this environment.

**A human opened them and reported the Apache-2.0 licence link (2026-07-26).**

That report was then corroborated mechanically rather than taken on trust. PDF
**link annotations are plain objects even when the page content is a flat
scanned image**, so every `/URI` action was extracted from all three files:

| Model card | `apache.org/licenses/LICENSE-2.0.html` present? |
|---|---|
| `Model Card MediaPipe Face Mesh V2.pdf` (3 476 420 B) | **yes** |
| `MediaPipe BlazeFace Model Card (Short Range).pdf` (434 425 B) | **yes** |
| `Model Card Blendshape V2.pdf` (2 324 099 B) | **yes** |

Checked 2026-07-26, stdlib-only extraction, no new dependency.

These three cards correspond 1:1 to the three models inside the bundle:

| Card | Bundle entry |
|---|---|
| FaceMesh V2 | `face_landmarks_detector.tflite` (2 553 590 B) — the 478-landmark model |
| BlazeFace (short range) | `face_detector.tflite` (229 746 B) |
| Blendshape V2 | `face_blendshapes.tflite` (955 312 B) |

So provenance is established **per asset, on its own terms** — the standard
`spec.md` §4 sets — rather than inherited from the project that references the
files.

## What is deliberately NOT claimed

- **The `.task` file does not carry a licence.** It embeds none: all four zip
  entries were scanned for `Apache` / `licen` / `copyright` with zero hits, and
  the TFLite metadata `license` field is unpopulated. The licence comes from the
  model cards; the vendored `NOTICE` says exactly that rather than implying the
  artifact is self-describing.
- **Only the link annotations were machine-verified**, not the sentence around
  them. The human read the cards in context and reported it as the licence;
  that human reading is part of the evidence, and is recorded as such.
- **A second independent avenue is still unread** — the Kaggle model page's
  licence field (`https://www.kaggle.com/models/mediapipe/face-landmarks-detection`),
  which is JS-gated and returns a 5 663-byte shell to any non-browser client.
  Noted for anyone wanting belt-and-braces confirmation.

## Why the earlier `unconfirmed` was still the right call

The TECH-PICK's working assumption was *"it is Apache-2.0 throughout"*
(`memory/decisions.md`, 2026-07-26) — which turned out **correct**, but was not
*established* by anything reachable without a human. Had the STOP condition been
waived on that assumption, the repo would have vendored a 3.7 MB artifact on the
strength of reasoning the spec explicitly rules insufficient, and the same
reasoning would have carried into Task 3's fixture — where `spec.md` §4's cited
counter-example shows it fails outright (MediaPipe's own face_detector sample
ships a **Pixabay**-licensed image, whose terms restrict redistributing
unaltered copies).

The check cost one human minute and converted an assumption into a fact. That is
the STOP condition working, not misfiring.

## The vendored artifact

- URL: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`
- Fetched: 2026-07-26 (build time only — nothing in `src/` fetches at runtime)
- Size: **3 758 596 bytes** · SHA-256
  `64184E229B263107BC2B804C6625DB1341FF2BB731874B0BCC2FE6544E0BC9FF`
- Licence: **Apache-2.0**, per the three model cards above

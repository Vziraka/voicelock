# Research — what licence governs `face_landmarker.task`?

Date: 2026-07-26 · Asked by: F5 Task 2 (vendor the Face Landmarker bundle)
Question: **Is the MediaPipe Face Landmarker model bundle under a permissive
licence that allows committing it into this repo?**

**Answer: `unconfirmed`.** No primary source states a licence for the model
weights. Under the research skill's "Gray zone = FAIL" rule and `spec.md` §4's
explicit teeth, Task 2 is `BLOCKED` pending a human decision. The bundle was
**not** committed.

## Playbook note

Loaded `formats/source-playbooks/library-evaluation.md` as required before
searching. It targets **liveness** (release dates, download counts), which was
already settled for `mediapipe` at TECH-PICK time and is not the question here.
Recorded per the skill's "if none fits, say so and name the sources you'll use
instead": sources used were, strongest first — the artifact itself, the
distribution bucket, the vendor's own docs and model cards, the vendor's
distribution channel (Kaggle), and the vendor's source repo.

## The artifact (fetched 2026-07-26)

- URL: `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`
- Size: **3 758 596 bytes** (clears `spec.md` §5's `> 1_000_000` assertion)
- SHA-256: `64184E229B263107BC2B804C6625DB1341FF2BB731874B0BCC2FE6544E0BC9FF`
- Container: a **zip** of four files —
  `face_detector.tflite` (229 746 B), `face_landmarks_detector.tflite`
  (2 553 590 B), `face_blendshapes.tflite` (955 312 B),
  `geometry_pipeline_metadata_landmarks.binarypb` (19 376 B).
  These map 1:1 onto the three model cards the docs page links.

## Claims, each with its source and date

1. **The bundle contains no licence text of its own.** — evidence: every zip
   entry was scanned for `Apache` / `licen` / `copyright` (case-insensitive);
   **zero hits in all four entries**. TFLite metadata has a `license` field in
   its schema; it is not populated here. Checked 2026-07-26.
2. **The hosting bucket publishes no licence file.** — `.../LICENSE` probed at
   three paths (bucket root, the model's `latest/` dir, the `face_landmarker/`
   dir): all **HTTP 404**. Checked 2026-07-26.
3. **The official Face Landmarker guide states no licence for the model.** —
   `https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker`
   (and its `/python` page). The only licence statement on the page is
   *"the content of this page is licensed under the Creative Commons
   Attribution 4.0 License, and code samples are licensed under the Apache 2.0
   License"* — which governs **page content and code samples**, not model
   weights. Fetched 2026-07-26.
4. **The three model cards are image-only PDFs; their licence sections could
   not be read.** — `MediaPipe BlazeFace Model Card (Short Range).pdf`
   (434 425 B), `Model Card MediaPipe Face Mesh V2.pdf` (3 476 420 B),
   `Model Card Blendshape V2.pdf` (2 324 099 B), all downloaded successfully
   from `storage.googleapis.com/mediapipe-assets/`. Stdlib text extraction
   returned image data, not text; no `/Font` or `/ToUnicode` objects were found.
   No OCR is available in this environment. **This is the single most likely
   place the answer is written, and it is unread — see "How a human settles
   this in 60 seconds" below.** Checked 2026-07-26.
5. **The `mediapipe` 0.10.35 wheel is Apache-2.0 but ships no models.** —
   `dist-info/METADATA`: `License: Apache 2.0`,
   `Classifier: License :: OSI Approved :: Apache Software License`. Its
   `licenses/LICENSE` (12 331 B) is unmodified Apache-2.0 text with **no**
   model/weights carve-out (0 hits for `model`, `weight`, `trained`,
   `dataset`). `RECORD` lists **zero** `.tflite` / `.task` / `.binarypb` files.
   So the wheel's licence cannot be transferred to a separately-downloaded
   bundle. Checked 2026-07-26 against the installed package.
6. **The `google-ai-edge/mediapipe` repo is Apache-2.0 but does not ship these
   weights.** — `gh api repos/google-ai-edge/mediapipe/license` →
   `Apache-2.0`; `mediapipe/modules/face_landmark/` contains only `.pbtxt`
   graph configs, `BUILD` and `README.md` — **no `.tflite`**; a code search for
   `extension:task` in that repo returns **0** results. The repo's licence
   therefore covers graph definitions and code, not the GCS-hosted weights.
   Checked 2026-07-26.
7. **Kaggle's model page could not be read.** —
   `https://www.kaggle.com/models/mediapipe/face-landmarks-detection` returns a
   5 663-byte JS shell with no licence field in the raw HTML; the
   `.../face-landmarker` URL is **404**. Kaggle model pages normally carry an
   explicit licence field, so this remains a live avenue for a human with a
   browser. Checked 2026-07-26.
8. **Web search produced only the insufficient evidence class.** — results
   asserting "Apache 2.0" trace back to Apache-2.0 headers in *code samples*
   and to the framework being open source. `spec.md` §4 rules exactly this out:
   *"it comes from Google's MediaPipe project" is NOT sufficient evidence*.
   Checked 2026-07-26.

## Where this contradicted the first instinct

The instinct — and the TECH-PICK's own working assumption, recorded as *"it is
Apache-2.0 throughout"* (`memory/decisions.md`, 2026-07-26) — was that the
bundle is plainly Apache-2.0. That is **not** established by any primary source
found here. The framework is Apache-2.0; the wheel is Apache-2.0; the repo is
Apache-2.0; the weights are distributed from a bucket that says nothing at all.
The TECH-PICK itself flagged this honestly under accepted limits (*"the `.task`
bundle's exact byte size and its own licence text are `unconfirmed` at pick
time … and must be checked at download, before vendoring"*), and the spec built
the STOP condition on top of it. The check ran; it did not clear.

This is also precisely the failure mode `spec.md` §4 warned about in the
neighbouring fixture decision: MediaPipe's own face_detector sample notebook
ships a **Pixabay**-licensed image, not an Apache-2.0 one — so "the vendor
references it" never establishes the vendor licensed it.

## How a human settles this in 60 seconds

The three model cards are already downloaded and are almost certainly where the
licence is stated — they just need eyes rather than a parser. They are at:

```
%TEMP%\claude\c--Users-zvent-Downloads-Testing-V5\d4b97a37-f1bc-43b4-9528-abf29fe81c9c\scratchpad\
  facemeshv2.pdf   blazeface.pdf   blendshape.pdf
```

Open them and read the licence / terms-of-use section. Failing that, the Kaggle
model page in a real browser shows a licence field.

## The quarantined artifact

The bundle was downloaded but **not committed**, and was moved out of the repo
tree to prevent an accidental `git add -A` from vendoring it. It sits at
`…\scratchpad\face_landmarker.task` with the SHA-256 above. Re-fetching is one
command; nothing is lost by the quarantine.

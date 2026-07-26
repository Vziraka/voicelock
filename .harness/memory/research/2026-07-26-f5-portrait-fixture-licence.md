# Research — what licence governs MediaPipe's `portrait.jpg` test image?

Date: 2026-07-26 · Asked by: F5 Task 3 (vendor the face fixture)
Question: **Can `portrait.jpg` be committed into this repo as a test fixture?**

**Answer: NO. Its licence is explicitly restrictive.** Task 3 is `BLOCKED`. The
image was downloaded, its metadata read, and the file then **deleted**; it was
never placed in the repo tree and never committed.

This is not a gray zone like Task 2's. It is a clear, quoted prohibition.

## The finding

The image carries its own copyright notice in EXIF:

- **Artist (EXIF 315):** `Pete Souza`
- **Copyright (EXIF 33432), quoted in full:**

  > This photograph is provided by THE WHITE HOUSE as a courtesy and may be
  > printed by the subject(s) in the photograph for personal use only. The
  > photograph may not be manipulated in any way and may not otherwise be
  > reproduced, disseminated or broadcast, without the written permission of the
  > White House Photo Office. This photograph may not be used in any commercial
  > or political materials, advertisements, emails, products, promotions that in
  > any way suggests approval or endorsement of the President, the First Family,
  > or the White House.

Checked 2026-07-26 by reading the EXIF of the file served from
`https://storage.googleapis.com/mediapipe-assets/portrait.jpg`
(176 561 bytes, 820×1024 JPEG, SHA-256
`A6F11EFAA834706DB23F275B6115058FA87FC7F14362681E6ABE14E82749DE3E`).

**Committing a fixture into a repo is "reproducing and disseminating" it**, and
a test suite that loads and processes it is arguably "manipulating" it. Both are
prohibited without written permission from the White House Photo Office. The
notice also confines permitted printing to *the subjects of the photograph*,
which we are not.

## Why "it's in Google's Apache-2.0 repo" does not rescue it

The repo's `mediapipe/tasks/testdata/vision/BUILD` declares
`licenses = ["notice"],  # Apache 2.0` and lists `"portrait.jpg"` among its
data files. That is **not** sufficient, for two independent reasons:

1. **The repo does not actually ship the image.** Listing the 34 entries of
   `mediapipe/tasks/testdata/vision/` via the GitHub API returns the *expected
   outputs* — `portrait_expected_face_landmarks.pbtxt`,
   `portrait_expected_blendshapes.pbtxt`, `portrait_expected_detection.pbtxt`,
   `portrait_expected_face_geometry.pbtxt` and rotated/full-range variants —
   and **no `.jpg` files at all**. The image is fetched from the
   `mediapipe-assets` bucket at build time. Exactly the same pattern as the
   model bundle in Task 2. Checked 2026-07-26.
2. **A package-level Bazel licence declaration cannot override an asset's own
   embedded copyright notice.** The specific notice travels with the file and is
   more specific than a directory-wide default.

## This is precisely the case `spec.md` §4 predicted

The spec warned, before any of this was checked:

> **That check has teeth — "it comes from Google's MediaPipe project" is NOT
> sufficient evidence.** … MediaPipe's own face_detector sample notebook does
> not ship an Apache-2.0 asset at all — it downloads
> `https://i.imgur.com/Vu2Nqwb.jpeg`, credited in the notebook to **Pixabay**,
> whose licence restricts redistributing images unaltered. Committing a fixture
> into a repo *is* redistributing it unaltered.

The prediction was right about the failure *mode* and understated the severity:
the canonical `portrait.jpg` is not merely awkwardly licensed like a Pixabay
image, it is a White House press photograph with an explicit no-redistribution
clause.

It is also a textbook instance of the guardrail the human approved earlier the
same day (`project.md`, `[Approval]`, per-asset licence provenance): the
framework is Apache-2.0, the repo is Apache-2.0, the BUILD file says Apache-2.0
— and the asset is not.

## What is lost, and what the options are

`spec.md` §5 wanted the real-model test to assert against MediaPipe's
**published expected landmarks** for this exact image
(`portrait_expected_face_landmarks.pbtxt`), which is a vendor reference rather
than a self-generated expectation. Those `.pbtxt` files **are** in the
Apache-2.0 repo and are freely usable — but they are only meaningful paired
with the image they describe. Losing the image loses the vendor-reference
assertion; a different face image can still prove "the bundle detects a real
face with 478 landmarks", which is the line `spec.md` §5 actually calls "the
line that separates 'the bundle is on disk' from 'the bundle works'".

All routes forward are **human-only** decisions (`spec.md` §4 forbids silent
substitution; §5's fallback is a Verification-section rewrite — a spec
amendment):

1. **Substitute a permissively-licensed face image** (e.g. CC0 / public domain
   from Wikimedia Commons, licence verified per-asset on its own page). Keeps a
   real-model test with a real face; loses the vendor-reference assertion.
2. **Take the spec's stated fallback** — replace the real-model test with an
   explicitly written limitation in the Verification section. Honest, but the
   vendored bundle then has no test proving it actually detects anything.
3. **Seek written permission from the White House Photo Office.** Complete, and
   disproportionate for a local learning project.

Not options: the repo owner's own face (forbidden by `spec.md` §4 —
biometrics in version control, and a withdrawable fixture is a test that breaks
later), and fabricating landmarks as a silent proxy (forbidden by §5).

## Artifact disposition

Downloaded to a scratchpad outside the repo, metadata extracted, then
**deleted**. `tests/fixtures/face/` was never created. `git status` clean; the
image appears nowhere in git history.

# Face fixtures

Fixtures for the F5 face-detection tests. **Read the first section before
assuming a clean checkout can run the whole suite** — one file here is
deliberately *not* committed, which is unlike every other fixture in this repo.

## `portrait.jpg` — NOT COMMITTED. You must fetch it.

```
curl -o tests/fixtures/face/portrait.jpg https://storage.googleapis.com/mediapipe-assets/portrait.jpg
```

PowerShell:

```
Invoke-WebRequest -Uri https://storage.googleapis.com/mediapipe-assets/portrait.jpg -OutFile tests\fixtures\face\portrait.jpg
```

| | |
|---|---|
| Source | `https://storage.googleapis.com/mediapipe-assets/portrait.jpg` |
| Size | 176 561 bytes (820×1024 JPEG) |
| SHA-256 | `A6F11EFAA834706DB23F275B6115058FA87FC7F14362681E6ABE14E82749DE3E` |
| Fetched | 2026-07-26 |
| Git | **ignored** — see `.gitignore` |

### Why it is not committed

The file carries its own copyright notice in EXIF. `Artist` is `Pete Souza`, and
the `Copyright` field reads, in full:

> This photograph is provided by THE WHITE HOUSE as a courtesy and may be
> printed by the subject(s) in the photograph for personal use only. The
> photograph may not be manipulated in any way and may not otherwise be
> reproduced, disseminated or broadcast, without the written permission of the
> White House Photo Office. This photograph may not be used in any commercial or
> political materials, advertisements, emails, products, promotions that in any
> way suggests approval or endorsement of the President, the First Family, or
> the White House.

Committing it into git **is** reproducing and disseminating it, and git history
is effectively permanent. Note also that the "personal use only" permission is
granted to **the subject(s) of the photograph** — it is not a general permission
for personal projects. Keeping a working copy on your own machine is a different
act from publishing one in a repository, and that is the line this arrangement
draws (human decision, 2026-07-26).

**Being in Google's Apache-2.0 repo does not license it.** MediaPipe's
`mediapipe/tasks/testdata/vision/BUILD` lists `portrait.jpg` under
`licenses = ["notice"]`, but the repository ships only the
`portrait_expected_*.pbtxt` **outputs** — there is no `.jpg` in that directory at
all — and a package-level Bazel declaration cannot override an asset's own
embedded notice.

Full investigation, including the alternatives that were researched and
rejected: `.harness/memory/research/2026-07-26-f5-portrait-fixture-licence.md`
and `…-f5-fixture-replacement-candidates.md`.

### What happens if you don't fetch it

The real-model test **skips**, with an explicit reason pointing here — it never
fails silently and never substitutes fabricated landmarks. But the harness Gate
pins a separate presence check, so **the Gate will fail** until the file is
fetched. That is deliberate: a skipping test must not be able to turn the Gate
green.

### This inverts the precedent set by the voice fixtures

`.gitignore` carries `!tests/fixtures/voiceprint/*.wav` with the comment
"committed test fixtures are the exception (Gate needs them on a clean
checkout)". F3 committed its fixtures precisely so a fresh clone could verify
itself. `portrait.jpg` is the first asset this repo's Gate needs but cannot
ship. It is a real, disclosed cost of keeping this particular image.

## `portrait_expected_face_landmarks.pbtxt` — committed

The **vendor reference**: MediaPipe's own published expected output for
`portrait.jpg`.

| | |
|---|---|
| Source | `google-ai-edge/mediapipe`, `mediapipe/tasks/testdata/vision/` (branch `master`) |
| Size | 29 637 bytes |
| Licence | **Apache-2.0** — the repository's own licence, and unlike the photograph this file genuinely ships there |
| Fetched | 2026-07-26 |

This is why `portrait.jpg` was kept rather than replaced with a freely-licensed
photograph: MediaPipe publishes expected landmarks for this image **and no
other**, so it is the only fixture against which the test can assert Google's
own coordinates instead of a self-generated expectation.

Format is a plain protobuf text dump of `NormalizedLandmarkList` — 478
`landmark { x: … y: … }` blocks, parseable with a regex and no new dependency.
(The published reference carries `x` and `y` only, no `z`.)

**Measured agreement**, 2026-07-26, vendored bundle vs. this reference:

```
reference landmarks: 478   detected: 478
max abs diff: 0.005645     mean: 0.001051   (normalized coords)
```

Max deviation is ~4.6 px on the 820 px-wide image. A test tolerance must sit
above that measured maximum, not at it — the numbers above are what a future
change to the model or preprocessing would be caught against.

## What these fixtures prove, and what they don't

They prove the **vendored bundle detects a real human face** and produces the
478 landmarks Google publishes for that face — the line between "the model file
is on disk" and "the model works".

They prove **nothing about identity**. No faceprint, no embedding, no match
distance; that is F6. And they say nothing about whether the *camera* works —
that is covered by the human-attested live check in F5's Verification section.

The repo owner's own face is deliberately **not** a fixture here: committing
one's biometrics is a poor default, and a fixture that can be withdrawn later is
a test that breaks later. The owner's face is proven live at runtime, never in
git.

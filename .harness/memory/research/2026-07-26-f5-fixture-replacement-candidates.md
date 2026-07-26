# Research — a permissively-licensed replacement for the `portrait.jpg` fixture

Date: 2026-07-26 · Asked by: F5 Task 3, after
`2026-07-26-f5-portrait-fixture-licence.md` established that MediaPipe's
`portrait.jpg` may **not** be redistributed.

**Recommendation: `-Elderly Man; Full Face- MET 37.14.52.jpg` — CC0 1.0, a
circa-1850 daguerreotype donated by the Metropolitan Museum of Art.** Verified
to produce 1 face / 478 landmarks with the vendored bundle.

Adopting it is a **spec amendment** (human-only): `spec.md` §4 names
`portrait.jpg` explicitly and forbids substituting another image without
escalation, and §5's pinned commands reference the filename.

## Method

Wikimedia Commons' API exposes **per-file** licence metadata
(`prop=imageinfo&iiprop=extmetadata`), which is a primary source that names the
asset — exactly the standard `project.md`'s new `[Approval]` guardrail requires,
and the standard MediaPipe's own bucket failed. Candidates were then run
through the **vendored** bundle to confirm they are actually detectable, since a
correctly-licensed image that the model cannot see is useless as a fixture.

## Candidates

### 1. `-Elderly Man; Full Face- MET 37.14.52.jpg` — **RECOMMENDED**

| Field | Value (from the Commons API, 2026-07-26) |
|---|---|
| `LicenseShortName` | **CC0** |
| `UsageTerms` | Creative Commons Zero, Public Domain Dedication |
| `Artist` | Albert Southworth / Josiah Johnson Hawes / Southworth & Hawes |
| `Credit` | Donated to Wikimedia Commons as part of a project by the **Metropolitan Museum of Art**, under its Image and Data Resources Open Access Policy |
| `DateTimeOriginal` | circa **1850** |
| Size | 602×768 |
| URL | `https://upload.wikimedia.org/wikipedia/commons/8/82/-Elderly_Man%3B_Full_Face-_MET_37.14.52.jpg` |

Detection against the vendored bundle: **faces=1, landmarks=478.**

Why this one:

- **CC0 is the strongest possible position** — no attribution condition, no
  redistribution restriction, nothing to get wrong later.
- **Two independent licence sources agree** — the Commons file page and the
  Met's Open Access Policy — and the Met is the institution that owns the
  object, not a third party passing it along.
- **No living subject.** The sitter and both photographers died in the 19th
  century. This matters here beyond politeness: `spec.md` §4 rejected the repo
  owner's own face partly because *"a biometrics project committing its owner's
  face as a permanent fixture is a poor default"*. That reasoning applies to any
  identifiable living person, CC0 or not. A c.1850 daguerreotype sidesteps it
  entirely.
- **Stable.** A museum open-access donation is not going to be withdrawn, so the
  fixture will not become a test that breaks later — the other property §4 asked
  for.
- It is a **full-face** portrait, which is what the detector wants.

### 2. `'head shot' JRCDP.jpg` — usable fallback

CC0, `Artist` KiketonPR, `Credit` "Own work", 1215×1215, dated 2013-06-17.
Detection: **faces=1, landmarks=478.** Licence is clean; the reservation is that
it depicts an **identifiable living person**, which the argument above makes
undesirable for a biometrics repo even when legally permitted.

### 3. `Ed Fallon Head Shot 2013.jpg` — **REJECTED**

CC0 on its face, but the metadata does not hold together: `Artist` is "Liz
George" while `Credit` reads *"Ed Fallon sent me, Zach Heffernen, the picture
personally via email."* The uploader is neither the photographer nor, on that
account, demonstrably the rights holder — a licence-laundering smell. Rejected
on exactly the principle that produced this whole investigation: the source must
establish the right, not merely assert it.

## What is lost by not using `portrait.jpg`

`spec.md` §5 wanted the real-model test to assert against MediaPipe's
**published** expected landmarks for that specific image
(`portrait_expected_face_landmarks.pbtxt`) — a vendor reference rather than a
self-generated expectation. Those `.pbtxt` files are in the Apache-2.0 repo and
are freely usable, but they only mean anything paired with the image they
describe, so the vendor-reference assertion goes away.

What survives is the assertion `spec.md` §5 itself calls the important one —
*"the line that separates 'the bundle is on disk' from 'the bundle works'"*: a
real face is found with **478** landmarks, and a plain-colour image yields
**none**. Both were confirmed against the vendored bundle before recommending
this (plain grey 640×480 → faces=0).

The spec anticipates disclosing exactly this kind of shortfall: *"if it is not
practical, say so in the fixture README rather than silently asserting less."*

## Nothing was committed

Both candidates were downloaded to a scratchpad outside the repo for the
detection test. `tests/fixtures/face/` does not exist. No image is in git.

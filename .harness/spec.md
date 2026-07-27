# Spec: F6 — Faceprint on screen

Feature: Feature 6 from `roadmap.md`

> **DRAFT — parked at the approval gate.** Written unattended as F5.5's Mode 4
> tail (2026-07-26). It has **not** been approved and must not be planned or
> built. Every open question is embedded below as a clarification marker with my
> recommended answer attached; the universal [Startup] rule makes an unresolved
> marker physically block approval. **Ten markers** — nine numbered questions
> plus §6's mandatory Mode 2+ blind-spot question — and Q1 and Q7 are the ones
> that change what gets built.

## 0. Approval gate

- [ ] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [ ] Approved by human

- **Mode:** *(left blank deliberately — the human sets this at approval. Mode 4
  is mechanically unlocked: 33 verdict files record Mode 3 or Mode 4, and the
  F3/F4/F5/F5.5 completion reports are in git history. Unlocked is not the same
  as appropriate — see the note under §6.)*

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Compute the **Faceprint** — a face embedding — and show a live match distance
against a stored face reference, in the Booth, coloured accept / borderline /
reject. **Not wired into any lock.** This is the visual analog of F3, and it is
deliberately the same shape: a diagnostic you can watch work before it becomes
a key in F7.

Three things must be true when this is done:

1. **`faceprint.py` exists and computes a real embedding** from a detected face,
   using OpenCV's SFace through the `opencv-contrib-python` F5 already declares,
   with the ONNX weights vendored offline beside `models/ecapa/` and
   `models/face_landmarker/`. No network at runtime.
2. **A stored face reference can be set, compared against, and reset**, and the
   Booth shows the resulting distance in a three-band meter — the same
   accept/borderline/reject vocabulary F3 established, with cutoffs **measured
   on this repo's fixtures and pinned**, not copied from a vendor default.
3. **Same face reads close, a different face reads far**, proven by a test whose
   assertion would break if the speaker— sorry, the *face* model were removed.
   F5.5 just spent a task fixing exactly this failure in the voice path; F6 must
   not reproduce it.

Demo: point the camera at your face with a reference set → the meter reads
accept; hold up a photo of someone else → it reads reject.

> **Inherited blind spot — read before writing a line of `faceprint.py`.**
> F5.5's `voiceprint.py` **refuses** audio that is not 16 kHz mono, and that is
> correct there **only** because `capture.py` pins the microphone to exactly one
> rate and one channel. **F6 must not copy that pattern.** Camera frames
> legitimately vary in resolution, and a faceprint module that raises on an
> unexpected frame size would reject valid input. Where the voice path refuses,
> the face path **converts** — resize, crop, align. This is a §4 constraint, not
> advice, and §5 pins a check for it.

## 2. Grilling record — ambiguity scan

**Status: DRAFT — NOT CLEAR.** Ten markers remain — the nine numbered questions
listed by category below, plus §6's mandatory Mode 2+ blind-spot question. Batch-grilled per the `spec` skill's unattended-drafting rule:
there was no human in the session to interview one question at a time, so each
question carries my recommended answer and the human resolves them at approval.

| Category | Verdict | State |
|---|---|---|
| Functional scope & behavior | **Partial** | Q4 (how many frames make a reference), Q8 (UI surface) |
| Domain & data model | **Partial** | Q3 (where the face reference is stored, and in what format) |
| Interaction & UX flow | **Partial** | Q8 (does the Booth mirror F3's panel exactly) |
| Non-functional (perf, security) | **Partial** | Q6 (per-frame budget — SFace on every frame, or on demand) |
| Integration & dependencies | **Partial** | Q2 (is a TECH-PICK owed for a vendored model file when no new package enters `pyproject.toml`), Q7 (how SFace gets its aligned crop) |
| Edge cases & failure modes | **Partial** | Q6 (no face / several faces), and the §1 blind-spot rule (convert, never refuse) |
| Completion signals | **Partial** | Q1 (what fixtures make the assertions real), Q5 (measured cutoffs vs vendor default), Q9 (manual check) |
| Terminology (matches `CONTEXT.md`) | **Clear** | Uses **Faceprint** and **FaceView** exactly as the glossary defines them. No new terms. |

### The questions

**Q1 — fixtures: where does a second face come from, and is a same-face pair
even honest?** This is the feature's hardest question and `roadmap.md` flags it
explicitly: F5 commits **one** face (`portrait.jpg`, and even that is
fetched-not-committed because it is a White House press photograph).

F6 needs two assertions with teeth: *same person → close* and *different person
→ far*. The different-person half is easy — the CC0 MET daguerreotype already
researched and detection-verified in
`memory/research/2026-07-26-f5-fixture-replacement-candidates.md` is a clean
face B. **The same-person half is the trap.** A photo cannot be windowed the way
F3 windowed its audio, so the tempting move is to derive a second "probe" from
the same image by cropping, rescaling or re-encoding it — and that would be
**exactly** the vacuous test F5.5 was created to remove. Note also that run 2's
recorded fix direction for the voice case (assert on a byte-disjoint pair) was
**drafted and then disproved by measurement** during F5.5's grilling; do not
import that idea here by analogy.

[NEEDS-CLARIFICATION: Which fixture arrangement? **My recommendation: (a) find a
genuine second photograph of the same person under a CC0/public-domain licence —
Wikimedia has many subjects with multiple independent PD portraits — and commit
face A1, A2 and B, all CC0, all licence-established per-asset. If a real A1/A2
pair cannot be found, take option (b): commit only the different-person
assertion, and state in the fixture README and at the test that no automated
same-face proof exists, with the same-face case proven only by the human's live
manual check.** Option (c) — deriving A2 from A1 by crop/rescale/re-encode — is
possible but must then be named for what it is: a proof of encoding invariance,
not of identity, and I recommend against it on F5.5's evidence. This needs a
`research` run before the spec is approved; it is a licence question as much as
a technical one.]

**Q2 — is a TECH-PICK owed?** `opencv-contrib-python` is already approved and
declared (F5), so `cv2.FaceRecognizerSF` needs no new package. But the SFace
**ONNX weights** are a new vendored third-party asset, and `project.md`'s first
guardrail requires the licence to be established from a source naming *that
asset* — the artifact's own metadata first.

[NEEDS-CLARIFICATION: Does vendoring a model file with no new package entry
require the full `formats/TECH-PICK.md` walkthrough, or only the per-asset
licence establishment? **My recommendation: skip the full TECH-PICK (no
alternative is being chosen — SFace was already named in F5's TECH-PICK and is
reachable through an approved package) but run the per-asset licence check in
full, as its own task, with the same escalation rule that fired twice in F5.
Nothing gets committed to `models/sface/` until that task produces a non-stub
`LICENSE` and `NOTICE` recording the evidence chain.**]

**Q3 — where does the face reference live, and in what format?**

[NEEDS-CLARIFICATION: **My recommendation: `~/.voicelock/faceprint.ref`, a
plaintext `np.save` sibling of `voiceprint.ref`, mirroring F3 exactly** — same
`default_reference_path()` shape, same `load_reference` / `_save_reference`
pattern. It is not a secret (an embedding is not a key until F7 makes it one),
and putting it beside the voice reference keeps one obvious place for
"diagnostic state that is not the vault".]

**Q4 — how many frames make a face reference?** F3 averages
`REFERENCE_TAKES = 3` separate utterances.

[NEEDS-CLARIFICATION: **My recommendation: average N frames captured over a
short window (N = 3, mirroring F3) rather than a single frame**, re-normalized
the same way, because a single frame bakes in one blink/expression. Note the
honest asymmetry: three *frames* seconds apart are far more correlated than
three separate spoken sentences, so this buys less than it does for voice —
which is an argument for saying so in the code, not for skipping it.]

**Q5 — cutoffs: measure or adopt?** OpenCV publishes canonical SFace thresholds
(cosine ≈ 0.363, L2 ≈ 1.128). F3's precedent is to *measure* cutoffs on this
repo's own fixtures and pin them as module constants.

[NEEDS-CLARIFICATION: **My recommendation: measure on this repo's fixtures and
pin, following F3, and record the measurement in the fixture README the way
`tests/fixtures/voiceprint/README.md` does** — but state the vendor's published
threshold alongside it, so a large divergence is visible rather than silently
overridden. This depends on Q1: with only one face pair there is not enough
data to pin honestly, and the spec should then adopt the vendor threshold and
say so.]

**Q6 — per-frame cost, no face, and several faces.** SFace inference on every
frame at `TARGET_FPS = 30` may not fit the 33 ms budget F5 measured itself
against (`facedetect.py` uses ~10 ms/frame today).

[NEEDS-CLARIFICATION: **My recommendation: compute the faceprint on demand, not
on every frame** — the Booth's meter updates on a button press or at a low fixed
interval, so the preview stays at 30 fps regardless. For **no face detected**,
raise a `NoFaceError` analogous to `NeedMoreAudioError`, surfaced as Booth copy,
not a crash. For **several faces**, use the largest by bounding-box area and say
so in a comment. And per §1's blind spot: an unexpected frame **size** is
converted, never refused.]

**Q7 — how does SFace get its aligned crop?** `cv2.FaceRecognizerSF.alignCrop`
expects a detection row in **YuNet's** format — a bounding box plus five
specific landmarks (both eye centres, nose tip, both mouth corners). This repo
detects with **MediaPipe**, which returns 478 landmarks in a different scheme.
This is an architecture question, so it is a must-answer under the universal
[Uncertainty] rule.

[NEEDS-CLARIFICATION: **My recommendation: derive the five YuNet-shaped points
from the 478 MediaPipe landmarks `FrameResult.landmarks` already carries
(unflipped, full-frame normalized — F5 deliberately returned all 478 for exactly
this) and build the detection row ourselves, rather than vendoring YuNet as a
third model.** It reuses what exists and adds no asset. **But it must be
verified before approval, not assumed:** confirm that `alignCrop` accepts a
hand-built row and that the resulting embedding actually separates the fixtures.
If it does not, the fallback is to vendor YuNet too — which reopens Q2's licence
work for a second asset.]

**Q8 — Booth surface.** F3 added a voiceprint panel: a 3-band meter, "Set
reference", "Reset".

[NEEDS-CLARIFICATION: **My recommendation: mirror F3's panel exactly** — a
faceprint panel with the same three-band meter, "Set face reference" and
"Reset", placed beside the existing FaceView disk. Same colours, same
vocabulary, and **the page keeps no state the engine owns** (`project.md`
guardrail): Python computes the distance and the band, JS renders them.]

**Q9 — manual check.** F5.5 was the first feature with none, because it had no
live surface. F6 has one.

[NEEDS-CLARIFICATION: **My recommendation: the manual check returns and is
required** — a human points the camera at their own face with a reference set
and confirms accept, then holds up a different face and confirms reject. F6's
whole point is a thing you watch work, and Q1 may leave the same-face case with
**no** automated proof at all, which would make the live check the only evidence
for half the feature.]

## 3. Non-goals

- **Any lock wiring.** The faceprint does not derive a key, does not touch
  `vault.py`, and does not seal anything. That is **F7**.
- **Liveness, anti-spoof, deepfake detection.** Holding a photo up to the camera
  is expected to *pass* the face match at F6 — that is precisely why F8 exists.
  Nothing in this feature may claim otherwise, in code, copy or comment.
- **Re-pinning any voice constant.** `ACCEPT_CUTOFF`, `REJECT_CUTOFF` and
  `CORRECTION_RADIUS` are F3/F4 measurements and stay untouched.
- **Changing `facedetect.py`'s camera lifecycle or preview pipeline.** F6
  consumes `FrameResult.landmarks`; it does not re-cut the F5 composite.
- **Replacing `portrait.jpg`.** Whatever Q1 resolves to, F5's
  fetched-not-committed arrangement for that file stands unless the human
  explicitly retires it.
- **The `voicelock` → new-name rename.** Still parked (`roadmap.md`).

## 4. Constraints

- **Offline-only.** No network at runtime; the SFace weights load from a local
  path exactly as `models/ecapa/` and `models/face_landmarker/` do.
- **No new package in `pyproject.toml`** on the recommended path — SFace comes
  through the already-approved `opencv-contrib-python`. If Q7 forces YuNet,
  that is still a vendored asset, not a package.
- **Per-asset licence.** Nothing enters `src/voicelock/models/sface/` until its
  licence is established from a source naming *that file* — embedded metadata
  first (`project.md` guardrail 1). A non-stub `LICENSE` and `NOTICE` recording
  the evidence chain ship with it.
- **Convert, never refuse.** The faceprint path accepts whatever frame the
  camera gives it and resizes/crops/aligns as needed. Refusing an unexpected
  frame size is forbidden — see §1's blind spot and §5's check.
- **Python owns the state; JS renders.** No face state in the page.
- **No unexercised surface.** Every branch added ships with a test that drives
  it (`project.md` guardrail), and every test must fail if the behaviour it
  claims to cover is removed (`project.md` guardrail) — F6's own §5 makes the
  second one runnable rather than aspirational.

## 5. Verification — definition of done (runnable)

*(Draft. The feature-specific commands below are the shape the Gate will run;
several cannot be finalised until Q1, Q5 and Q7 are resolved, and the ones that
depend on a fixture name are marked. At Mode 2+ every command needs pinned
expectations — filling those in is part of resolving the questions.)*

**Standing** (the regression net — `project.md`'s Gate commands):

- `uv run ruff check .` → exit 0.
- `uv run pytest` → exit 0. Reference: **124 passing** at the end of F5.5; the
  count rises by F6's tests and must not fall.

**Feature-specific:**

1. **The vendored SFace model is present and licence-documented.**
   `uv run python -c "import pathlib; d = pathlib.Path('src/voicelock/models/sface'); assert d.is_dir(); assert (d / 'LICENSE').stat().st_size > 200; assert (d / 'NOTICE').stat().st_size > 200"`
   → exit 0. Mirrors the standing check F5 pinned for `models/face_landmarker/`.
2. **The faceprint is computed offline** — no DNS resolution during a load +
   embed, the same socket-blocking pattern
   `tests/test_voiceprint.py::test_model_loads_offline_from_vendored_path` uses.
   → exit 0.
3. **Same face close, different face far** — the assertions Q1 decides. Pinned
   expectations pending Q1/Q5.
4. **The face path CONVERTS rather than refuses** — the F5.5 blind-spot
   mitigation, made runnable: feed the embedder a frame at a resolution the
   camera never produces (e.g. 1280×720 and 320×240) and assert it returns an
   embedding instead of raising.
   `uv run python -c "import numpy as np; from voicelock import faceprint; ..."`
   → exit 0. **This is the command that stops F6 inheriting the wrong half of
   F5.5.**
5. **The justification travels with the code**, the converse of F5.5 §6:
   `uv run python -c "import inspect; from voicelock import faceprint as f; s = inspect.getsource(f); assert 'voiceprint' in s, 'the module does not record WHY it converts where voiceprint.py refuses'"`
   → exit 0.
6. **The match test is mutation-sensitive** — F6's own version of F5.5 §5 cmd 4:
   a dummy embedder with no face modelling must **fail** to separate the
   fixtures, proving the real assertion depends on the model. Exact form pending
   Q1.
7. **Manual check** — pending Q9. If required: a human points the camera at
   their own face with a reference set (accept), then at a different face
   (reject), and attests it.

**Out-of-scope default (Modes 3–4):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

**"If every gate passed but the feature were still wrong, what would be wrong?"**

[NEEDS-CLARIFICATION: This is the mandatory Mode 2+ question and it is the
human's to answer at approval — my draft answer is below, but it is not a
resolution.

**My draft answer: the meter would read "accept" for a photograph, and a
watching human would read that as "the face lock works".** F6 computes a face
*match* and nothing else; a printed photo of the enrolled person will score as
accept, by design, until F8 adds liveness. The gates cannot catch this because
the behaviour is correct — the risk is in what the Booth *appears* to claim. The
mitigation I would propose is the same shape as F5.5's: make the honesty
runnable rather than cultural — the faceprint panel carries visible copy saying
this is a match, not a liveness check, and a §5 command asserts that copy exists
in `index.html` so a later UI tidy-up cannot quietly drop it.

A second candidate, if the human prefers a different framing: **Mode choice.**
F5.5 ran at Mode 4 and was suited to it — settled design, no dependencies, no
live surface. F6 is the opposite on every count: a new vendored asset, an
unresolved fixture-licence question, an unverified alignment path (Q7), and a
live demo. **I would not recommend Mode 4 here**; Mode 2 or 3 fits the
uncertainty better. The mode is the human's call and box 2 approves it.]

## 7. What F6 inherits (recorded so it survives the next handoff rewrite)

- **From F5:** the fetched-not-committed fixture arrangement for `portrait.jpg`;
  the vendored-model directory pattern with `LICENSE` + `NOTICE`; `FrameResult`
  carrying **all 478 unflipped landmarks** specifically so this feature can
  consume them; and the two-faces gap that Q1 must close.
- **From F5.5:** the blind spot above — refuse-unexpected-input is correct for a
  pinned source and wrong for a camera — and the harder lesson underneath it,
  that a same-X test built on a derived probe proves the pipeline, not the
  model. F6's Q1 is that lesson arriving one feature early, on purpose.
- **From `project.md`:** the per-asset licence rule (which fired twice in F5, and
  cleared one asset while rejecting another), the no-unexercised-surface rule,
  and the mutation-sensitivity rule that §5 cmd 6 makes runnable.

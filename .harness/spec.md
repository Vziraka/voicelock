# Spec: F6 — Faceprint on screen

Feature: Feature 6 from `roadmap.md`

> **GRILLED AND APPROVED (2026-07-26/27).** Drafted unattended as F5.5's Mode 4
> tail (2026-07-26), then all ten markers — nine numbered questions plus §6's
> mandatory Mode 2+ blind-spot question — were resolved interactively with the
> human on 2026-07-26/27, two (Q1, Q7) backed by dedicated `research` runs
> rather than assumption. See §2 for the resolutions and §0 for the approval
> gate.

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [x] Approved by human

- **Mode: Mode 3 — Spec-to-done.** Set by the human 2026-07-27. Build↔verify
cycles and the feature-end wrap-up run unattended within this feature; the
human is checked in with at the feature-end checkpoint (final-verdict review
  - commit/push approval). Mode 4 was available (mechanically unlocked) but not
  chosen — the human picked Mode 3.

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
   accept/borderline/reject vocabulary F3 established, with cutoffs **adopted
   from OpenCV's published SFace thresholds** (cosine ≥ 0.363, L2 ≤ 1.128) —
   not measured on this repo's fixtures, per Q5: two comparisons is not enough
   data to responsibly derive a custom threshold, unlike F3's many-take voice
   measurement. The code states this reasoning, not just the numbers.
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

**Status: CLEAR.** All ten markers resolved interactively with the human
(2026-07-26/27) — a search for the `NEEDS-CLARIFICATION` token returns zero
hits in this file. Drafted unattended per the `spec` skill's
unattended-drafting rule (each question carried a recommended answer); Q1 and
Q7 were additionally backed by dedicated `research` runs before being put to
the human, rather than resolved from the recommendation alone.


| Category                           | Verdict      | State                                                                                                                                             |
| ---------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Functional scope & behavior        | **Resolved** | Q4 — average 3 frames; Q8 — mirrors F3's panel                                                                                                    |
| Domain & data model                | **Resolved** | Q3 — `~/.voicelock/faceprint.ref`, mirrors `voiceprint.ref`                                                                                       |
| Interaction & UX flow              | **Resolved** | Q8 — mirrors F3's panel exactly                                                                                                                   |
| Non-functional (perf, security)    | **Resolved** | Q6 — on-demand computation, not every frame                                                                                                       |
| Integration & dependencies         | **Resolved** | Q2 — narrower per-asset licence task, no full TECH-PICK; Q7 — hand-built MediaPipe→SFace alignment, verified, no YuNet, `research` run 2026-07-26 |
| Edge cases & failure modes         | **Resolved** | Q6 — `NoFaceError`, largest-face-wins; the §1 blind-spot rule (convert, never refuse)                                                             |
| Completion signals                 | **Resolved** | Q1 — Douglass A1/A2 + MET B; Q5 — vendor thresholds adopted; Q9 — manual check required                                                           |
| Terminology (matches `CONTEXT.md`) | **Clear**    | Uses **Faceprint** and **FaceView** exactly as the glossary defines them. No new terms.                                                           |


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

**RESOLVED (2026-07-26, human-approved).** A genuine, independent same-person
pair was found and verified: `research` run
`memory/research/2026-07-26-f6-same-person-fixture-pair.md` located two
separate 19th-century photographs of Frederick Douglass — **A1**: 1870, George
Francis Schreiber, Library of Congress (LCCN 2004671911); **A2**: c.1879,
photographer unrecorded, National Archives (NARA 558770) — different
photographers, different negatives, different custodial chains, both
`Public domain` per Wikimedia Commons' per-file metadata, both deceased
subjects. **Face B** carries over from F5's research: the CC0 MET daguerreotype
`-Elderly Man; Full Face- MET 37.14.52.jpg`. All three confirmed
faces=1/landmarks=478 against the vendored `face_landmarker.task` bundle. This
is **not** a derived probe (F5.5's failure mode) — A1 and A2 are independent
photographic acts, not a crop/rescale/re-encode of one file. Fixtures A1, A2,
B are to be committed to `tests/fixtures/face/` with a README documenting
provenance and licence, per F5's `LICENSE`/`NOTICE`-adjacent pattern.
Resolved by: `research`.

**Q2 — is a TECH-PICK owed?** `opencv-contrib-python` is already approved and
declared (F5), so `cv2.FaceRecognizerSF` needs no new package. But the SFace
**ONNX weights** are a new vendored third-party asset, and `project.md`'s first
guardrail requires the licence to be established from a source naming *that
asset* — the artifact's own metadata first.

**RESOLVED (2026-07-26, human-approved).** Skip the full `formats/TECH-PICK.md`
walkthrough — no alternative is being chosen, SFace was already named in F5's
TECH-PICK. Run the per-asset licence establishment in full as its own task,
same standard as `project.md`'s guardrail (embedded metadata first, then
per-asset primary sources). Nothing is committed to `models/sface/` until that
task produces a non-stub `LICENSE` and `NOTICE`.

**Q3 — where does the face reference live, and in what format?**

**RESOLVED (2026-07-26, human-approved).** `~/.voicelock/faceprint.ref`, a
plaintext `np.save` sibling of `voiceprint.ref`, mirroring F3 exactly — same
`default_reference_path()` shape, same `load_reference` / `_save_reference`
pattern. Not a secret (an embedding is not a key until F7 makes it one).

**Q4 — how many frames make a face reference?** F3 averages
`REFERENCE_TAKES = 3` separate utterances.

**RESOLVED (2026-07-26, human-approved).** Average 3 frames captured over a
short window (mirroring F3's `REFERENCE_TAKES = 3`), re-normalized the same
way, rather than a single frame — avoids baking in one blink/expression. The
code must note the honest asymmetry: three frames seconds apart are far more
correlated than three separate spoken sentences, so this buys less
noise-reduction than it does for voice.

**Q5 — cutoffs: measure or adopt?** OpenCV publishes canonical SFace thresholds
(cosine ≈ 0.363, L2 ≈ 1.128). F3's precedent is to *measure* cutoffs on this
repo's own fixtures and pin them as module constants.

**RESOLVED (2026-07-26, human-approved).** Adopt OpenCV's published SFace
thresholds as module constants — cosine ≥ 0.363 accept, L2 ≤ 1.128 accept —
rather than measuring a repo-specific cutoff. Reason, per the spec's own
fallback: Q1 yields exactly one same-person pair and one different-person
subject (two comparisons), which is not enough data to responsibly derive a
custom threshold the way F3 measured `ACCEPT_CUTOFF`/`REJECT_CUTOFF` across
many voice takes. The Q7 research measured this exact pair against the vendor
thresholds and found clean separation (same-person 0.7325 cosine / 0.7314 L2;
different-person 0.0970–0.1358 cosine / 1.3147–1.3439 L2) — evidence the vendor
threshold is reasonable here, not a substitute for a proper measurement. The
code and fixture README must state plainly why the vendor default was adopted
rather than a measured one.

**Q6 — per-frame cost, no face, and several faces.** SFace inference on every
frame at `TARGET_FPS = 30` may not fit the 33 ms budget F5 measured itself
against (`facedetect.py` uses ~10 ms/frame today).

**RESOLVED (2026-07-26, human-approved).** Compute the faceprint on demand, not
on every frame — the Booth's meter updates on a button press or at a low fixed
interval, so the preview stays at 30 fps regardless. For **no face detected**,
raise a `NoFaceError` analogous to `NeedMoreAudioError`, surfaced as Booth copy,
not a crash. For **several faces**, use the largest by bounding-box area and say
so in a comment. Per §1's blind spot: an unexpected frame **size** is converted,
never refused.

**Q7 — how does SFace get its aligned crop?** `cv2.FaceRecognizerSF.alignCrop`
expects a detection row in **YuNet's** format — a bounding box plus five
specific landmarks (both eye centres, nose tip, both mouth corners). This repo
detects with **MediaPipe**, which returns 478 landmarks in a different scheme.
This is an architecture question, so it is a must-answer under the universal
[Uncertainty] rule.

**RESOLVED (2026-07-26, human-approved), verified not assumed.** `research` run
`memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md` built the
five YuNet-shaped points from MediaPipe's 478 landmarks (eye centers =
midpoint of outer+inner corner, indices 33/133 and 263/362; nose tip = index
4; mouth corners = 61 and 291), confirmed the point order empirically (the
correct order produces a visibly well-aligned 112×112 crop; the reversed order
visibly does not), and ran real SFace embeddings on the Q1 fixtures: A1–A2
(same person) scored cosine 0.7325 / L2 0.7314 — solidly past OpenCV's own
accept thresholds (cosine ≥ 0.363, L2 ≤ 1.128); A1–B and A2–B (different
person) scored cosine 0.10–0.14 / L2 1.31–1.34 — solidly on the reject side.
**No YuNet vendoring. No second Q2 licence task.** Resolved by: `research`.

**Q8 — Booth surface.** F3 added a voiceprint panel: a 3-band meter, "Set
reference", "Reset".

**RESOLVED (2026-07-26, human-approved).** Mirror F3's panel exactly — a
faceprint panel with the same three-band meter, "Set face reference" and
"Reset", placed beside the existing FaceView disk. Same colours, same
vocabulary. The page keeps no state the engine owns (`project.md` guardrail):
Python computes the distance and the band, JS renders them.

**Q9 — manual check.** F5.5 was the first feature with none, because it had no
live surface. F6 has one.

**RESOLVED (2026-07-26, human-approved).** The manual check is required — a
human points the camera at their own face with a reference set and confirms
accept, then holds up a different face and confirms reject. Even with Q1's
resolved automated fixtures (two static photographs), the live webcam path for
a same-face comparison is exercised by nothing else — this is the only
live-camera evidence for that half of the feature.

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
- **No new package in `pyproject.toml`.** SFace comes through the
already-approved `opencv-contrib-python`. Q7's alignment path (a hand-built
YuNet-shaped row from MediaPipe's existing 478 landmarks) needs no second
vendored model — verified in
`memory/research/2026-07-26-f6-mediapipe-to-sface-alignment.md`.
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

Fixtures (per Q1, committed to `tests/fixtures/face/` with a README
documenting provenance/licence, mirroring `tests/fixtures/voiceprint/README.md`):
`personA_1.jpg` (Douglass, 1870, LOC), `personA_2.jpg` (Douglass, c.1879,
NARA), `personB.jpg` (MET elderly-man daguerreotype).

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
3. **Same face close, different face far**, on the real fixtures:
  `uv run python -c "from voicelock.faceprint import embed_file, compare, ACCEPT_CUTOFF, REJECT_CUTOFF; d_same = compare(embed_file('tests/fixtures/face/personA_1.jpg'), embed_file('tests/fixtures/face/personA_2.jpg')); d_diff = compare(embed_file('tests/fixtures/face/personA_1.jpg'), embed_file('tests/fixtures/face/personB.jpg')); assert d_same <= ACCEPT_CUTOFF, d_same; assert d_diff >= REJECT_CUTOFF, d_diff"`
   → exit 0. (Exact call shape — `embed_file`/`compare` names — is set at
   `/plan`; the assertion intent, not the API, is pinned here.)
4. **The face path CONVERTS rather than refuses** — the F5.5 blind-spot
  mitigation, made runnable: feed the embedder frames at resolutions the
   camera never produces and assert each returns an embedding instead of
   raising.
   `uv run python -c "import numpy as np; from voicelock.faceprint import embed_frame; import cv2; img720 = cv2.imread('tests/fixtures/face/personA_1.jpg'); img720 = cv2.resize(img720, (1280, 720)); img320 = cv2.resize(img720, (320, 240)); assert embed_frame(img720) is not None; assert embed_frame(img320) is not None"`
   → exit 0. **This is the command that stops F6 inheriting the wrong half of
   F5.5.**
5. **The justification travels with the code**, the converse of F5.5 §6:
  `uv run python -c "import inspect; from voicelock import faceprint as f; s = inspect.getsource(f); assert 'voiceprint' in s, 'the module does not record WHY it converts where voiceprint.py refuses'"`
   → exit 0.
6. **The match test is mutation-sensitive** — F6's own version of F5.5 §5 cmd 4:
  a dummy embedder (e.g. one that returns the image's mean pixel value tiled
   into a vector, with no face modelling at all) substituted for the real
   SFace call must **fail** to separate `personA_1`/`personA_2` from
   `personB` at the pinned cutoffs — proving the real test's pass depends on
   the model, not on the assertion being trivially satisfiable. Exact
   mutation-injection shape is set at `/plan`, following F5.5 §5 cmd 4's
   pattern.
7. **The liveness-honesty copy is present** — §6's mitigation, made runnable:
  `uv run python -c "import pathlib; t = pathlib.Path('src/voicelock/ui/index.html').read_text(encoding='utf-8'); assert 'liveness' in t.lower() and ('match' in t.lower()), 'the faceprint panel does not disclose match-not-liveness'"`
   → exit 0. (Exact path/wording set at `/plan`; per `project.md`'s earned
   guardrail this must be a meaning-check, not a brittle exact-string match.)
8. **Manual check — required (Q9).** A human points the camera at their own
  face with a reference set and confirms the meter reads **accept**, then
   holds up a different face (a photo, or a second person) and confirms the
   meter reads **reject**. Attested by the human at the feature-end checkpoint.

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

**"If every gate passed but the feature were still wrong, what would be wrong?"**

**RESOLVED (2026-07-26, human-approved).** The meter would read "accept" for a
photograph held up to the camera, and a watching human would read that as "the
face lock works" — F6 computes a face *match* and nothing else; a printed
photo of the enrolled person scores as accept, by design, until F8 adds
liveness. The gates cannot catch this because the behaviour is correct — the
risk is in what the Booth *appears* to claim. **Mitigation, made runnable
rather than cultural**: the faceprint panel carries visible copy stating this
is a match, not a liveness check, and a §5 Verification command asserts that
copy exists in `index.html` so a later UI tidy-up cannot quietly drop it.

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


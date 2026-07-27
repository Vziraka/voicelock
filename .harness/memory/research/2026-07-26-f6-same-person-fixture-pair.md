# Research — a genuine same-person fixture pair for F6 (Q1)

Date: 2026-07-26 · Asked by: F6 spec.md Q1, resolving the parked marker on
"which fixture arrangement proves same-face-close honestly".

**Finding: a genuine independent same-person pair exists and is verified against
the vendored bundle.** Frederick Douglass, two photographs from two different
sittings nine years apart, both institutionally-sourced public domain:

- **A1** — *"Frederick Douglass, head-and-shoulders portrait, facing right"*,
  George Francis Schreiber, 1870, Library of Congress (LCCN 2004671911).
- **A2** — *"Frederick Douglass, ca. 1879"*, photographer unrecorded, U.S.
  National Archives and Records Administration (NARA 558770).

Different-person **B** carries over unchanged from
`2026-07-26-f5-fixture-replacement-candidates.md`: the MET daguerreotype
`-Elderly Man; Full Face- MET 37.14.52.jpg` (CC0).

## Method

Same standard as the prior research file: Wikimedia Commons' per-file
`imageinfo&extmetadata` API is the primary source that names the specific
asset. Searched `Category:Frederick Douglass` and Commons full-text search
(`srnamespace=6`, filtered to photographs, excluding engravings/paintings/book
scans) for a subject with (a) multiple photographs from demonstrably different
sittings, (b) each with clean per-file public-domain metadata from an
institutional custodian, (c) deceased, sidestepping the living-subject
reservation `2026-07-26-f5-fixture-replacement-candidates.md` raised. Douglass
(1818–1895) is among the most-photographed 19th-century Americans, which is why
the search converged on him quickly — an unusually deep well of independently
custodied sittings.

Candidates were then downloaded to a scratchpad (never committed — see below)
and run through the **vendored** `face_landmarker.task` bundle to confirm
detectability, exactly as the prior research did.

## Candidates verified

| File | Licence (Commons metadata) | Credit / custodian | Date | Size | Detection |
|---|---|---|---|---|---|
| `Frederick Douglass, head-and-shoulders portrait, facing right LCCN2004671911.jpg` | Public domain | Library of Congress | 1870 | 816×1024 | faces=1, landmarks=478 |
| `Frederick Douglass, ca. 1879 - NARA - 558770.tif` | Public domain | U.S. National Archives (NARA) | c. 1879 | 1280×1834 (JPEG derivative used for detection; source is TIFF) | faces=1, landmarks=478 |
| `-Elderly Man; Full Face- MET 37.14.52.jpg` (carried over as face B) | CC0 | Metropolitan Museum of Art | c. 1850 | 602×768 | faces=1, landmarks=478 |

A third Douglass photograph was also confirmed available with clean metadata
if a spare is wanted: `C. M. Battey - Frederick Douglass NMAAHC-2009.37.1.jpg`
(Public domain, Smithsonian NMAAHC, c. 1895, 2561×3000) — not used, recorded in
case A1 or A2 hits an unexpected licence or technical snag later.

## Why this pair is honest, not a repeat of the F5.5 vacuous-test failure

F5.5 existed because a same-X test built on a **derived** probe (crop/rescale/
re-encode of one file, or a sub-window of one audio recording) proves the
pipeline runs, not that the model discriminates identity. A1 and A2 here are
**not derivatives of each other**: different photographer (Schreiber vs.
unrecorded NARA photographer), different negative, different year (1870 vs.
1879, a 9-year gap — different apparent age too), different custodial chain
(Library of Congress vs. National Archives), different file format at source
(JPEG vs. TIFF), different pixel dimensions. There is no operation that turns
one into the other; they are two independent photographic acts of the same
person. This is a materially stronger claim than "same photo session, different
exposure" would have been, and far stronger than a crop/rescale.

## Licence provenance, per-asset

Both Douglass files and the MET file report `LicenseShortName: Public domain` /
`CC0` directly in Commons' per-file `extmetadata`, sourced to the institution
that holds the physical/archival object (LOC, NARA, MET) — not a secondary
aggregator. This is the same evidentiary standard
`2026-07-26-f5-fixture-replacement-candidates.md` used and `project.md`'s
per-asset licence guardrail requires: the source names *that* asset. All three
subjects (Douglass d. 1895, the MET sitter d. mid-late 19th century) are
long deceased, so none carries the living-identifiable-person reservation that
ruled out `'head shot' JRCDP.jpg` in the prior research.

## What was NOT verified here (out of scope for Q1, belongs to Q7/Q2)

This research answers "does a genuine same-person pair exist and can the
detector see both frames" — it does **not** answer whether the SFace embedder
(not yet vendored; Q2 licence work is a separate, still-open task) actually
scores A1↔A2 closer than A1↔B. That distance measurement needs the licensed
SFace ONNX weights in hand and belongs to the tasks that resolve Q5 (cutoffs)
and Q7 (alignment), not to this fixture-existence question. If SFace's
`alignCrop` or the MediaPipe→YuNet landmark conversion (Q7) turns out not to
separate these two particular sittings well (large a pose/quality difference
can happen even for true positives), the fallback is either a different
Douglass pair from the spare above, or Q1's own recommended option (b).

## Nothing was committed

All three images live only in the session scratchpad
(`…/scratchpad/f6fixtures/`), never `git add`ed. `tests/fixtures/face/` does
not exist yet. Committing them is F6 implementation work, gated on the human
approving this fixture choice at the spec's approval gate, exactly as F5's
`portrait.jpg` replacement was.

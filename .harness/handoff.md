# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 3)

**Session date: 2026-07-27.** Task 3 hit a real blocker mid-build, stopped
for human input per Mode 3's rule, was unblocked by an approved spec
amendment, and is now `REVIEW`.

## What happened this session

- Set Task 3 `DOING`, committed alone (`3885e79`) before any build work.
  Base commit for the Gate diff: `dd4a975` (parent of the DOING commit).
- Built `src/voicelock/faceprint.py` and `tests/test_faceprint.py` in full:
  MediaPipe→SFace alignment (the verified 5-point scheme from the Q7
  research), `embed_frame`/`embed_file`/`compare`/`band_for`,
  `set_reference`/`load_reference` (Q3/Q4), convert-never-refuse (no
  `ValueError` on frame shape anywhere), the largest-face-wins several-faces
  handling (Q6, tested via a stub landmarker since no 2-face fixture
  exists), and the mutation-sensitivity test (a dummy mean-pixel embedder
  proven NOT to separate the fixtures).
- **Hit a real blocker on spec.md §5 cmd 4** (convert-not-refuse at two
  resolutions): the pinned command's literal resize (`personA_1.jpg`,
  816×1024 portrait, stretched non-uniformly to 1280×720) produced a frame
  no honest implementation could detect a face in. Confirmed by elimination,
  not assumed: F5's own already-shipped `facedetect.load_landmarker()` also
  finds 0 faces on the identical distorted array; a confidence-threshold
  sweep (0.5→0.01) made no difference; an aspect-preserving resize to a
  comparable scale detects fine on the same model. Per Mode 3's rule on a
  verification command that cannot be followed literally, stopped — set
  Task 3 `BLOCKED`, committed the full evidence (`c5d5d45`), and reported to
  the human rather than reinterpreting unsupervised.
- **Human approved the recommended fix** (aspect-preserving resize,
  mirroring `facedetect.py`'s own centre-crop-before-resize discipline).
  Amended `spec.md` §5 cmd 4 accordingly (re-verified exit 0 BEFORE writing
  it into the spec, so the fix wasn't itself untested), recorded the full
  decision in `memory/decisions.md`, re-scanned `spec.md` for the
  `NEEDS-CLARIFICATION` marker (zero hits, still `CLEAR`), and set Task 3
  back to `REVIEW`. Commit `f6578e2`.
- Ran all of Task 3's done-criteria after the fix:
  - §5 cmd 3 (verbatim) → exit 0. Real numbers: same-person (A1↔A2) 0.727
    L2; different-person 1.315 (A1↔B) / 1.345 (A2↔B) — both against a
    1.128 cutoff.
  - §5 cmd 4 (verbatim, as amended) → exit 0.
  - §5 cmd 5 (verbatim) → exit 0.
  - §5 cmd 2 (`pytest -k offline`) → exit 0.
  - §5 cmd 6 (`pytest -k mutation`) → exit 0.
  - Cutoff anti-drift pin (`ACCEPT_CUTOFF == REJECT_CUTOFF == 1.128`) →
    exit 0.
  - `uv run ruff check .` → exit 0.
  - `uv run pytest` → **138 passed** (up from 124, 0 failed).
- Build commits: `3885e79` (DOING) → `c5d5d45` (full build, discovered
  BLOCKED) → `f6578e2` (spec amendment, UNBLOCKED, REVIEW). The verifier's
  diff base/head below spans all of this — `git diff` shows the net result,
  and this handoff plus `memory/decisions.md` explain the path.

## Failed attempts / lessons

The blocker above is not a rejected implementation attempt — the code was
correct throughout; the spec's own verification command needed a fix.
Whether the underlying pattern (a verification command constructed before
being run against the real model) deserves a `learn` guardrail is a call
for this task's `learn` scan at wrap-up, not decided here.

## next_action

**Mode 3 — spawn the clean-context verifier now.**

- Task: **F6 Task 3** — now `REVIEW`
- Base commit: `dd4a975` (parent of the `DOING` commit `3885e79`)
- Head commit: `f6578e2`
- Verifier: `formats/VERIFIER-PROMPT.md`, used verbatim. Note for the
  verifier: the diff includes a `spec.md` amendment (§5 cmd 4) alongside the
  code — this is expected and human-approved (see `memory/decisions.md`
  2026-07-27 entry "F6 spec AMENDED"), not a scope violation to flag.
- On REJECT: feedback appended to Task 3's log in `plan.md`, task back to
  `TODO`, `rejects` incremented (cap 3).
- On APPROVE: `wrap-up` runs, verdict written, Task 3 → `DONE`, then Task 4
  (Booth bridge) starts unattended per Mode 3.

## Pending guardrail (unrelated, still awaiting a separate decision)

**Proposed, awaiting approval** (learn scan, F6 Task 2, 2026-07-27) — the
human's "yes" this session approved the Task 3 spec-amendment recommendation
specifically, NOT this guardrail, which remains an open, separate question:

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
>   section.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

## Commits

Session base → head: `dd4a975` → `f6578e2` (three commits: `3885e79` DOING,
`c5d5d45` BLOCKED + full build, `f6578e2` spec amendment + REVIEW). This
`handoff.md` write is a fourth, bookkeeping-only commit. Nothing pushed.

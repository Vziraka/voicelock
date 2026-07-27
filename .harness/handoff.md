# F6 — Faceprint on screen · Task 2 WRAP-UP

**Session date: 2026-07-27.** Task 2 built, verified (clean-context
subagent, APPROVE), and wrapped up in this session.

## What happened this session

- Spawned the clean-context verifier (subagent path) with
  `formats/VERIFIER-PROMPT.md` verbatim. Verdict: **GATE PASS, REVIEW
  APPROVE**, no feedback. Full reasoning in
  `memory/verdicts/2026-07-27-F6-T2.json`.
- Wrap-up checklist run in full:
  - **ADR:** none — fails condition 1 (hard to reverse). Committing
    licence-cleared fixtures and fixing a throwaway script bug is not an
    architecture decision.
  - **`learn` scan:** ran. One lesson cleared the bar — see **Pending
    guardrail** below (parked, not written to `project.md`; Mode 3 is
    unattended, no human present to approve).
  - No idea was declined by a human this task — no `.out-of-scope/` entry
    owed.
  - **Roadmap:** unchanged — 3 tasks remain in Feature 6 (Tasks 3–5).
  - **`plan.md`:** Active context, memory spine, and Task 2's line
    refreshed; Task 2 → `DONE`.

## Pending guardrail

**Proposed, awaiting human approval** (learn scan, F6 Task 2, 2026-07-27):

> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. It carries face-tracker state (an ROI prior) across
> `detect_for_video` calls, so feeding it unrelated stills back-to-back
> silently drops the face (0 detections, no error) on any frame after the
> first whose face falls outside the prior frame's tracked region. Use a
> fresh instance per unrelated image, or `IMAGE` mode outright, for any
> script/test that compares or checks multiple independent photographs.
> `warn` · expires: 2027-01-31
> - _Evidence:_ F6 Task 2 (2026-07-27) — the plan's own template script for
>   checking the three face fixtures reused one shared `VIDEO`-mode
>   landmarker via `detect_for_video` across `personA_1.jpg`,
>   `personA_2.jpg`, `personB.jpg`. It found 0 faces on whichever image was
>   NOT first (confirmed by deliberately reordering the images — the
>   failing image changed with call order, ruling out an image-quality
>   explanation). A fresh `load_landmarker()` call per image fixed it
>   immediately, with zero other code changes. Cost ~5 diagnostic tool
>   calls to isolate. Does not affect `facedetect.py` (real, continuous
>   video frames — the mode fits) or `faceprint.py`'s planned embedder
>   (already `IMAGE` mode per `plan.md` decision 2) — the hazard is
>   specific to ad-hoc multi-still test/check scripts, which F7/F8 may
>   also need to write.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

Verdict file records `"lesson": "proposed — pending approval"`. A human
needs to approve (or decline) this diff before it lands in `project.md`.

## next_action

**Mode 3 — the approved spec's Mode line is the standing "go."** This same
session continues to **Task 3** (`faceprint.py`: alignment, embed/compare,
cutoffs, convert-not-refuse, mutation-sensitive test) — Task 2's wrap-up is
the precondition, and it just completed. **The pending guardrail above
needs a human's attention at the next touchpoint** — it does not block
Task 3, which is unrelated code.

## Commits

Session base → head: `4c8f880` → (this wrap-up's commits: verdict file +
`handoff.md` + `plan.md` DONE state). Nothing pushed.

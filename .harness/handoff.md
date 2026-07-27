# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 2)

**Session date: 2026-07-27.** Continuing the same session after Task 1's
wrap-up completed (Mode 3's standing "go").

## What happened this session

- Set Task 2 `DOING`, committed alone (`8123012`) before any build work.
  Base commit for the Gate diff: `a4c3528` (parent of the DOING commit).
- Re-confirmed all three fixture licences directly against Wikimedia
  Commons' per-file `imageinfo&extmetadata` API (not trusted from the Q1
  research file alone, per the task's own instruction that a filename can
  drift between research and build): `personA_1.jpg` (LOC, Public domain),
  `personA_2.jpg` (NARA, Public domain), `personB.jpg` (MET, CC0) — all
  matched the research file's findings exactly.
- Fetched all three from Commons; each committed file's SHA-1 verified
  byte-identical to the `sha1` Commons' own `imageinfo` API reports.
  `personA_2` exists upstream only as a 2094×3000 TIFF — converted to a
  1280×1834 JPEG (resize-only, no crop/rotate/retouch; the specific
  dimensions match the size the Q1 research already proved detects
  reliably).
- **Found and fixed a real bug in the plan's own template script**
  (`scripts/_check_face_fixtures.py`): the plan-authored version reused one
  `VIDEO`-mode `FaceLandmarker` instance across all three images via
  `detect_for_video`. That carries face-tracker state (an ROI prior) across
  calls, so on unrelated stills it silently dropped the face (0 detections,
  no error) on whichever image was NOT first. Confirmed by reordering — the
  failing image changed depending on call order, not on image size/quality.
  Fixed by instantiating a fresh landmarker per image. This does not affect
  Task 3: `faceprint.py`'s own embedder already plans a separate `IMAGE`-mode
  landmarker (decision 2, `plan.md`), which is stateless per call by design.
  Documented in both the build commit and a new `README.md` section (so a
  future reader of the fixtures folder sees the finding, not just the fix).
- Ran Task 2's four done-criteria locally (measurement exception):
  - `uv run python scripts/_check_face_fixtures.py` → `ok`, exit 0 (all
    three fixtures detect 1 face / 478 landmarks through the vendored
    bundle).
  - README content check (`personA_1.jpg`/`personA_2.jpg`/`personB.jpg` +
    `Public domain`/`CC0` present) → exit 0.
  - `uv run ruff check .` → exit 0.
  - `uv run pytest` → 124 passed (unchanged, as expected — Task 2 adds no
    pytest tests, only the throwaway script).
- Build commit: `4c8f880` (fixtures + README + script + `plan.md` Task 2 →
  `REVIEW`).
- `git status` confirmed the diff matches Task 2's declared files exactly;
  `portrait.jpg` remains correctly `.gitignore`d (`git check-ignore`
  confirmed), untouched by this task.

## Failed attempts / lessons

One real fix mid-task, already folded into the build commit and README (see
above) — not a rejected attempt, caught and corrected before Gate. Whether
this rises to a `project.md` guardrail is a call for this task's `learn`
scan at wrap-up, not decided here.

## next_action

**Mode 3 — spawn the clean-context verifier now.**

- Task: **F6 Task 2** — now `REVIEW`
- Base commit: `a4c3528` (parent of the `DOING` commit `8123012`)
- Head commit: `4c8f880`
- Verifier: `formats/VERIFIER-PROMPT.md`, used verbatim
- On REJECT: feedback appended to Task 2's log in `plan.md`, task back to
  `TODO`, `rejects` incremented (cap 3).
- On APPROVE: `wrap-up` runs (including the `learn` scan on the VIDEO-mode
  tracker-state finding above), verdict written, Task 2 → `DONE`, then
  Task 3 (`faceprint.py` itself) starts unattended per Mode 3.

## Commits

Session base → head: `a4c3528` → `4c8f880` (two commits: `8123012` DOING
state, `4c8f880` build + REVIEW state). This `handoff.md` write is a third,
bookkeeping-only commit. Nothing pushed.

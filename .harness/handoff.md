# Handoff — F5 planned, ready for `/implement` Task 1

Session of 2026-07-26 (after the F5 spec was approved). Ran `/plan` for **F5 —
Camera booth**. No code was written and **nothing was installed** —
`pyproject.toml` and `uv.lock` are untouched.

**Entry gate, verified and quoted before planning:** `spec.md`'s Grilling record
says `Status: CLEAR`, a mechanical scan for the bracketed `NEEDS-CLARIFICATION`
colon token returns **zero** hits, and both approval boxes are checked with
`Mode: Mode 3` set by the human.

> F4.5's completion report and the F5 spec-session report were previously here.
> Both are closed; their evidence lives in
> `memory/verdicts/2026-07-26-F4.5-T1/-T2/-T3.json` and in git (`93bc887`, the
> F4.5 feature-end commit; `cf97c77` and `0fdb90e`, the F5 spec and its
> approval).

## What this session produced

- **`plan.md`** — rewritten from F4.5's ledger to **F5's**: 7 tasks, all `TODO`,
  `rejects: 0`, ordered so dependencies come first. Every task has runnable
  done-criteria (Mode 3 requires it for **every** task, not just the last).
- **The module contract is pinned in `plan.md`'s Active context** —
  `FaceEngine` / `FrameResult` / `FaceStatus` / `TARGET_FPS` — because several
  later done-criteria name that surface, so it had to be fixed at plan time
  rather than discovered at build time.

## The task shape

1. Declare `mediapipe` + `opencv-contrib-python` (manifest only)
2. Vendor the `face_landmarker.task` bundle — **licence checked at download**
3. Vendor `portrait.jpg` + provenance README — **licence checked at download**
4. `facedetect.py` — the per-frame composite path, on injectable fakes
5. `facedetect.py` — camera lifecycle: 30 fps worker, drop-don't-queue, release
   tripwire, throughput floor
6. Booth UI — the `<img>` preview in the existing 172 px face disk
7. `BoothApi` wiring + release on window close — **LAST task, FULL §5, including
   the human-attested manual check**

## Judgment calls this session made, so they are reviewable

- **Tasks 2 and 3 are split** (model bundle / face fixture) although both are
  "download an asset and check its licence". They escalate **independently**: a
  blocked fixture must not also block the engine work, and the two remedies are
  different — a bad model licence has no fallback at all, while a bad image
  licence has a spec-amendment path (`spec.md` §4).
- **Tasks 4 and 5 split one new module** into the pure per-frame transform and
  the threaded device lifecycle. They are separately verifiable, and it keeps the
  release/teardown work — the F4.5 defect class — in a diff small enough to
  actually review.
- **The UI task (6) comes before the bridge task (7)**, so the page function
  exists before anything calls it. `_eval`'s existing
  `window.voicelockBooth && …` guard would make the reverse order a silent
  no-op, which is exactly why it would be the wrong order.
- **The throughput floor lives in Task 5, not Task 4**, because the named
  constant it justifies is introduced there — a constant with no caller in
  Task 4 would be precisely the unexercised surface the first earned guardrail
  forbids.
- **`FrameResult.landmarks` returns all 478 while only a subset is drawn.** This
  looks like unexercised surface and is not: `spec.md` §4 requires it (F6/F8
  prefactor) and §5 item (3) pins it with a test. Called out in Task 4's notes so
  a verifier does not reject it under the earned guardrail.

## Open items for the human

1. **A tool mismatch worth resolving before `/implement`.**
   `constitution/project.md`'s Environment section says *"Tool(s): Cursor only ·
   Verifier path: subagent · Signposts: AGENTS.md only"*, and this session ran in
   **Claude Code**, where the harness skills are not installed as slash commands
   (`.claude/skills/` does not exist in this repo — they were invoked by reading
   `.harness/skills/<name>/SKILL.md` directly, the documented fallback).
   That is cosmetic. What is **not** cosmetic: the constitution requires a
   **clean-context verifier**, and this Claude Code session runs under a standing
   instruction not to spawn subagents unless explicitly asked. Under Mode 3 the
   build session is supposed to spawn the template verifier itself. So either:
   - the human explicitly authorizes subagent verification for this feature, or
   - each task's verify step degrades to a **fresh session** — the implement
     session commits state, writes the handoff, and stops, per
     `universal.md`'s BUILD gate ("if the host tool has no clean-context
     subagent, it does NOT self-verify").
   Either is legitimate; the second is slower but needs no decision. **Not
   deciding means the second happens by default.** Re-running `setup` would also
   refresh the stale Environment section.
2. **Two escalations are scheduled, not accidental.** Tasks 2 and 3 will stop and
   ask if either asset's licence does not check out. If the `portrait.jpg`
   licence fails, the spec's remedy (replace the real-model test with a written
   limitation in the Verification section) is a **spec amendment** — human-only,
   needing a fresh box-2 approval.
3. **Nothing else is parked.** No guardrail proposal is outstanding; the third
   earned guardrail from F4.5 was approved and written into `project.md` last
   session.

## Two things carried in from F4.5, both honored in the ledger

- **Task 2's fake-stream shape is the pattern F5's camera fake must copy.** The
  plan states how it reads for a **polling** device: `cv2.VideoCapture` has no
  callback, so `read()` **is** the real path the fake must deliver through, and
  `release()` is the teardown it must trip on — with a `BaseException` subclass,
  since F4.5 proved a plain `Exception` is swallowed by blanket handlers.
- **A per-module tripwire in the Verification section.** F4.5's was
  `assert 'callback' in <test file>`; F5's pins `release` and `read` in
  `tests/test_facedetect.py`, carried verbatim into Tasks 5 and 7.

## next_action

**`/implement` Task 1 — "Declare `mediapipe` + `opencv-contrib-python`" — in a
fresh session.** `Mode: Mode 3` is the standing "go" for tasks inside this
feature, so no further human "go" is needed to start; the planning session ends
here regardless (the plan skill never builds).

Carry into the build: item 1 above (who verifies), and the unmeasured
`evaluate_js` bridge throughput — the one thing in this feature that cannot be
measured until it is built.

## Commits

Base for this session: `0fdb90e` (the F5 spec approval) → head: the plan commit
recorded below.
Remote: **none** — local history only, nothing pushed.

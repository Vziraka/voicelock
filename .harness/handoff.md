# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 5, LAST task)

**Session date: 2026-07-27.** Task 5 built and passing every automatable
check. One item — the required live manual check — needs the human.

## What happened this session

- Set Task 5 `DOING`, committed alone (`f57a1d9`) before any build work.
  Base commit for the Gate diff: `1b93e90` (parent of the DOING commit).
- Built the `.faceprint`/`#faceprint-panel` block in `index.html`, mirroring
  `.voiceprint`/`#voiceprint-panel` almost verbatim (Q8): 3-band meter,
  "Set face reference"/"Reset" buttons, take-progress dots, hint line —
  placed directly after the voiceprint panel.
- Wired `set_face_reference`/`reset_face_reference` to buttons (same shape
  as the voice equivalents). `compare_face` is polled on a `setInterval`
  (1000 ms, decision 4) gated on `recording && hasFaceReference`, started/
  stopped from `setRecording()` and whenever either flag changes — never
  inside `FaceEngine`'s 30 fps loop, unlike voice's once-per-take update
  (the face path has no discrete "take" boundary to hook instead).
- Added the liveness-honesty line (§6, §5 cmd 7) as dedicated visible copy
  on the panel, not buried in a comment.
- **Caught a JS syntax risk before committing:** this repo's Gate has no JS
  linter, so extracted the inline `<script>` and ran `node --check` on it
  (node used only as a syntax-check tool, not a project dependency) —
  clean. Given Task 4's retry already surfaced two unrun-before-pinning
  mistakes this feature, verified this manually rather than assuming.
- Ran the FULL `spec.md` Verification list (Task 5 is the LAST task, per
  the universal [Done] rule): §5 cmds 1–7 all exit 0 (model+licence
  present, offline load, same/different face separation, convert-not-
  refuse at the amended two resolutions, justification present, mutation-
  sensitivity, liveness-honesty copy present). `uv run ruff check .` →
  exit 0. `uv run pytest` → **145 passed** (unchanged — Task 5 adds no
  pytest tests, UI only), 0 failed.
- Build commit: `dc0e7b5` (`index.html` + `plan.md` Task 5 → `REVIEW`).
  `git status` confirmed the diff is exactly `index.html`, matching Task
  5's declared file.

## The one remaining item: §5 cmd 8 (manual, required)

`spec.md` Q9: a human points the camera at their own face with a
reference set, confirms the meter reads **accept**; then holds up a
different face (a photo, or a second person) and confirms **reject**.
This cannot be performed by an agent — no camera, no eyes on the screen.

**This is not a new problem for this repo** — checked the precedent
directly: `memory/verdicts/2026-07-23-F3-T5.json` and
`memory/verdicts/2026-07-26-F5-T7.json` both record the identical shape:
every automated command passed, the verifier returned `ESCALATE_HUMAN` on
the manual line specifically, the human then ran the live demo and
attested in chat ("looks good" / "manual test passed looks good"), and
that attestation is what "closed the Gate" for the verdict to be written.

Given this session already knows the automated half is fully green (just
verified above) and the outcome of spawning a verifier now would be a
foregone `ESCALATE_HUMAN` on the exact same line every precedent hits,
the human is being asked directly in this session — a clean-context
verifier will still run afterward (it must; this session may not judge
its own diff), but only once the manual attestation is in hand, so that
verifier can complete the FULL Gate (including that line, marked exit 0
on the strength of the attestation) and proceed straight to Review.

## Layout fix (found by the human's manual smoke test, before formal verify)

The human ran the Booth to perform §5 cmd 8 and immediately hit a real bug:
the window's top (the face preview disk) and the new faceprint panel's
buttons were both clipped. Root cause: `.window` has a fixed height budget
with `overflow: hidden`, and `main` centered `.booth` via
`justify-content: center` — a flexbox quirk where overflowing centered
content is pushed past BOTH edges and becomes unreachable even with
`overflow-y: auto`. Fixed within `index.html` only (no `app.py` window-size
change, staying in Task 5's declared scope): `main` drops
`justify-content: center` and gains `overflow-y: auto`; `.booth` centers
itself via `margin: auto 0`, which degrades to top-anchored + scrollable
when content doesn't fit, instead of clipping. Re-ran ruff, the full
suite (145 passed), and cmd 7 — all still exit 0. Commit `e4c17bd`.

## next_action

**Waiting on the human — the ONLY blocker.** Once they run `uv run
voicelock`, set a face reference, confirm accept on their own face and
reject on a different face (or report a problem instead), this session
(or a resumed one) spawns the clean-context verifier with the attestation
quoted into the prompt, per the F3-T5/F5-T7 pattern. From there: Gate PASS
→ Review → (on APPROVE) `wrap-up` → Task 5 `DONE` → **Feature 6 complete**
→ the Mode 3 feature-end checkpoint (completion report, commit/push
approval) — the human's involvement continues past just this manual check.

Also still outstanding, unrelated, from earlier tasks: **TWO pending
guardrail proposals** in this file's prior revisions (now folded into
`memory/verdicts/2026-07-27-F6-T{2,3}.json`) — VIDEO-mode landmarker
tracker-state hazard, and dry-run-before-pinning for concrete-parameter
Verification commands (two occurrences: Task 3's spec.md cmd 4, Task 4's
plan.md SyntaxError). Worth resolving at the same feature-end checkpoint
rather than a separate touchpoint.

## Commits

Session base → head: `1b93e90` → `e4c17bd` (three commits: `f57a1d9` DOING,
`dc0e7b5` build + REVIEW, `e4c17bd` the layout fix above). This
`handoff.md` write is a fourth, bookkeeping-only commit. Nothing pushed.
**The verifier's diff base/head should be `1b93e90`..`e4c17bd`**, not the
earlier `dc0e7b5` — the layout fix landed after this handoff was first
written and is folded in here.

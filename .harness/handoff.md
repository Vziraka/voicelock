# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 3, retry 1)

**Session date: 2026-07-27.** Task 3 was REJECTed once (unexercised error
branch), fixed same-session per Mode 3's budgeted-retry rule, and is back
at `REVIEW`.

## What happened this session

- Verifier REJECTed Task 3 (first pass — spec.md amendment + full module):
  GATE PASS, REVIEW REJECT on the Standards axis only (Spec axis passed).
  Finding: `embed_file`'s `if frame is None: raise FaceprintError(...)`
  branch (a bad/missing image path) was reachable but driven by zero tests
  — `project.md`'s earned no-unexercised-branch guardrail, previously the
  cause of three REJECTs in F4. Minor secondary note: two byte-identical
  tests (`test_compare_without_reference` /
  `test_load_reference_missing_raises`).
- Feedback appended to `plan.md`, Task 3 → `TODO`, `rejects: 1` (commit
  `756e655`).
- Retry (same session, unattended, per Mode 3's rule that a REJECT below
  the 3-cap IS the trigger): set Task 3 `DOING` (commit `352fba1`), base
  for this retry's diff: `756e655`.
- Fix: added `test_embed_file_missing_path_raises` and
  `test_embed_file_corrupt_image_raises`, both asserting `FaceprintError`.
  **Mutation-confirmed before committing** — temporarily neutered the
  `if frame is None: raise` branch and re-ran both new tests: they FAIL
  (with an unrelated `cv2.error`, not the expected `FaceprintError`),
  proving the tests are load-bearing on the actual check rather than
  trivially satisfiable. File restored byte-identical afterward
  (diffed against a backup to confirm). Also deduped the byte-identical
  test per feedback item 2.
- Re-ran all of Task 3's done-criteria: §5 cmd 3 (verbatim) → exit 0; cmd 4
  (verbatim, as amended) → exit 0; cmd 5 (verbatim) → exit 0; cmd 2
  (`pytest -k offline`) → exit 0; cmd 6 (`pytest -k mutation`) → exit 0;
  cutoff anti-drift pin → exit 0; `uv run ruff check .` → exit 0;
  `uv run pytest` → **139 passed** (up from 138, 0 failed).
- Build commit: `adbe26b` (test file fix + `plan.md` Task 3 → `REVIEW`,
  `rejects: 1`).
- `git status` before committing: only `tests/test_faceprint.py` changed —
  minimal, scoped fix, no other files touched.

## Failed attempts / lessons

The REJECT itself is the "failed attempt" — addressed above. Whether it
warrants a `learn` guardrail beyond the existing no-unexercised-branch rule
(which already caught it) is a call for wrap-up's `learn` scan, not this
handoff.

## next_action

**Mode 3 — spawn the clean-context verifier now.**

- Task: **F6 Task 3** — now `REVIEW` (retry 1)
- Base commit: `756e655` (parent of the retry's `DOING` commit `352fba1`)
- Head commit: `adbe26b`
- Verifier: `formats/VERIFIER-PROMPT.md`, used verbatim.
- On REJECT: feedback appended, task back to `TODO`, `rejects` → 2 (one
  attempt remains before the 3-cap sets it `BLOCKED`).
- On APPROVE: `wrap-up` runs, verdict written, Task 3 → `DONE`, then Task 4
  (Booth bridge) starts unattended per Mode 3.

## Pending guardrail (unrelated, still awaiting a separate decision)

Unchanged from the prior handoff — still open, still not part of the
human's "yes" to the Task 3 spec amendment:

> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. (Full text: `memory/verdicts` and prior handoff commits;
> evidence in `tests/fixtures/face/README.md`'s "Detection re-verified"
> section, commit `4c8f880`.) `warn` · expires: 2027-01-31 · proposed
> 2026-07-27, pending human approval.

## Commits

Session base → head: `756e655` → `adbe26b` (two commits: `352fba1` DOING,
`adbe26b` build + REVIEW). This `handoff.md` write is a third,
bookkeeping-only commit. Nothing pushed.

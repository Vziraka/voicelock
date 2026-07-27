# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 4)

**Session date: 2026-07-27.** Continuing the same session after Task 3's
wrap-up completed (Mode 3's standing "go").

## What happened this session

- Set Task 4 `DOING`, committed alone (`8618094`) before any build work.
  Base commit for the Gate diff: `1adec92` (parent of the DOING commit).
- Built the additive `facedetect.py` change (decision 3, `plan.md`): a
  `last_frame` field on `FaceEngine`, set to the raw pre-overlay frame each
  `_loop` tick. Verified additive-only: `pytest tests/test_facedetect.py` (25
  tests) and the existing `test_booth_api.py` camera-lifecycle tests all
  passed unchanged before adding anything new.
- Built `app.py`'s three bridge methods (`set_face_reference`,
  `compare_face`, `reset_face_reference`) exactly to the plan's shape,
  including `compare_face`'s reference-checked-first ordering (mirrors
  `voiceprint.compare`, so a missing reference never costs a face embed).
- Added 6 tests to `tests/test_booth_api.py` (stub `FaceEngine` exposing
  `last_frame`, real fixtures through the real `faceprint` module via the
  bridge — no real camera): the same-face-accepts/different-face-rejects
  path end to end, and both `no_reference`/`no_face` edges (including "no
  camera frame yet" — `last_frame is None`).
- **Caught and fixed a self-inflicted mid-edit bug before committing:** an
  `Edit` call matched `old_string` inside the middle of an existing test
  (`test_frames_are_pushed_to_the_page_as_a_data_uri`) rather than at true
  end-of-file (a truncated `Read` had hidden the test's real tail), which
  split that test in two and left 2 orphaned lines referencing an undefined
  `scripts` variable at the new end of file. `ruff` caught it immediately
  (`F821 Undefined name`). Fixed by moving the tail lines back to their
  original test and removing the orphan copy; re-ran `ruff` clean and the
  full `test_booth_api.py` suite (33 passed) to confirm no other damage.
- **Found and fixed Task 4's own pinned done-criteria one-liner**
  (`plan.md`): the original command chained a `for` loop after `;`
  statements on one line — a Python `SyntaxError`, so it had never actually
  been run before being pinned (the same class of gap as Task 3's cmd 4,
  and the direct evidence for the pending guardrail #2 proposal). Unlike
  cmd 4, this had **zero design ambiguity** — `for x: assert hasattr(...)`
  and `all(hasattr(...) for x in ...)` are the same check — so fixed
  directly without a BLOCKED/human-approval cycle, same category as F5.5
  Task 1's criterion-spelling retry (a mechanical correction, not a design
  fork). Re-ran corrected: exit 0.
- Ran the full standing gate: `uv run ruff check .` → exit 0;
  `uv run pytest` → **145 passed** (up from 139, 0 failed).
- Build commit: `c19c0c5` (`facedetect.py`, `app.py`, `test_booth_api.py`,
  `plan.md` Task 4 → `REVIEW`). `git status` confirmed the diff matches
  Task 4's declared files exactly.

## Failed attempts / lessons

The split-test bug above was self-caused and self-caught (by `ruff`) before
ever reaching a commit — not a rejected attempt, but worth naming: a
truncated `Read` before an `Edit` can silently hide content past the
`limit`, and an `old_string` that matches mid-function rather than at the
intended boundary splices new content into the wrong place. Whether this
pattern (verify insertion points with a wider read, or `grep` for the true
EOF, before editing near the end of a long file) clears the `learn` bar is
a call for wrap-up, not decided here — it cost real time this task but was
a one-off caught immediately by tooling, not by a human or a failed Gate.

## next_action

**Mode 3 — spawn the clean-context verifier now.**

- Task: **F6 Task 4** — now `REVIEW`
- Base commit: `1adec92` (parent of the `DOING` commit `8618094`)
- Head commit: `c19c0c5`
- Verifier: `formats/VERIFIER-PROMPT.md`, used verbatim. Note for the
  verifier: the diff includes a `plan.md` fix to Task 4's own pinned
  done-criteria one-liner (a `SyntaxError` correction, zero design
  ambiguity) — expected and disclosed here, not a scope violation.
- On REJECT: feedback appended to Task 4's log in `plan.md`, task back to
  `TODO`, `rejects` incremented (cap 3).
- On APPROVE: `wrap-up` runs, verdict written, Task 4 → `DONE`, then Task 5
  (Booth UI, the LAST task — full spec Verification) starts unattended per
  Mode 3.

## Pending guardrails (TWO, unchanged, still awaiting separate decisions)

Both carried forward unchanged from the prior handoff — see
`memory/verdicts/2026-07-27-F6-T{2,3}.json` for the proposal text and
evidence (VIDEO-mode landmarker tracker-state hazard; dry-run
verification-command parameters before pinning — this task's own
Syntax-Error criterion is a THIRD piece of evidence for #2, noted above,
though not separately re-proposed).

## Commits

Session base → head: `1adec92` → `c19c0c5` (two commits: `8618094` DOING,
`c19c0c5` build + REVIEW). This `handoff.md` write is a third,
bookkeeping-only commit. Nothing pushed.

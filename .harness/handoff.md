# F7 — Task 1 (`facelock.py`) · BUILT, IN REVIEW

**Base:** `2753768` (Task 1 set `DOING`, committed before any code touched).
**Build commit:** `18118f0` — `facelock.py` (new) + `tests/test_facelock.py`
(new) + `plan.md` (Task 1 → `REVIEW`).

## What this session did
Built Task 1 exactly as `plan.md` scoped it: `facelock.py`, the face fuzzy-
commitment module (`commit`/`reconcile`/`derive_key`/`residual_bits`), ported
from `middlelock.py`'s shape per the two named decisions:

- `commit()` takes a variable-length, non-empty embedding list (decision 1) —
  the Gate test enrolls on `personA_1.jpg` alone; production will enroll on
  `ENROLLMENT_TAKES = 3` live frames (decision 2, wired up by Task 3, not
  this task).
- `CANDIDATE_BITS`/`RELIABLE_BITS`/`KEY_BITS`/`REPETITION` reused **unchanged**
  from `middlelock` (4096/512/32/16) — no dependency on faceprint.py, since
  it exports no `EMBEDDING_DIM`; pinned `EMBEDDING_DIM = 128` locally in
  `facelock.py` (SFace's published output width), citing that in a comment,
  per the plan's fallback instruction. `faceprint.py` itself is untouched
  (spec §3 non-goal).

**`CORRECTION_RADIUS` was measured, not guessed** — dry-run-before-pinning
guardrail (`project.md`): ran 100 fresh-LSH-seed `commit()`/`residual_bits()`
trials against the real vendored SFace model and the real A1/A2/B fixtures
(scratch script, not committed — outside the repo, in `/tmp`). Genuine
residual (enroll A1, reconcile A2) never exceeded 20; impostor residual
(enroll A1 or A2, reconcile B) never dropped below 170. Set
`CORRECTION_RADIUS = 95`, the midpoint, matching the module docstring and
disclosed there as n=1 genuine / n=2 impostor — thinner than `middlelock`'s
200-commit measurement, per spec Q2/§7.

## Gate commands run this session (build-time check, not the fresh-eyes Gate)
- `uv run ruff check .` → exit 0
- `uv run pytest tests/test_facelock.py -q` → **28 passed**
- `uv run pytest -q` → **173 passed** (up from 145 at F6's end — the 28 new
  tests, exact match, 0 failed)

All three are also Task 1's pinned done-criteria (`plan.md` §Task 1) — the
fresh-eyes verifier re-runs them; nothing here substitutes for that.

## What the verifier should know
- Scope held: only `src/voicelock/facelock.py` (new) and
  `tests/test_facelock.py` (new) plus `plan.md`/`handoff.md` bookkeeping
  changed. `middlelock.py`, `voiceprint.py`, `faceprint.py`, `facedetect.py`,
  `vault.py`, `app.py`, `index.html` are all untouched, per spec §3 and
  `plan.md`'s memory-spine item 3.
- The measurement script that produced `CORRECTION_RADIUS = 95` was run in
  `/tmp` and is not part of this diff — the number it produced is pinned as
  a literal constant with a doc comment, same pattern `middlelock.py` uses
  for its own `CORRECTION_RADIUS = 110`.
- `test_genuine_and_impostor_straddle_the_correction_radius` re-measures the
  gap live (two fresh commits, real fixtures) and asserts
  `genuine < CORRECTION_RADIUS < impostor_floor` — satisfies spec §5 cmd 1's
  explicit "assert the actual measured gap" requirement.

## next_action
Mode 3 is the standing "go". Spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, used verbatim, task id `Task 1`, base
`2753768`, head `18118f0`) — this session proceeds to do so immediately, per
Mode 3's build↔verify-cycle rule. On APPROVE, `wrap-up` marks Task 1 `DONE`
and Task 2 (`vault.py` v3) starts unattended, same session. On REJECT, the
task returns to `TODO` with feedback appended to `plan.md`, and Task 1's
`rejects:` counter increments (budgeted retry, cap 3).

## Pending guardrail
None proposed this task — nothing surprising enough to clear the `learn` bar
yet; that scan runs properly at wrap-up if Task 1 is approved.

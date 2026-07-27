# F7 — Task 2 (merged) · BUILT, IN REVIEW

**Base:** `9d2b4b6` (Task 2 set `DOING`, before any code touched).
**Intermediate:** `7272339` (vault half, BLOCKED — see the resolved
contradiction below), `6147254` (UNBLOCKED, plan amended to merge with the
former standalone bridge task).
**Build commit (bridge half):** `656cd65` — `app.py` + `test_booth_api.py`
+ `plan.md` (Task 2 → `REVIEW`).

## What this session did
Task 2 hit a plan contradiction identical in shape to F4 Task 3's precedent:
its declared `files:` line excluded `app.py`, but its done-criteria demanded
a green full suite, and adding a required `faceprints`/`faceprint` parameter
to `vault.enroll`/`unlock` breaks `app.py`'s two existing callers. Stopped
per the universal `[Modes]` rule (Mode 3 forbids unsupervised
interpretation), built and verified everything inside the declared-plus-
coupled scope first (`vault.py` v3 + `test_vault.py`/`test_outer_lock.py`/
`test_middlelock.py`, 52 passed), then presented three resolution options.
**Human chose to merge the vault task with the former standalone bridge
task** (`AskUserQuestion`, recorded in `memory/deviations.md` task F7-T2).
Unlike F4's precedent, there was no honest "minimal, no new bridge
behaviour" framing available — the bridge collected zero face material
before this task — so the merge named the real scope up front rather than
discovering it mid-task.

This session then built the bridge half: `BoothApi` gained
`_enroll_faceprints`, `enroll_face_take()`/`reset_enroll_face_takes()`
(mirroring the voice pair `enroll_take()`/`reset_enroll_takes()` exactly),
a `need_face_takes` guard in `enroll()` after `need_voice_takes`, and
`unlock()` now embeds `self.face.last_frame` and passes it through —
`FaceAuthError` maps to `auth_face` alongside the existing
`auth_outer`/`auth_voice` branches. `plan.md`'s former Task 4 (UI) is
renumbered **Task 3**.

## Gate commands run this session
- `uv run ruff check .` → exit 0
- `uv run pytest tests/test_vault.py tests/test_outer_lock.py tests/test_middlelock.py -q`
  → exit 0, **52 passed** (vault half, run before the block)
- `uv run pytest tests/test_booth_api.py -q` → exit 0, **36 passed** (bridge half)
- `uv run pytest` → exit 0, **181 passed** (up from 173 at Task 1's end — the
  vault half's ~8 new tests + the bridge half's 3 new tests + Task 1's 28,
  all accounted for; 0 failed)

All are also Task 2's pinned done-criteria (`plan.md` §Task 2, spec §5 cmds
2 and 3) — the fresh-eyes verifier re-runs them; nothing here substitutes
for that.

## What the verifier should know
- **This task's scope is unusual — read `memory/deviations.md`'s F7-T2 entry
  and `plan.md`'s 2026-07-27 amendment before judging scope.** Task 2 was
  originally declared as `vault.py`/`test_vault.py` only; a human-approved
  mid-task amendment merged in the former standalone bridge task
  (`app.py`/`test_booth_api.py`) after a documented BLOCKED stop. The diff
  legitimately spans both halves — that is not scope creep, it is the
  approved scope.
- `tests/test_outer_lock.py` and `tests/test_middlelock.py`'s nested-vault
  section are also touched (synthetic-embedding signature updates) — flagged
  explicitly per the same precedent, not left for the scope check to find.
- `middlelock.py`, `voiceprint.py`, `faceprint.py`, `facedetect.py`,
  `facelock.py` are all untouched (spec §3 non-goals / already-DONE Task 1).
- Peel order is outer → middle → inner: `vault.unlock` only reaches
  `facelock.reconcile` after both the passphrase and the voice have already
  verified — traced in `vault.py`'s `unlock()`.

## next_action
Mode 3 is the standing "go". Spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, verbatim, task id `Task 2`, base `9d2b4b6`,
head `656cd65`) — this session proceeds immediately. On APPROVE, `wrap-up`
marks Task 2 `DONE` and Task 3 (Booth UI, the LAST task — full spec
Verification including the required live manual check) starts unattended,
same session. On REJECT, Task 2 returns to `TODO` with feedback appended to
`plan.md`, `rejects:` increments (cap 3).

## Pending guardrail
None proposed yet this task — the recurrence itself (identical shape to F4
Task 3, now twice) is worth raising at this task's `learn` scan, including
the observation that F4's own proposed guardrail for this ("a task that
changes a module's public signature owns every in-repo caller of it, or the
plan must name the caller explicitly") does not appear in `project.md`'s
current earned guardrails despite being proposed once already.

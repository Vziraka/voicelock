# Handoff — F7 Task 2 · BLOCKED (plan contradiction) · 2026-07-27

## Where we are
Task 1 is `DONE`. **Task 2 is `BLOCKED`** — not because the code failed, but
because the task's own ledger entry cannot be satisfied as written. Everything
inside Task 2's declared (plus unavoidably-coupled) scope is built and
passing; one human decision unblocks it. Tasks 3–4 remain `TODO`.

- base: `9d2b4b6` (Task 2 `DOING`, committed before building)
- head: this session's Task 2 work-in-progress commit

**This is the identical shape F4 Task 3 hit** (`git log --oneline`:
`2706679` `F4 Task 3: BLOCKED — plan contradiction` →
`d583749` `F4 Task 3: UNBLOCKED by human decision — scope extended to app.py;
Task 4 reduced`). Same root cause, one feature deeper: a task that adds a
required parameter to a shared function breaks every existing caller, and the
plan assigned the only other caller to the next task.

## The contradiction (why this stopped instead of improvising)
Universal `[Modes]`: *"A rule you cannot follow literally (contradictory,
impossible, or pointing at something that does not exist): in Modes 3–4, STOP —
set the task `BLOCKED` and report; unsupervised interpretation is forbidden."*

Task 2's ledger entry says both of these, and they cannot both hold:

| Where | What it says |
|---|---|
| `files:` | `src/voicelock/vault.py`, `tests/test_vault.py` |
| done-criteria | `uv run pytest` → exit 0 (**full** suite green) |

Task 2 adds a required `faceprints: list[np.ndarray]` parameter to
`vault.enroll` and a required `faceprint: np.ndarray` parameter to
`vault.unlock` (plan.md decision 4). `src/voicelock/app.py` lines **173** and
**204** are the only other callers, and the plan assigns the bridge to
**Task 3**. So the full suite cannot reach exit 0 while Task 2 stays inside
its declared files.

Unlike F4's precedent, there is no "minimal, no new bridge behaviour" escape
hatch even in principle: the vault now requires **face material the bridge
does not collect** — `BoothApi` has no `_enroll_faceprints` list, no
`enroll_face_take()`, and no captured face embedding at unlock time. Wiring
around that minimally would mean building Task 3's actual bridge behaviour
under Task 2's name.

## What is already built and green (declared scope + unavoidably-coupled callers)
- `src/voicelock/vault.py` — v3 nested layout exactly as spec §2 Q3 and
  `plan.md` decisions 4–6 pin it: `{helper_data_voice, middle_ciphertext}`
  under the outer (passphrase) key, `{helper_data_face, inner_ciphertext}`
  under the middle (voice) key, profile JSON under the inner (face) key.
  `FaceAuthError` alongside `AuthError`/`VoiceAuthError`. Both legacy
  versions refused by name: v1 → "This vault predates voice", v2 → "This
  vault predates face". Peel order outer → middle → inner, each check only
  reached after the previous one verified.
- `tests/test_vault.py` (declared) — format/validation cases plus the new
  inner-reject cases (spec §5 cmd 2's "right passphrase + right voice +
  wrong face" and the v1/v2 legacy-message assertions), all synthetic
  unit-vector embeddings, no model dependency.
- `tests/test_outer_lock.py`, `tests/test_middlelock.py`'s nested-vault
  section — both call the same changed signature and were unavoidable for
  the same reason F4's precedent flagged; not on Task 2's `files:` line,
  flagged here explicitly rather than left for the verifier's scope check to
  find.

Evidence:
- `uv run pytest tests/test_vault.py tests/test_outer_lock.py tests/test_middlelock.py -q`
  → exit 0, **52 passed in 23.87s**
- `uv run ruff check .` → exit 0 (`All checks passed!`)
- `uv run pytest` → exit **1**, **8 failed, 170 passed** — every failure is
  in `tests/test_booth_api.py`, all cascading from `app.py:173`/`204` calling
  `vault_enroll`/`vault_unlock` with too few arguments (`TypeError`,
  surfaced through the bridge's generic exception fallback as e.g.
  `"enroll() missing 1 required positional argument: 'faceprints'"`). No
  other file fails.

## The decision needed (my recommendation first)
1. **Merge Tasks 2 and 3** into one task and verify them together —
   recommended, and the honest reading of F4's own precedent: F4's "minimal
   signature fix" turned out to require the real bridge behaviour anyway
   (`enroll_take()`/banking/`need_voice_takes`), and its own commit message
   said so plainly ("the bridge half absorbed... Task 4 reduced"). Here the
   gap is larger (F4 already had voice material to pass; F7 doesn't yet have
   face material at all), so calling it "minimal" would be dishonest — this
   option names that up front. Concretely: finish Task 2's vault work (already
   green) plus Task 3's bridge work (`enroll_face_take()`,
   `reset_enroll_face_takes()`, `_enroll_faceprints`, `need_face_takes`
   guard, unlock's face capture + `auth_face` mapping) as one task, verified
   once. Task 4 (pure UI wiring) stays a separate task, unchanged in scope.
2. **Amend Task 2's done-criteria** to the three-file subset
   (`test_vault.py`/`test_outer_lock.py`/`test_middlelock.py`) and let the
   full suite go green at Task 3. Honest, and keeps the two tasks separate,
   but it leaves the standing regression net red (8 failing) for one task
   cycle — a real, if temporary, weakening at exactly the moment the vault
   format changes.
3. **Revert Task 2's signature change** and stage it as additive/optional
   instead (e.g. `faceprints: list[np.ndarray] | None = None`, vault falls
   back to some placeholder when absent). Keeps every existing caller
   compiling untouched. Not recommended: it reintroduces exactly the kind of
   provisional/never-cleaned-up optionality `project.md`'s guardrails warn
   against, and it would let a vault seal without a real face factor —
   contrary to spec §1's "always all factors" outcome.

Any of the three is a `plan.md` amendment. Under Mode 3 the amendment itself
is a human gate, which is the other reason this stopped here.

## next_action
**Human:** pick 1, 2, or 3 above. Then the session resumes Task 2 (or the
merged task) unattended, re-runs the Gate, and continues per Mode 3.

## Commits this session
`bcb4138` (F7 Task 1 wrap-up, DONE) → `9d2b4b6` (Task 2 `DOING`) → this
work-in-progress commit (vault.py v3 + the three coupled test files,
Task 2 → `BLOCKED`). Remote: local commits only, no push this session.

## Pending guardrail
None yet — but this is the **second** occurrence of the exact same failure
shape (F4 Task 3, now F7 Task 2): a task that changes a shared function's
signature and the plan splitting "the function" from "its only other caller"
across two tasks. F4's own `learn` scan proposed a guardrail for this
("a task that changes a module's public signature owns every in-repo caller
of it, or the plan must name the caller explicitly") but it does not appear
in `project.md`'s current earned guardrails — it was apparently never
approved or was dropped at a `curate` pass. Worth raising again at this
task's `learn` scan once unblocked, given it has now recurred once, exactly
as the guardrail predicted it would.

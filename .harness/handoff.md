# Handoff — F4 Task 3 · BLOCKED (plan contradiction) · 2026-07-26

## Where we are
Tasks 1–2 are `DONE`. **Task 3 is `BLOCKED`** — not because the code failed, but
because the task's own ledger entry cannot be satisfied as written. Everything
inside Task 3's declared scope is built and passing; one human decision unblocks
it. Tasks 4–5 remain `TODO`.

- base: `3a88ed3` (Task 3 `DOING`, committed before building)
- head: this session's Task 3 work-in-progress commit

## The contradiction (why this stopped instead of improvising)
Universal `[Modes]`: *"A rule you cannot follow literally (contradictory,
impossible, or pointing at something that does not exist): in Modes 3–4, STOP —
set the task `BLOCKED` and report; unsupervised interpretation is forbidden."*

Task 3's ledger entry says both of these, and they cannot both hold:

| Where | What it says |
|---|---|
| `files:` | `src/voicelock/vault.py`, `tests/test_middlelock.py`, `tests/test_vault.py` |
| done-criteria | `uv run pytest` → exit 0 (**full** suite green) |

Task 3 changes the `vault.enroll` / `vault.unlock` signatures (they now take
voiceprints). `src/voicelock/app.py` lines **70** and **86** are the only other
callers, and the plan assigns the bridge to **Task 4**. So the full suite cannot
reach exit 0 while Task 3 stays inside its declared files.

The plan did anticipate part of this — Task 3's notes say updating `test_vault.py`
"is a required change, not scope creep", and Task 4's notes say the booth test's
`"auth"` → `"auth_outer"` string changes in Task 4. What neither anticipated is
that Task 3 **breaks the bridge outright**, not just its error strings.

## What is already built and green (inside the declared scope)
- `src/voicelock/vault.py` — v2 nested layout exactly as spec §4 pins it: profile
  JSON sealed with the voice-derived middle key → `{helper_data,
  middle_ciphertext}` sealed with the passphrase-derived outer key → `VLCK` +
  version byte **2** + opslimit + memlimit + salt. New `VoiceAuthError` and
  `LegacyVaultError` beside the existing `AuthError`. Peel order is outer-then-
  middle, with a test that asserts a wrong passphrase outranks a wrong voice.
- `tests/test_middlelock.py` — spec §5 vault cases **(1)(2)(3)(4)(6)(7)** added.
- `tests/test_vault.py`, `tests/test_outer_lock.py` — updated for the new
  signature using synthetic unit-vector voiceprints, so the format/validation
  cases stay fast and free of the ECAPA model.

Evidence:
- `uv run pytest tests/test_middlelock.py tests/test_vault.py tests/test_outer_lock.py -q`
  → exit 0, **47 passed in 15.70s**
- `uv run ruff check .` → exit 0 (`All checks passed!`)
- `uv run pytest` → exit **1**, `5 failed, 69 passed` — all five failures are
  `tests/test_booth_api.py` cases calling the old signature. No other file fails.

**Note:** `tests/test_outer_lock.py` is edited but is NOT on Task 3's `files:`
line. It calls the same changed API, so it was unavoidable for the same reason —
flagging it explicitly rather than letting the verifier's scope check find it.

## The decision needed (my recommendation first)
1. **Extend Task 3 to include the minimal `app.py` signature fix** — recommended.
   Two call sites, no new bridge behaviour: `enroll` passes the voiceprints it
   already has access to, `unlock` passes one. Task 4 still owns the real work
   (5-take `enroll_take` banking, `auth_outer` / `auth_voice` / `legacy_vault` /
   `need_more_audio` mapping, the raised minimum, window-averaged embedding).
   Cheapest, keeps WIP=1 honest, and the Gate goes green.
2. **Merge Tasks 3 and 4** into one task and verify them together. Cleanest on
   paper, but it makes one large diff out of the two riskiest integration steps.
3. **Amend Task 3's done-criteria** to the three-file subset and let the full
   suite go green at Task 4. Honest, but it weakens the standing regression net
   at exactly the moment the vault format changes.

Any of the three is a `plan.md` amendment. Under Mode 3 the amendment itself is a
human gate, which is the other reason this stopped here.

## next_action
**Human:** pick 1, 2 or 3 above. Then the session resumes Task 3 (or the merged
task), re-runs the Gate, and continues to Tasks 4–5 unattended per Mode 3.
*(curate due — 16 verdicts vs `Last curated: never`)*

## Commits (this session, on `main`)
`a13d891` → `01667e1` → `a671db3` → `72b6743` (T1 done) → `4a16acc` → `469a4cd` →
`c2310ef` → `0fa8e8a` (T2 done) → `3a88ed3` (T3 DOING) → this work-in-progress
commit. Remote: **none** — local history only, no push.

## Pending guardrail
None yet — but if you pick option 1 or 2, the `learn` scan at Task 3's wrap-up
should consider a guardrail along the lines of *"a task that changes a module's
public signature owns every in-repo caller of it, or the plan must name the
caller explicitly"*. That is the lesson this stop is evidence for; I am not
writing it to `project.md` without your approval.

## Notes for the human (carried, still open)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- Your existing `~/.voicelock/vault.vl` is a v1 vault; once Task 3 lands it is
  refused with a re-enroll prompt (by design).

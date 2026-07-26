# Handoff — F4 Task 3 · DONE · 2026-07-26

## Where we are
**Tasks 1–3 are `DONE`**; Feature 4 is 3/5. The vault is genuinely two-locked.
Task 3 was `BLOCKED` on a plan contradiction (human-resolved), then REJECTed once
on the Standards axis and APPROVEd on retry 1 — `rejects: 1`. Tasks 4–5 `TODO`.

## Changed
- `src/voicelock/vault.py` — v2 nested layout, `VoiceAuthError`, `LegacyVaultError`
- `src/voicelock/app.py` — `enroll_take()` banking, banked takes → `vault.enroll`,
  unlock embeds the last capture, distinct `auth_outer` / `auth_voice` /
  `legacy_vault` / `need_more_audio` error mapping
- `tests/test_middlelock.py` — spec §5 vault cases (1)(2)(3)(4)(6)(7)
- `tests/test_vault.py`, `tests/test_outer_lock.py`, `tests/test_booth_api.py` —
  new signature; booth tests bank five takes and assert the distinct rejects
- `.harness/memory/deviations.md` — the block, the human's decision, and the
  honest note that "no new bridge behaviour" was unachievable

## Failed + lesson
**One REJECT, both findings accepted without argument:** `reset_enroll_takes()`
was speculative, uncalled and untested (deleted — the suite still reports 78
passed, confirming it was dead code), and `plan.md`'s `files:` line contradicted
its own scope-extension paragraph (corrected). Recorded in Task 3's feedback log.
Verdict: `memory/verdicts/2026-07-26-F4-T3.json`.

## THE THING THAT MATTERS MOST RIGHT NOW
**The feature is not demo-able yet.** `src/voicelock/ui/index.html` still tests
`error === "auth"` and its fallback renders "wrong passphrase" for *any* error, so
in the live Booth today the two rejects collapse into one message and enrollment
cannot bank voice takes at all. The engine is correct; the window is not wired.
Task 5 owns this, and its criterion is the §5 manual demo. Do not judge the
feature by the green suite until Task 5 lands.

## next_action
**Task 4** — the reduced scope: lever 5 (embed each take as the average of 2–3
overlapping windows, plus an F4-specific raised minimum speech length as a module
constant; F3's `compare` floor stays untouched) and any remaining booth-api
done-criteria coverage. Not started. *(curate due — 17 verdicts)*

## Where the rest lives
- the block, the decision, the honest correction → `memory/deviations.md` (2026-07-26, F4-T3)
- v2 on-disk layout diagram → `src/voicelock/vault.py` module docstring
- middle-lock constants + measured basis → `src/voicelock/middlelock.py`
- why the commitment costs a KDF → `adr/0003-middle-lock-commitment-costs-a-kdf.md`

## Commits (this session, on `main`)
`a13d891` → `01667e1` → `a671db3` → `72b6743` (T1 done) → `4a16acc` → `469a4cd` →
`c2310ef` → `0fa8e8a` (T2 done) → `3a88ed3` → `2706679` (BLOCKED) → `d583749`
(decision) → `1488925` (rejected build) → `16c01fb` (reject recorded) → `eb7d4ce`
(retry-1 build, APPROVEd) → `b832bed` / `18bcef6` (handoff) → this wrap-up commit.
Remote: **none** — local history only, no push.

## Pending guardrail — NEEDS YOUR APPROVAL, not written
The `learn` scan found a lesson that clears the bar (it cost a `BLOCKED` stop, a
human touchpoint, and a REJECT — and it will recur, since Tasks 4–5 and every
future feature change APIs). Proposed for `constitution/project.md`:

> - **[Startup]** A task that changes a module's public signature owns every
>   in-repo caller of it — the plan must name those callers in the task's `files:`
>   line, or the task's done-criteria must not require a green full suite.
>   `warn` · expires: 2027-01-31
>   - _Evidence:_ F4 Task 3 (2026-07-26) declared three files but changed
>     `vault.enroll`/`vault.unlock`, which `app.py`, `test_outer_lock.py` and
>     `test_booth_api.py` all call. Its done-criteria demanded `uv run pytest`
>     exit 0, so the two requirements were mutually exclusive and the task
>     stopped `BLOCKED` mid-session.
>   - _Added:_ 2026-07-26

Considered enforcing it mechanically instead of remembering it (the `learn`
skill's first question): the honest answer is that this belongs in the `plan`
skill as a caller-scan step rather than in a lint rule, which is a harness change
outside this feature's scope. Prose guardrail is the fallback; say the word and I
will write it, or decline it and it disappears.

## Notes for the human (carried)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- Your `~/.voicelock/vault.vl` is v1 and is now refused with a re-enroll prompt.

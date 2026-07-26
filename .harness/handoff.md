# Handoff — F4 Task 4 (lever 5 capture quality) · /implement session · 2026-07-26

## Where we are
Tasks 1–3 `DONE`. **Task 4 is `REVIEW`.** Task 5 remains `TODO` — it is the
feature's LAST task and carries the FULL spec §5 list including the
**human-attested manual demo**, which an agent cannot perform.

- base: `f41f669` (Task 4 `DOING`, committed before building)
- head: **`RETRYHEAD`** (retry-1 build commit — supersedes `0fc073d`)
- **retry 1 of 3** after a Standards-axis REJECT; `rejects: 1`

## Changed
- `src/voicelock/app.py` — `MIN_LOCK_SECONDS = 1.2`, `LOCK_WINDOWS = 3`,
  `LOCK_WINDOW_FRACTION = 0.7`, and `lock_voiceprint()`; wired into `enroll_take`
  and `unlock`
- `tests/test_booth_api.py` — three lever-5 cases
- Nothing else. `voiceprint.py` untouched, so F3's diagnostic keeps its own floor.

## Scope note for the verifier
Task 4's ledger entry was **reduced** on 2026-07-26: Task 3 absorbed the bridge's
signature-driven half (`enroll_take` banking, banked takes → `vault.enroll`,
`unlock` embedding, the `auth_outer`/`auth_voice`/`legacy_vault`/`need_more_audio`
mapping) because the vault change broke those call sites and Task 3's
done-criteria demanded a green full suite. See `memory/deviations.md`
(2026-07-26, F4-T3) and Task 4's own "scope REDUCED" paragraph. What remained,
and what this diff is, is **lever 5 only**. Task 4's original done-criteria
(a)-(g) are all still satisfied — most were met in Task 3 and are asserted in
`tests/test_booth_api.py`; this task adds the capture-quality half.

## Doubts the verifier should weigh
1. **`MIN_LOCK_SECONDS = 1.2` is bounded above by the fixtures, not chosen freely.**
   Spec §3 asks for "meaningfully more" than 0.4 s; a real enrollment sentence is
   3-5 s. The enrollment fixtures are 1.6 s (Task 1 pinned that as the longest
   window keeping takes 1 and 5 disjoint), so any floor above 1.6 s would make
   the fixtures unusable. 1.2 s is 3x F3's floor with headroom under 1.6 s. In a
   live demo the real constraint is the spoken sentence, not this floor.
2. **`lock_voiceprint` lives in `app.py`, not `voiceprint.py`.** Deliberate: spec
   §4 says keep the F3 voiceprint engine unchanged as the identity source, and
   Task 4's `files:` line is `app.py` + its test. The cost is that a DSP-ish
   helper sits in the bridge module. If you would rather it lived in the engine,
   that is a spec question, not a build one.
3. **Runtime tripled per lock take** (3 embeds instead of 1); whole suite 25s ->
   47s. Inside spec §5's 10-minute budget with room, but worth knowing before
   Task 5 adds more.
4. **RETRACTED, and the reason for the one REJECT.** The first build had a
   `hop == 0` short-circuit, and this handoff defended it by claiming it was
   reachable for takes between 1.2 s and ~1.71 s and exercised by the suite. That
   was **wrong**: with `window = min(N, max(19200, 0.7N))`, hop is zero only for
   `N ∈ {19200, 19201}`, and measured hops on the fixtures are 3200 / 4696 / 4963
   — never 0. No test drove it. The branch is **deleted**; the general path
   handles a degenerate take correctly, confirmed directly (a 19 200-sample take
   returns a unit vector, no error).

## What I ran (measurement-exception disclosure)
- `uv run ruff check .` → exit 0 (`All checks passed!`)
- `uv run pytest tests/test_booth_api.py -q` → exit 0 (17 passed)
- `uv run pytest` → exit 0 (**81 passed in 46.95s**)

## next_action
Verify Task 4 with **clean context** — `formats/VERIFIER-PROMPT.md` verbatim, task
`F4-T4`, base `f41f669`, head `RETRYHEAD`. On APPROVE → wrap-up, then **Task 5**.

**Read this before starting Task 5:** it is F4's LAST task, so its done-criterion
is the FULL spec §5 Verification list — which includes a **manual, human-attested
live demo** (real mic, enroll, unlock, wrong passphrase, and a *different person*
speaking). No agent can attest that. Expect the Gate to return ESCALATE_HUMAN on
that line, exactly as F3 Task 5 did (`memory/verdicts/2026-07-23-F3-T5.json`
records the same pattern: automated PASS, manual attested by the human afterward).
The UI wiring itself is automatable and must land first: `index.html` still tests
`error === "auth"` and cannot bank enrollment takes.

## Pending guardrail
Unchanged from Task 3's wrap-up and still awaiting your approval — the
"a task that changes a public signature owns its callers" rule. Full text in the
Task 3 wrap-up handoff (git: `2f5662b`).

## Commits (this session, on `main`)
… → `2f5662b` (T3 done) → `f41f669` (T4 DOING) → `0fc073d` (T4 build).
Remote: **none** — local history only, no push.

## Notes for the human (carried)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- Your `~/.voicelock/vault.vl` is v1 and is now refused with a re-enroll prompt.

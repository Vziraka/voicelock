# Handoff — F4 Task 4 · DONE · 2026-07-26

## Where we are
**Tasks 1–4 are `DONE`**; Feature 4 is 4/5. The engine is complete: the vault is
genuinely two-locked and both lock paths use the raised floor and window-averaged
embedding. **Only Task 5 remains, and it cannot finish unattended** — see below.

## Changed
- `src/voicelock/app.py` — `MIN_LOCK_SECONDS = 1.2`, `LOCK_WINDOWS = 3`,
  `LOCK_WINDOW_FRACTION = 0.7`, `lock_voiceprint()`; wired into `enroll_take` and
  `unlock` only
- `tests/test_booth_api.py` — three lever-5 cases
- `voiceprint.py` untouched, so F3's diagnostic keeps its own 0.4 s floor

## Failed + lesson
**One REJECT** (`rejects: 1`), Standards axis: a `hop == 0` short-circuit that was
dead (reachable only at exactly 19 200–19 201 samples), untested, and redundant.
Deleted. The handoff note that had defended it with a false coverage claim was
**retracted in place** rather than quietly dropped. Verdict:
`memory/verdicts/2026-07-26-F4-T4.json`.

The first verifier also independently re-measured the calibration risk this task
creates — enrollment vectors are now window-averaged while `CORRECTION_RADIUS`
was pinned on raw embeddings — and separation holds: genuine residual **0**,
impostor floor **159** (raw-enroll baseline 0 / 173).

## next_action — READ BEFORE STARTING
**Task 5, the feature's LAST task.** Its done-criterion is the FULL `spec.md`
**Verification** list, which includes:

> **Manual (required for F4 done, human-attested):** `uv run voicelock` → enroll
> (name + passphrase + read the 5 sentences) → unlock with the right passphrase +
> the enrolled voice → unlocked; **wrong passphrase** → outer REJECT; a
> **different person** speaks with the right passphrase → middle REJECT.

No agent can attest that — it needs a real mic, a real human, and a second
person. **Expect the Gate to return ESCALATE_HUMAN on that line.** This is the
same shape as F3 Task 5, whose verdict
(`memory/verdicts/2026-07-23-F3-T5.json`) records: *"Manual Booth demo attested
PASS by the human 2026-07-23 ('looks good') after verifier ESCALATE_HUMAN."*

The automatable part must land first — **the Booth UI is not wired to F4 at all**:
- `src/voicelock/ui/index.html` still tests `error === "auth"`, and its fallback
  renders "wrong passphrase" for *any* error, so the two rejects collapse in the
  live window
- there is no enrollment voice-capture step, so `enroll_take()` is never called
  and enrolling through the real Booth is currently impossible
- no `auth_voice` chip, no `legacy_vault` re-enroll message

Also carry a one-line cleanup the Task 4 verifier flagged as non-blocking:
`tests/test_booth_api.py::test_lock_take_is_the_average_of_overlapping_windows`
declares an unused `tmp_path` fixture.

## Pending guardrails — BOTH await your approval, neither written
1. *(from Task 3)* **[Startup]** A task that changes a module's public signature
   owns every in-repo caller of it — the plan must name those callers in the
   task's `files:` line, or the task's done-criteria must not require a green full
   suite. `warn` · _Evidence:_ F4 Task 3 stopped `BLOCKED` mid-session on exactly
   this contradiction.
2. *(new, from Tasks 3 and 4 together)* **[Forbidden]** Do not add a helper,
   branch, or method that no caller and no test exercises — delete it and let the
   task that needs it introduce it. `warn` · _Evidence:_ **both** of this
   session's REJECTs were this same defect — `reset_enroll_takes()` (Task 3,
   uncalled and untested) and `lock_voiceprint`'s `hop == 0` branch (Task 4, dead
   and untested). Two occurrences in one feature is the pattern the `learn` bar
   asks for.

Proposal 2 has the stronger evidence. `learn`'s first question is whether a lesson
can be *enforced* rather than remembered: partially — ruff's `vulture`-style dead
code detection is not in the current ruff config, and adding a linter is a
dependency decision needing a TECH-PICK, so prose is the honest fallback for now.

## Where the rest lives
- lever-5 constants and rationale → `src/voicelock/app.py` header comment
- middle-lock constants + measured basis → `src/voicelock/middlelock.py`
- v2 on-disk layout → `src/voicelock/vault.py` docstring
- the Task 3 block and its resolution → `memory/deviations.md` (2026-07-26)

## Commits (this session, on `main`)
… → `2f5662b` (T3 done) → `f41f669` (T4 DOING) → `0fc073d` (rejected build) →
`d7baf22` (reject recorded) → `82d9096` (retry-1 build, APPROVEd) → `b52741f` →
this wrap-up commit. Remote: **none** — local history only, no push.

## Notes for the human (carried)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- Your `~/.voicelock/vault.vl` is v1 and is now refused with a re-enroll prompt —
  you will need to re-enroll once before the manual demo.
- **Curate is due** — 18 verdicts vs `Last curated: never`.

# F6 — Faceprint on screen · Task 4 WRAP-UP

**Session date: 2026-07-27.** Task 4 built, verified (clean-context
subagent, APPROVE), and wrapped up in this session.

## What happened this session

- Spawned the clean-context verifier (subagent path) with
  `formats/VERIFIER-PROMPT.md` verbatim. Verdict: **GATE PASS, REVIEW
  APPROVE**, no feedback. The verifier independently reproduced the
  pre-fix `SyntaxError` in Task 4's original done-criteria one-liner,
  confirming the build-time fix was mechanical (not a design amendment),
  and specifically scrutinized whether `facedetect.py`'s change stayed
  additive-only (confirmed byte-for-byte) and whether the new bridge tests
  exercise the real `faceprint` module (confirmed, unmocked). Full
  reasoning: `memory/verdicts/2026-07-27-F6-T4.json`.
- Wrap-up checklist run in full:
  - **ADR:** none — fails condition 1 (hard to reverse). Additive plumbing,
    not architecture.
  - **`learn` scan:** ran, outcome `"lesson": "none"` — no NEW guardrail
    from this task. The two things that could look lesson-shaped both
    reduce to existing signal: the self-caught split-test slip (fixed
    within seconds by `ruff`, no rework, no human, no multi-step
    investigation — below the bar) and the `SyntaxError` in Task 4's own
    pinned criterion (the SAME pattern as the already-pending guardrail
    #2, not a new one — its evidence line below is updated with this
    occurrence rather than duplicated as a fresh proposal).
  - No idea was declined by a human this task — no `.out-of-scope/` entry
    owed.
  - **Roadmap:** unchanged — 1 task remains in Feature 6 (Task 5, the
    LAST task, full spec Verification).
  - **`plan.md`:** Active context, memory spine, and Task 4's line
    refreshed; Task 4 → `DONE`.

## Pending guardrails (TWO, both still awaiting separate human decisions)

**#1 — carried from Task 2, unchanged:**

> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. (Full text and evidence: `memory/verdicts/2026-07-27-F6-T2.json`,
> `tests/fixtures/face/README.md`'s "Detection re-verified" section, commit
> `4c8f880`.) `warn` · expires: 2027-01-31 · proposed 2026-07-27.

**#2 — carried from Task 3, evidence extended this session:**

> **[Done]** A Verification command that exercises a real vendored model,
> OR any command with concrete literal parameters, must be dry-run BEFORE
> being pinned into `spec.md`/`plan.md` — a plausible-looking one-liner can
> be silently wrong (impossible data, or outright invalid syntax) and that
> is indistinguishable from a real defect until someone actually runs it.
> `warn` · expires: 2027-01-31
> - _Evidence:_ (1) F6 Task 3 (2026-07-27) — `spec.md` §5 cmd 4's
>   non-aspect-preserving resize produced input no honest implementation
>   could process; cost a full `BLOCKED` stop and human escalation. (2) F6
>   Task 4 (2026-07-27) — `plan.md`'s own pinned done-criteria one-liner
>   (`for name in (...): assert hasattr(...)` chained after `;`) was a
>   Python `SyntaxError` — it had never been run before being pinned
>   either. Lower cost this time (a mechanical, zero-ambiguity fix, no
>   escalation needed), but the SAME root gap: a criterion authored and
>   pinned without being executed once against reality. Two independent
>   occurrences in one feature is why this is proposed as a guardrail, not
>   dismissed as a one-off.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

Both proposals still need your yes/no/amend before either lands in
`project.md`. Neither blocks Task 5.

## next_action

**Mode 3 — the approved spec's Mode line is the standing "go."** This same
session continues to **Task 5** (Booth UI panel + liveness-honesty copy) —
Task 4's wrap-up is the precondition, and it just completed. **Task 5 is
the LAST task**, so its verify pass runs the FULL list from `spec.md`'s
Verification section, not just plan-authored done-criteria — and per Q9,
**§5 cmd 8 is a required manual check**: a human must point a real camera
at their own face with a reference set and confirm the meter reads accept,
then hold up a different face and confirm reject. That check cannot run
unattended even in Mode 3 — it will need you at the feature-end checkpoint
regardless of how the rest of Task 5 goes.

## Commits

Session base → head: `c19c0c5` → (this wrap-up's commits: verdict file +
`handoff.md` + `plan.md` DONE state). Nothing pushed.

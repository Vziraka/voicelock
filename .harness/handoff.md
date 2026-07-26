# Handoff — F4.5 planned, 3 tasks ready to build · 2026-07-26

Session type: `/plan` (pre-build). No code was changed.

## Entry gate — quoted, not remembered
All three checks passed against `spec.md` before anything was written:
- Grilling record: "**Status: CLEAR** — every category resolved; zero
  clarification markers remain (2026-07-26)."
- Marker scan for the bracketed `NEEDS-CLARIFICATION` token in its colon form:
  **0 hits**.
- `- [x] Grilling record below is CLEAR` · `- [x] Approved by human` ·
  `- **Mode:** Mode 3 (Spec-to-done). Set by the human 2026-07-26.`
  The box-2 `x` was confirmed via `git diff` to be the **human's own** unstaged
  edit — the only difference between the index and the working tree.

## Changed this session
- **`plan.md`** — replaced. F4's completed ledger is gone (git `22e6a4a` is its
  archive, per the single-file convention); F4.5's ledger takes its place:
  **3 tasks, all `TODO`, `rejects: 0`**, memory spine refreshed.
- **`constitution/project.md`** — the F4 pending guardrail, approved by the human
  this session and written: "**[Forbidden]** The UI must not keep its own copy of
  state the engine owns — render the engine's value instead of a local mirror."
  Second earned guardrail in the repo.
- **`handoff.md`** — this file.

## The plan in one paragraph
Three tasks, ordered so dependencies come first. **Task 1** declares `soundfile`
(`uv add`, manifest only — the TECH-PICK is already human-approved). **Task 2**
teaches `FakeStream` to deliver frames through the **real** callback and adds a
re-entrant-teardown tripwire, plus the two tests that prove both — all of it
passes at base, because it touches no production code. **Task 3** lands the
actual fix (`_on_audio` raises `sd.CallbackStop`, no self-teardown, stale comment
corrected) together with its regression tests, and carries the FULL spec §5 list
as the last task.

Why the fix and its tests are one task: splitting them would land a fixed branch
with no test covering it — the exact earned guardrail (`project.md` 2026-07-26)
that cost F4 three REJECTs.

Why no cap-through-callback test in Task 2: at base that path deadlocks, so such
a test cannot exit 0 there. It is Task 3's repro. This is stated in Task 2's
notes so a verifier does not score its absence as missing coverage.

## Found while planning — read before building Task 2
`capture.py:135-142` wraps both `stream.stop()` and `stream.close()` in
`except Exception: pass`. A re-entrant tripwire that raises a plain `Exception`
is therefore **swallowed silently**, and Task 3's regression test would pass
while the defect is still live. The tripwire must raise a **`BaseException`
subclass**. This is in Task 2's notes and in the memory spine.

## Pending guardrail — RESOLVED this session
The guardrail proposed by F4 Task 5's `learn` scan, carried unapproved across two
handoffs, was **approved by the human this session and written to
`constitution/project.md`**. Nothing is pending any more. The written entry:

> **[Forbidden]** The UI must not keep its own copy of state the engine owns —
> render the engine's value instead of a local mirror. `warn` · expires: 2027-01-31

It is the repo's **second** earned guardrail. F4.5 touches no UI so it does not
bite here; it lands before F5, which is the feature that adds FaceView.

## next_action
1. **`/implement` Task 1 in a fresh session.** No further human "go" is needed —
   `spec.md`'s approved `Mode: Mode 3` is the standing go for tasks inside this
   feature (universal [Approval]). Planning ends here; building belongs to the
   implement skill's own session.
2. Task 3 will reach the Gate as **ESCALATE_HUMAN** on spec §5's required
   31-second live Booth check. Do not mark it `DONE` or write its verdict file
   until the human attests it (F3-T5 / F4-T5 precedent).
3. After F4.5 is DONE: `/spec` for **F5 — Camera booth**, starting with its
   TECH-PICK (offline face detect / landmark / embedding stack). Deferred by
   human decision so only one feature is ever in flight.

## Commits
Base `9d0b137` → head `PENDING` (recorded in the follow-up bookkeeping commit,
per the two-commit rule — a commit cannot contain its own hash).
Remote: **none** — local history only, nothing pushed.

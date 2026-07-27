# Handoff — F5.5 planned, 3 tasks, ready to build

**Mode 4 is the standing "go".** No further human approval is needed to start
Task 1 — the approved spec's `Mode:` line is that permission, and it reaches
every task inside this feature (never past it).

## State

- **F5 — Camera booth: DONE** (`319b48b`).
- **`/curate` second pass: DONE** (`296357a`) — 6 guardrails, calibration run 2.
- **`/setup` re-run: DONE** (`2a87c28`) — both tools, `CLAUDE.md`, adapter.
- **F5.5 spec: APPROVED** (`b246cb2`, box 2 checked by the human 2026-07-26).
- **F5.5 plan: WRITTEN — 3 tasks, all `TODO`, `rejects: 0`.** ← this session

## The ledger

| Task | What | Files |
|---|---|---|
| 1 | `load_wav` refuses bad audio instead of converting it (+ tests, + the F6 justification comment) | `voiceprint.py`, `tests/test_voiceprint.py` |
| 2 | Remove the `sample_rate` parameters, then delete the now-callerless `_resample` | `voiceprint.py` |
| 3 | **LAST** — stop the same-speaker test overclaiming (rename + docstring) | `tests/test_voiceprint.py` |

**The order is forced, not stylistic.** `_resample` has two call sites — `embed`
and `load_wav` — so it cannot be deleted until both are gone. Task 1 removes
one, Task 2 removes the other and then the function. That is the whole reason
the deletion is not a single task.

Task 3 is LAST, so its done-criterion is the FULL `spec.md` Verification list.

## Things the builder must not re-litigate

1. **Do not re-propose the ordering assertion** on the byte-disjoint
   `enroll1`/`enroll5` pair. It was drafted during grilling and **disproved by
   measurement**: a dummy embedder with no speaker modelling orders that pair
   correctly too (0.077 < 0.113). The confound is one recording session per
   speaker, not byte overlap. `plan.md` memory spine item 1 has the detail.
2. **Do not move a threshold to make anything pass.** `ACCEPT_CUTOFF = 0.45` and
   `REJECT_CUTOFF = 0.65` are pinned by a done-criterion on Tasks 2 and 3.
3. **Do not touch `load_reference`'s re-normalize** (`voiceprint.py:112`). A
   verifier flagged it; `spec.md` §3 keeps it deliberately.
4. **Do not expect a manual check.** This is the first feature with none, and
   `spec.md` §5 records why — no live surface, so a Booth demo would be theatre.
   A verifier should **not** `ESCALATE_HUMAN` over its absence here.

## Verifier path

**Subagent** (`project.md` Environment, and proven this session — six
clean-context verifiers ran during calibration run 2). At Mode 4 the implement
session spawns the verifier itself with `formats/VERIFIER-PROMPT.md` **verbatim**
and is the executor of the returned verdict; it never overrides it. Wanting to
override = `ESCALATE_HUMAN`.

## Mode 4 tail — after Task 3

Once Task 3 is `DONE` and wrap-up writes F5.5's completion report, the session
drafts **F6 — Faceprint on screen**'s spec with every grilling question embedded
as a clarification marker and its `Mode:` line left blank, then **parks it at
the approval gate and stops.** Never approved, never built, never more than that
one spec. F6 inherits from F5: the fetched-not-committed fixture arrangement,
the two-faces gap (CC0 shortlist in
`memory/research/2026-07-26-f5-fixture-replacement-candidates.md`), and a second
vendored model dir for OpenCV SFace — which owes a per-asset licence check under
the updated rule 1.

## Pending guardrail

None.

## Commits

- Session base: `b246cb2` → head: this bookkeeping commit.
- Remote `origin` exists (private), so the checkpoint pushes as well as commits.

## next_action

**`/implement` Task 1** — in a fresh session (building belongs to the implement
skill's own session, per plan skill step 7; the planning session ends here). At
Mode 4 that session starts **without a further "go"**.

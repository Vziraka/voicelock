# Handoff — F4 (Voice as the middle lock) · /plan + amendment session · 2026-07-26

## Where we are
F4's ledger is written (**5 tasks, all `TODO`, `rejects: 0`**), but `spec.md` was
**amended this session** with five accuracy levers agreed with the human, which
re-opened the approval gate.

**`spec.md` approval box 2 is OPEN — `- [ ] Approved by human`. Nothing may be
planned further or built until the human types the `x`.** Box 1 stays checked:
the Grilling record was re-scanned after the amendment and
`grep -c "NEEDS-CLARIFICATION:" .harness/spec.md` still returns **0**.

## Next action
1. **Human:** read `spec.md` §0 (the `AMENDMENT 2026-07-26` block) plus the amended
   §3 Enroll/Unlock flow and §4 keystone, then re-check **box 2**.
2. Then `/implement` **Task 1** in a fresh session — Mode 3 is the standing "go"
   for tasks inside F4 once box 2 is checked.

## What the amendment changed (and what it did NOT)
Five levers, agreed after the human asked how to reduce the ~25 % genuine
bit-error. Full rationale in `memory/decisions.md` (2026-07-26).

1. **Soft-decision decoding** — weight each repetition vote by its projection
   magnitude instead of counting hard signs.
2. **Cross-take unanimity** as the reliability mask's primary filter (margin
   becomes the tiebreak).
3. **Large LSH candidate pool (~2048–4096) masked down to ~512** reliable bits,
   instead of projecting straight to ~512.
4. **Short key (~32 bits) with deep repetition (~16×)** rather than a long,
   shallowly-repeated key.
5. **Longer, window-averaged captures on both sides** — full 3–5 s phonetically
   varied enrollment sentences, and an unlock take embedded as the average of 2–3
   overlapping windows against a raised minimum length.

Explicitly **rejected**: deliberately varying emotion / pitch / vocal effort across
the enrollment takes (it widens between-take spread and starves lever 2). Lever 6,
embedding centering, is **test-only and low confidence** — measure it, don't
depend on it.

**Unchanged:** the feature's outcome, its non-goals, the §5 Verification list, the
task count and task boundaries, and "no new dependency". This amendment changes
only HOW the reconcile is built.

## Why the spec was amended rather than just the plan
The verifier reads exactly `universal.md`, `project.md`, `spec.md`, `plan.md`,
`handoff.md` — **`memory/decisions.md` is not on that list**, so a decision logged
only there is invisible at verification. `verify-review`'s Spec axis asks "does the
diff faithfully implement `spec.md`?" with a default stance of REJECT. Two spec
lines would have contradicted the planned build: §4's "~512 bits" (we now expand to
~4096 and mask down) and §4's "majority-vote" (we now weight by confidence). Both
are now corrected in the spec. Amending pre-build, with nothing `DOING`, is the
cheapest possible moment — a mid-build REJECT would have burned one of Task 2's
three retry attempts.

## Risks for the human
- **Task 2 is the one that can genuinely fail.** The research's binomial numbers
  assume independent bit flips; with only 192 real dimensions the expanded bits are
  correlated, so measured results will be **worse** than the arithmetic predicts.
  The plan requires a `BLOCKED` report rather than a loosened correction radius —
  a voice lock that accepts everyone is worse than none.
- **If Task 2 blocks, suspect the fixtures first.** The committed speaker-A source
  audio is ~3.3 s total, so fixture takes are ~1 s each versus 3–5 s in a real
  enrollment. Escalation order: better fixture audio → accept a higher false-reject
  rate for the demo → revisit the declined `komm` BCH dependency (already
  researched, live, and would need a fresh TECH-PICK + sign-off).
- **Breaking changes inside the repo (planned, not accidental):** `vault.enroll` /
  `vault.unlock` gain a voiceprint argument, and the bridge's old `error: "auth"`
  becomes `auth_outer`. `tests/test_vault.py` (Task 3) and `tests/test_booth_api.py`
  (Task 4) are updated in the tasks that cause the break.
- **Your existing `~/.voicelock/vault.vl` is a v1 vault** and will be refused with
  a re-enroll prompt after F4 (by design — human confirmed 2026-07-26). One
  re-enroll is needed before the manual demo.
- Carried from F3: `spec.md`'s "~20 MB" model-size wording is wrong (the vendored
  ECAPA is ~85 MB). Left for the human — I did not touch it while amending, since
  it is outside this amendment's scope.

## Commits (this session, on `main`)
- Base `13dd43f` (F4 `/plan`: 5-task ledger) → head: the amendment commit for this
  session.
- Remote: **none** — local history only, no push.

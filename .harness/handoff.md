# Handoff — F4 (Voice as the middle lock) · /spec session · 2026-07-23

## Where we are
F4's `spec.md` is drafted and the **Grilling record is CLEAR** (zero
`[NEEDS-CLARIFICATION:` markers). **Box 1 checked** (mechanical CLEAR gate);
**box 2 is OPEN** — the human approves it. **Mode 3** (Spec-to-done), set at
grilling. No planning or building may start until box 2 is checked.

## Next action
1. **Human:** read `spec.md` §1 Outcome + §5 Verification, confirm the **Mode 3**
   line, and type the `x` in **box 2** of the §0 Approval gate.
2. Then, in a **fresh session**, run **`/plan`** to break F4 into ordered tasks.

## What F4 is (one line)
The voiceprint becomes a real cryptographic lock: fuzzy-reconcile the enrolled
voiceprint into a stable key + non-secret helper data, sealing a **middle lock**
inside F2's outer (passphrase) lock. Unlock needs passphrase **and** the enrolled
voice, with three visibly-distinct outcomes (in / wrong-passphrase-outer-reject /
wrong-voice-middle-reject).

## Decisions locked this session (all in `memory/decisions.md`, dated 2026-07-23)
- **Fuzzy reconcile:** hand-rolled **pure-numpy code-offset fuzzy commitment**,
  **NO new dependency** (LSH bit-expansion + reliability mask + repetition/majority
  ECC). Research: `memory/research/2026-07-23-f4-fuzzy-reconcile.md` (bchlib/reedsolo
  fail liveness; komm/galois live but add a dep for only the easy step). No
  TECH-PICK triggered.
- **Accuracy/enroll:** 5-sentence averaged enrollment (richer than F3's 3) +
  reliability mask + fixture-pinned correction radius. Full tuning/quality-gate = F9.
- **Vault:** helper data lives **inside the outer-passphrase box**; nested v2
  layout (`VLCK` v2). A pre-existing **v1** vault is **refused** with a re-enroll
  prompt (no passphrase-only bypass).
- **Unlock:** passphrase + one utterance (identity-only, no challenge — that's F8);
  distinct rejects `auth_outer` ("Wrong passphrase") vs `auth_voice` ("Voice didn't
  match"); neither leaks the name.
- **F3 diagnostic panel:** kept as-is (independent diagnostic).
- **Mode 3** + the mandatory "if gates passed but still wrong" answer: cross-session
  real-mic robustness is covered by the **required manual demo**; reject-collapse /
  leak covered by automated distinct-reject + no-leak checks (§5).

## Verification shape (pinned in §5)
Standing: `ruff` + `pytest` exit 0. Feature: `tests/test_middlelock.py` (enroll
binds middle key + seals v2 · same-speaker unlocks · different-speaker → middle
REJECT no leak · wrong passphrase → outer REJECT · tolerance = imported constants ·
v1 refused · helper-data-at-rest) + `tests/test_booth_api.py` (bridge enroll seals
v2, unlock distinct `auth_outer`/`auth_voice`) + a **required live Booth manual demo**.

## Notes / risks for the human
- Likely new module `src/voicelock/middlelock.py` (~150–250 lines numpy) + `vault.py`
  v2 nesting + `app.py`/`ui/index.html` wiring. `/plan` will break this down.
- Honest limits accepted (in spec §3/§4): small false-reject rate, non-zero
  false-accept for a very similar voice, replay of the enrolled voice still passes
  (F8 defends it), no FAR/FRR guarantees.
- Minor stale-state note carried from F3: `plan.md` mentioned a "pending feature-end
  commit checkpoint", but the F3 DONE + completion-report commit already landed
  (`627963e`) and the tree was clean — F3 is effectively closed.

## Commits (this session, on `main`)
- Base `627963e` (F3 DONE) → head: the `/spec` commit for this session.
- Remote: **none** — local history only, no push.

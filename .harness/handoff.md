# F7 — Face as the inner lock (innermost) · COMPLETION REPORT

**Feature complete 2026-07-28 (Mode 3).** All three tasks `DONE`, verdicts in
`memory/verdicts/2026-07-27-F7-T1.json`, `2026-07-27-F7-T2.json`,
`2026-07-28-F7-T3.json`. Awaiting the human's commit/push approval below —
the feature-end checkpoint.

## Outcome vs spec.md §1

Spec's Outcome: make the faceprint a real cryptographic lock — fuzzy-
reconcile it into a stable key, seal a third, innermost AEAD layer wrapping
F4's voice middle lock, itself wrapping F2's passphrase outer lock. Unlock
requires passphrase **and** voice **and** face, with four visibly distinct
outcomes.

**Delivered exactly that.** `vault.py` is now `FORMAT_VERSION = 3`:
passphrase outer → voice middle → face inner, peel order load-bearing (each
layer only reached after the previous one verified). All four demo
outcomes confirmed live by the human (verbatim: **"everything worked
perfect"**):
- right passphrase + enrolled voice + enrolled face → **unlocked**, name shown
- wrong passphrase → **outer REJECT**
- right passphrase, wrong voice → **middle REJECT**
- right passphrase, right voice, wrong face → **inner REJECT**

F7's two non-goals held: F6's diagnostic faceprint panel (and
`faceprint.ref`) are untouched — still an independent, non-lock meter,
exactly as F3's voiceprint panel survived F4; no liveness/challenge/lip-sync
(F8's job) and no enrollment-quality gate or tolerance UI (F9's job) were
added.

## Full final-Gate evidence (command → exit code)

- `uv run pytest tests/test_facelock.py -q` → exit 0, 28 passed
- `uv run pytest tests/test_vault.py -q` → exit 0, 13 passed
- `uv run pytest tests/test_booth_api.py -q` → exit 0, 41 passed
- `uv run ruff check .` → exit 0 ("All checks passed!")
- `uv run pytest` → exit 0, **186 passed** (0 failed; 145 at F6's end → 173
  after Task 1 → 186 after Task 2's retry; Task 3 added no Python tests)
- spec §5 cmd 4 (manual, required) → **ATTESTED** by the human 2026-07-28,
  same protocol as `2026-07-23-F3-T5.json`/`2026-07-26-F5-T7.json`/
  `2026-07-27-F6-T5.json`: ran `uv run voicelock`, walked enroll (name +
  passphrase + 5 voice sentences + 3 face frames) then all four unlock
  outcomes above, explicitly checked for layout clipping in the new
  enroll-face-step block. Verbatim: "everything worked perfect."

## Retry counts per task

- Task 1 (`facelock.py`): `rejects: 0`
- Task 2 (`vault.py` v3 + Booth bridge, merged): `rejects: 1` — one REJECT
  for missing test coverage on new bridge surfaces (`enroll_face_take`'s and
  `unlock`'s `no_face` edges, an unexercised `reset_enroll_face_takes()`),
  fixed same session, APPROVE on retry 1 of 3
- Task 3 (Booth UI): `rejects: 0`

## `memory/deviations.md` entries made during this feature

One entry, task `F7-T2` (2026-07-27): Task 2's declared `files:` line
(`vault.py`, `test_vault.py`) excluded `app.py`, but its done-criteria
demanded a green full test suite, and the required `faceprints`/`faceprint`
parameter broke `app.py`'s only calls to it — the plan had assigned that
fix to a separate Task 3. Identical shape to `memory/deviations.md`'s
existing `F4-T3` entry (2026-07-26). Stopped per the universal `[Modes]`
rule (Mode 3 forbids unsupervised interpretation) rather than improvising;
presented three resolution options; the human chose to merge Task 2 with
the former standalone bridge task. Unlike F4's precedent, no "minimal, no
new bridge behaviour" framing was available or attempted — the bridge
collected zero face material before this task, so the merge named the real
scope up front.

## Anything escalation-worthy that resolved itself

The manual-attestation sequencing: the first verifier pass on Task 3 (build
`30f4add`) scored spec §5 cmd 4 as "PENDING, not a failure" under this
session's explicit framing and returned APPROVE. On reflection this
diverged from the repo's own established protocol for an unattested manual
check (`F3-T5`/`F5-T7`/`F6-T5`: score `ESCALATE_HUMAN`, ask the human
directly, then re-verify with the attestation quoted in). Self-corrected
before wrap-up: asked the human for the live attestation, recorded it in
this file, then re-spawned a second clean-context verifier with the
attestation quoted into its prompt — that second pass is what
`2026-07-28-F7-T3.json` records as authoritative. No rework was lost (the
UI code itself needed no changes), and no human correction was required —
caught by re-reading this repo's own precedent files before finalizing.

## Guardrail earned this feature

Human-approved, written to `project.md` during Task 2's wrap-up (see that
file's newest `[Forbidden]` entry, dated 2026-07-27): *"When `/plan` splits
a signature change to a shared function across two tasks, it must grep for
every in-repo caller of that function BEFORE assigning `files:` lines."*
Evidence: this exact failure shape recurred verbatim across two features
(F4 Task 3, then F7 Task 2) — F4's own `learn` scan proposed the identical
guardrail once already and it was never adopted; re-proposed and approved
this time.

## State files refreshed this wrap-up

- `roadmap.md` — F7's box checked, built summary added, architecture
  diagram's `planned` class corrected (was stale since before F7 — several
  already-shipped F3–F6 nodes were still marked dashed/planned; now only
  `Liveness`/F8 is planned)
- `memory/codebase-map.md` — refreshed for F7: `facelock.py` documented,
  `vault.py`'s entry updated to v3/three-layer, `app.py`/`index.html`
  entries updated for the bridge + UI additions, architecture diagram's
  `FuzzyF`/`Inner` moved from planned to solid
- `plan.md` — Active context, memory spine, all three task lines → `DONE`

## Curate status

**Curate is due** — 40 verdict files vs `project.md`'s `Last curated:
2026-07-26 (second pass) · verdicts then: 29` = 11 tasks since the last
pass (was 10 at Task 2's wrap-up, now 11 after Task 3's verdict). Not
blocking; worth running soon given the sustained backlog.

## next_action

**Feature-end checkpoint — awaiting the human.** Proposed commit message
below covers all state-file writes from this wrap-up (verdict, roadmap,
codebase-map, plan.md). On approval: commit, then push if requested (no
push without explicit ask, per standing instructions). After that, F8
(Lip-sync liveness) is the next roadmap item — not started, no draft
parked (Mode 3, not Mode 4 — unattended next-feature drafting is a Mode 4
behavior only).

**Proposed commit message:**
```
F7 wrap-up: feature complete -- roadmap/codebase-map refreshed, Task 3 verdict recorded

All three tasks DONE. Human attested the live 4-outcome demo (Sec5 cmd 4),
verbatim "everything worked perfect". Full Gate: 186 passed, ruff clean.
roadmap.md F7 box checked + built summary; memory/codebase-map.md refreshed
for the face inner lock (was planned, now solid) and its stale pre-F7
planned/solid markers corrected. plan.md: all three tasks -> DONE.
```

# F4 — COMPLETION REPORT · Voice as the middle lock · 2026-07-26 (Mode 3)

**Feature complete.** All five tasks `DONE`, `roadmap.md`'s F4 box checked,
`memory/codebase-map.md` refreshed. The commit checkpoint is the human's.

## Outcome vs the spec's Outcome section
Spec §1 asked to "make the **voiceprint** a real cryptographic lock, not just an
on-screen meter", with three visibly distinct demo outcomes. Delivered:

| Spec §1 promise | Status |
|---|---|
| Fuzzy-reconcile the voiceprint into a stable key with non-secret helper data | `middlelock.py` — code-offset fuzzy commitment, pure numpy, **no new dependency** |
| Middle lock as an AEAD layer wrapping the F2 outer box | `vault.py` v2: profile sealed with the voice key, wrapped in `{helper_data, middle_ciphertext}` sealed with the passphrase key |
| Unlock needs passphrase **and** the enrolled speaker's voice | peel order outer→middle; a wrong passphrase raises before the voice is consulted |
| right passphrase + right voice → **unlocked** (name shown) | attested live |
| **wrong passphrase** → outer REJECT "wrong passphrase" | attested live |
| right passphrase + **different person** → middle REJECT "voice did not match" | attested live |

Non-goals held: no face/camera/liveness, no tolerance-tuning UI, single vault, no
recovery, and the honest limits stayed honest — helper data is non-secret, the
secret is short, and F4 does **not** stop replay of a recording (that is F8).

## Final Gate evidence (all run this session)
| Command | Exit |
|---|---|
| `uv run ruff check .` | 0 — `All checks passed!` |
| `uv run pytest` | 0 — **83 passed in 48.15s** |
| `uv run pytest tests/test_middlelock.py -q` | 0 — 36 passed (§5 cases 1–7) |
| `uv run pytest tests/test_booth_api.py -q` | 0 — 19 passed (distinct `auth_outer`/`auth_voice`) |
| UI copy + offline assertion (`plan.md` T5) | 0 |
| **Manual Booth demo** (required, human-attested) | **PASS — attested by the human 2026-07-26** after the verifier's GATE ESCALATE_HUMAN |

## Retry counts
| Task | rejects | Note |
|---|---|---|
| 1 — enrollment fixtures | 0 | |
| 2 — `middlelock.py` | 0 | the feature's riskiest task passed first time |
| 3 — `vault.py` v2 | 1 | also stopped `BLOCKED` once on a plan contradiction |
| 4 — lever 5 capture quality | 1 | |
| 5 — Booth UI | 1 | the reject was a real correctness defect, see below |

## Deviations logged during the feature
One entry in `memory/deviations.md` (2026-07-26, F4-T3): Task 3's `files:` line
and its green-full-suite done-criterion were mutually exclusive, because the task
changed `vault.enroll`/`vault.unlock` and `app.py` calls them. The session
**stopped `BLOCKED`** rather than interpret (Mode 3 forbids unsupervised
interpretation); the human chose to extend Task 3 with the bridge fix. The entry
also records honestly that the human's option said "no new bridge behaviour" and
that this proved unachievable, so the smallest coherent change was taken instead.

## Escalation-worthy things that resolved themselves
- **Task 2 was expected to be able to fail** — the plan required a `BLOCKED`
  report rather than a loosened correction radius if genuine and impostor would
  not separate. They separated with a wide margin (genuine 0 residual bits,
  impostor floor 156, radius 110 at the midpoint of that gap), measured over 200
  independent commits and independently reproduced by the verifier. No radius was
  ever loosened.
- **The one defect that mattered** was caught at Task 5, not by the tests: an
  abandoned enrollment left banked takes in the bridge while the UI showed "0 / 5",
  so the vault could have been sealed from discarded audio — possibly a different
  person's — and it was reachable in the manual demo itself. Fixed at the source.

## What this feature taught (one guardrail, human-approved and written)
`constitution/project.md` now holds its first earned rule:
> **[Forbidden]** Never add a helper, method, or branch that no caller and no test
> exercises… `warn` · expires: 2027-01-31

All three of this feature's REJECTs were that same defect. A second proposal (a
signature change owning its in-repo callers) was **declined/parked** — the real
fix belongs in the `plan` skill, not in a rule someone must remember.

A third candidate surfaced at Task 5 and is **proposed, not written** — awaiting
the human:
> **[Forbidden]** The UI must not keep its own copy of state the engine owns —
> render the engine's value instead of a local mirror. `warn`
> _Evidence:_ F4 Task 5 — `resetEnrollVoiceStep()` zeroed a JS take-counter while
> the bridge kept its banked takes, so the panel showed `0 / 5` over a non-empty
> engine and the next enrollment would have sealed abandoned takes into the vault.
> Relevant beyond this bug: F5–F8 add FaceView, liveness and more UI state to a
> project whose stated convention is already "Python owns state; JS renders only".

## Next
- **Curate is due** — 19 verdict files vs `project.md`'s `Last curated: never ·
  verdicts then: 0`. Human-invoked; nothing blocks on it.
- **F5 — Camera booth** is next in `roadmap.md` and carries a **TECH-PICK**
  (offline face detect/landmark/embedding stack). Its spec is not drafted.
- Carried, still open for the human: `spec.md`'s "~20 MB" model-size wording is
  wrong (the vendored ECAPA is ~85 MB), and §0's amendment paragraph still reads
  "awaiting the human's `x`" though box 2 is checked.

## Commits
This session ran `a13d891` → `41d5391` on `main` (Task 1 DOING through the Task 5
escalation), plus the approved-guardrail commit. Remote: **none** — local history
only, nothing pushed.

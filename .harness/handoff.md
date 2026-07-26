# Handoff — F4 Task 2 (`middlelock.py`) · /implement session · 2026-07-26

## Where we are
Task 1 is `DONE`. **Task 2 is `REVIEW`** — the fuzzy commitment is built and it
separates genuine from impostor with a wide margin, so the planned `BLOCKED`
branch did **not** fire. Tasks 3–5 stay `TODO` (WIP=1).

- base: `4a16acc` (Task 2 `DOING`, committed before building)
- head: `469a4cd` (build commit — this handoff's own commit is one after it)

## Changed
- `src/voicelock/middlelock.py` — **new**. `commit` / `reconcile` / `derive_key`
  plus `residual_bits` (the diagnostic view the tests assert on). Pure numpy +
  the already-present PyNaCl; **no new dependency**, nothing added to
  `pyproject.toml` or `uv.lock`.
- `tests/test_middlelock.py` — **new**, 27 cases.
- `.harness/plan.md` — Task 2 `DOING → REVIEW` with the measurements under it.
- `voiceprint.py`, `vault.py`, `app.py`, the UI and the F3 tests are **untouched**
  — Task 2 is engine-only, as planned.

## The number that decides the feature
Measured over **200 independent commits** (each draws a fresh random LSH seed, so
this is a distribution, not one lucky projection):

| probe class | n | min | median | max |
|---|---|---|---|---|
| enrollment takes + same-speaker probe | 1200 | 0 | 0 | **0** |
| harder same-speaker (F3 thirds, cosine 0.12–0.43) | 600 | 0 | 19 | **63** |
| impostor (speaker B) | 200 | **156** | 188 | 218 |

`CORRECTION_RADIUS = 110` is the midpoint of the 63…156 gap. Pinned constants:
`CANDIDATE_BITS=4096`, `RELIABLE_BITS=512`, `KEY_BITS=32`, `REPETITION=16`.

## Doubts and judgment calls the verifier should weigh
1. **Soft decoding does not measurably help on these fixtures** (lever 1, the
   spec's highest-expected-effect lever). Over 40 commits: worst genuine 51 either
   way, impostor floor 167 soft vs 165 hard. The cause is that the fixtures never
   approach the decision boundary — the hardest genuine clip still gets only ~1.5
   of 16 copies wrong per secret bit, nowhere near an 8/16 tie, so no reweighting
   can change the outcome. Spec §4 says "plain hard-decision majority remains the
   fallback if soft decoding does not measurably help on the fixtures". I **kept
   soft**: it cannot lose to hard voting, it is the spec's required lever, and
   switching on the basis of an easy fixture set would be optimizing for the
   fixture rather than the live demo. Flagging it rather than burying it — if you
   read that clause as mandatory, this is the line to reject on.
2. **Lever 6 (centering) measured and NOT adopted, as the plan directed.** The
   vendored `mean_var_norm_emb.ckpt` is **not** applied: SpeechBrain's
   `encode_batch(wavs, wav_lens=None, normalize=False)` defaults to `False` and
   `voiceprint.embed` never passes it. Enabling it moves the genuine/impostor gap
   from 116 to 117 bits — i.e. nothing — and would require editing F3's
   `voiceprint.py`, which spec §4 forbids ("keep the F3 voiceprint engine
   unchanged").
3. **KDF choice** (spec §4 left this open: "Argon2id or HKDF-style stretch — pick
   one at build time"). Chose **Argon2id at INTERACTIVE** cost, not MODERATE. The
   outer passphrase lock already pays MODERATE and this layer is only reachable
   after the outer lock has fallen. Two stretches run per unlock (commitment
   verify + key derive). Whole suite: **11.4 s**, far inside spec §5's budget.
4. **A short secret needs a slow verifier.** With `KEY_BITS=32`, storing a plain
   `sha256(s)` as the commitment would let anyone who has already opened the outer
   box brute-force 2³² hashes in seconds and recover the middle key. So the
   commitment tag and the key both hang off **one Argon2id stretch** under
   different info strings — a guess costs a KDF, not a hash. This is a
   strengthening of spec §4's `H(s)`, not a departure from its structure: the
   helper still carries exactly {LSH seed, reliability mask, XOR offset P, H(s)}.
5. **What the radius can and cannot do.** Widening it can never admit a wrong
   voice — the commitment tag is the authoritative check and a wrong secret fails
   it at any radius. The radius is a cheap early reject and the inspectable place
   where "close enough" is written down. Narrowing it too far costs genuine
   unlocks. Worth knowing before F9 touches the tuning UI.
6. **One test I wrote was wrong and I rewrote it, rather than working around it.**
   The first version asserted that corrupting a few helper-data bits must stop the
   lock opening. That is backwards: a handful of flipped bits is exactly the error
   pattern the repetition code exists to absorb, so recovering the original secret
   there is correct. The shipped tests assert the real property — light corruption
   either corrects or fails closed but never yields a *different* secret, and
   swapping in a whole valid component from a second commit always fails closed.

## What I ran (measurement-exception disclosure)
Task 2's done-criterion is a measurement (pin the tolerance so the clusters
separate), so I ran its commands. Fresh eyes still own verification:
- `uv run pytest tests/test_middlelock.py -q` → exit 0, **27 passed** (run 5× to
  check for seed flakiness — the random LSH seed differs every run; 27 passed each
  time)
- `uv run ruff check .` → exit 0 (`All checks passed!`)
- `uv run pytest` → exit 0 (**62 passed in 11.39s**)

## next_action
Verify Task 2 with **clean context** — `formats/VERIFIER-PROMPT.md` verbatim,
task `F4-T2`, base `4a16acc`, head `469a4cd`. On APPROVE → wrap-up, then Task 3
(`vault.py` v2 nesting). *(curate due — 15 verdicts vs `Last curated: never`)*

## Where the rest lives
- pinned constants + why → `src/voicelock/middlelock.py` module header and the
  comment above `CORRECTION_RADIUS`
- fixture geometry and the raw sign-bit statistics → `tests/fixtures/voiceprint/README.md`
- construction background and the rejected ECC dependencies →
  `memory/research/2026-07-23-f4-fuzzy-reconcile.md`

## Commits (this session, on `main`)
`a13d891` → `01667e1` → `a671db3` → `72b6743` (Task 1 done) → `4a16acc` (Task 2
DOING) → `469a4cd` (Task 2 build). Remote: **none** — local history, no push.

## Pending guardrail
None.

## Notes for the human (unchanged from the last handoff, still open)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- Your existing `~/.voicelock/vault.vl` is a v1 vault and will be refused with a
  re-enroll prompt after F4 (by design).

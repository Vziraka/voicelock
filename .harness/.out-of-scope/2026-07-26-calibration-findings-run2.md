# Findings from the SECOND 2026-07-26 calibration run

Found by re-verifying the same three archived tasks as run 1 (F1-T2, F2-T3,
F3-T2) with run 1's confounds fixed. See
`memory/verdicts/2026-07-26-CALIBRATION-RUN-2.md`.

**Not built** — curate is a gardening pass and shipped-code fixes need their own
spec/plan. Every claim below was reproduced independently in the main working
tree, not taken on an agent's word.

Companion file: `2026-07-26-calibration-findings.md` (run 1). Its items 1
(callback self-deadlock) and 2 (undeclared `soundfile`) were **fixed by F4.5**
and are closed — verified at HEAD: `capture.py:120` raises `sd.CallbackStop`,
and `pyproject.toml:13` declares `soundfile>=0.14.0`.

---

## 1. Speculative resample / multichannel surface (F3, LIVE)

The one blocking finding of run 2, and the only one both F3-T2 verifiers agreed
on. Re-confirmed at HEAD: `_resample` (`voiceprint.py:206`) is reached only from
`:72` and `:157`, both behind `sample_rate != SAMPLE_RATE`. `capture.py:32,65-66`
pins the only real audio source at 16 kHz, an unsupported rate raises into the
mic-error path rather than renegotiating, and all fixtures are 16 kHz mono.

Mutation-proved dead by the verifier: replacing the body with a raise leaves the
full suite at 30 passed. Same pattern, smaller: the stereo-downmix branch
(`:154-155`), `load_reference`'s re-normalize (`:112`), and the `sample_rate`
parameters on `embed` (`:65`) and `compare` (`:116`).

- Direct hit on the earned "no unexercised branch" guardrail, though the code
  predates the rule by four days.
- **Fix direction:** ~12-line deletion; reintroduce where genuinely needed.
- **Caution:** `voiceprint.py` is frozen by F4's spec §4 as "the identity
  source, unchanged", so this needs a spec that says otherwise.
- **Roadmap fit:** F9 — Demo reliability.

## 2. The same-speaker automated test is weak by construction (F3, LIVE, narrow)

**Read the counterweight below before acting on this.** The fixture overlap
itself is *not* a new finding — it is disclosed, reasoned, and deliberate. What
survives scrutiny is narrower than run 1's framing suggested.

### What I verified

Exact-array comparison over `tests/fixtures/voiceprint/` — the containment is
byte-level, not merely acoustic:

| Relationship | Offset |
|---|---|
| `speakerA_live` is a verbatim slice of `take1+take2+take3` | 10434 |
| `speakerA_take2` is contained in `speakerA_live` | 6957 |
| `speakerA_enroll3` is contained in `speakerA_live` | 2852 |
| `speakerA_take1` is contained in `speakerA_enroll1` | 0 |
| `speakerA_take2` is contained in `speakerA_enroll3` | 4105 |

Measured with the vendored model at HEAD:

| Pair | Distance | Band |
|---|---|---|
| take1 vs take2 — same speaker, byte-disjoint | 0.641 | borderline |
| take1 vs take3 — same speaker, byte-disjoint | 0.745 | reject |
| take2 vs take3 — same speaker, byte-disjoint | 0.518 | borderline |
| mean(take1..3) vs live — *what the accept test measures* | 0.165 | accept |
| mean(take1..3) vs speakerB | 0.832 | reject |
| mean(enroll1..5) vs live — *what F4 measures* | 0.058 | accept |
| mean(enroll1,2,4,5) — dropping byte-overlapping enroll3 | 0.082 | accept |

### The counterweight — why this is mostly already handled

`tests/fixtures/voiceprint/README.md` is more rigorous than run 1 credited. It
discloses the overlap (`:18-22`), gives the cause — the Apache-2.0 model repo
**ships one clip per speaker**, and offline-only forbids fetching another —
documents the window geometry chosen so **takes 1 and 5 share zero audio**
(`:51-58`), already records cross-take max 0.624 at 1.6 s and 0.747 at 1.2 s
(i.e. it *already states* that two same-speaker takes can exceed the reject
cutoff), and says outright that the fixtures "prove the *math* separates same
from different; they do **not** prove the lock works live" (`:89-93`), assigning
that proof to spec §5's required manual demo. It even pre-forbids the tempting
wrong fix: "never widen the correction radius to force a pass."

The second F3-T2 verifier weighed all of this and **passed** the Spec axis on it
deliberately. That judgment is respected here.

### What is genuinely left

One thing, and it is real under the guardrail adopted this same day ("a test
must assert something that would break if the behaviour were removed"):

Because `speakerA_live` is a **sub-window of the reference audio**, any
content-derived embedding scores the pair as near-identical. So
`test_same_speaker_accepts` passes largely independent of whether the speaker
model works — run 1's F3-T2 verifier reported that substituting a plain 192-bin
log-magnitude spectrum, with no speaker modelling at all, still yields d≈0.003
and an accept band. The different-speaker case has real teeth; the same-speaker
case does not.

- **Fix direction — cheap and non-invasive:** strengthen the *test*, not the
  cutoffs. Assert the same-speaker accept using the **byte-disjoint** pair the
  fixture set already guarantees (`enroll1` vs `enroll5`, documented as sharing
  zero audio), so the assertion can fail. Optionally add a Gate check that no
  probe is a subarray of any reference, so a future fixture edit cannot silently
  reintroduce the vacuity.
- **Explicitly NOT proposed:** re-pinning `ACCEPT_CUTOFF` or
  `CORRECTION_RADIUS`. Those were pinned via the multi-window study in the
  README, including a zero-overlap pair, and the fixture limits are disclosed.
  Changing measured constants is a spec-level measurement task, not a curate
  finding.
- **Roadmap fit:** F9, or fold into whichever feature next touches the fixtures.

## 3. Process defect: the bookkeeping commit was skipped in F1-T2 and F3-T2 (historical, closed)

Both build commits are `HEAD` with no following state-only commit, so
`handoff.md` at the build commit still describes the **previous** task and
records no base/head for the task under review.

Same defect class as `FAILURES.md`'s 2026-07-15 entry (batched task state) and
the F3-T3 entry in `memory/deviations.md`. It stopped after F3 — F2-T3, F4,
F4.5 and F5 all have proper bookkeeping commits — so this is closed history, not
an open action.

**It is why run 2 exists in the shape it does:** run 1 checked the worktrees out
at the build commit, and the missing handoff tripped the Gate. See the run-2
record's confound section.

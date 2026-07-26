# Spec: F4 — Voice as the middle lock (stacked)

Feature: Feature 4 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file) — re-scanned after the 2026-07-26 amendment, still zero hits
- [ ] Approved by human

- **Mode:** Mode 3 (Spec-to-done). Set by the human at grilling 2026-07-23. The
  security-critical crypto keystone (§4) is still locked in this spec via a
  TECH-PICK + human approval BEFORE any building — Mode 3's autonomy is bounded to
  an already-approved design.

- **AMENDMENT 2026-07-26 (box 2 re-opened, awaiting the human's `x`):** the §4
  reconcile pipeline and the §3 unlock/enroll capture lines are refined with five
  accuracy levers agreed with the human this session — bigger LSH expansion masked
  down to the same ~512 reliable bits, cross-take unanimity as the stability
  filter, confidence-weighted (soft-decision) majority decoding, a deliberately
  short key traded for repetition depth, and a longer/window-averaged unlock take.
  **Scope, outcome, non-goals and the §5 Verification list are unchanged** — this
  amendment changes only HOW the reconcile is built. Nothing may be built until
  the human re-checks box 2. Rationale: `memory/decisions.md` 2026-07-26.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Make the **voiceprint** a real cryptographic lock, not just an on-screen meter.
**Fuzzy-reconcile** the enrolled voiceprint into a **stable key** (with non-secret
**helper data**) and use it to seal a **middle lock** — an AEAD layer wrapping the
existing F2 **outer** (passphrase) lock's sealed box. After F4 the profile Vault
is sealed by **two nested locks**: passphrase (outer) around voice (middle) around
the payload. Unlock now requires the passphrase **and** the enrolled speaker's
voice: the outer lock peels with the typed passphrase, then the middle lock peels
only when a fresh voiceprint reconciles (via the helper data) to the enrollment
key.

Demo (the three impostor outcomes, each **visibly distinct**):
- right passphrase **and** the enrolled person's voice → **unlocked** (display name shown);
- **wrong passphrase** → REJECT at the **outer** lock ("wrong passphrase");
- right passphrase but a **different person's voice** → REJECT at the **middle**
  lock ("voice did not match").

## 2. Grilling record — ambiguity scan

**Status: CLEAR** — every category resolved; zero clarification markers remain
(2026-07-23, after grilling; re-scanned 2026-07-26 after the §3/§4 accuracy-lever
amendment — the changed sections introduced no new ambiguity and no markers).

| Category                           | Verdict | Resolved by |
| ---------------------------------- | ------- | ----------- |
| Functional scope & behavior        | Clear   | Voice = middle lock; unlock needs passphrase + voice; enroll = 5-sentence averaged capture; unlock = passphrase + one utterance, identity-only. |
| Domain & data model                | Clear   | Hand-rolled numpy code-offset fuzzy commitment (§4); helper data **inside** the outer box; nested **v2** vault layout; v1 refused with re-enroll. |
| Interaction & UX flow              | Clear   | Enroll voice capture + unlock voice capture + two **distinct** reject messages (`auth_outer` / `auth_voice`); F3 diagnostic panel kept as-is. |
| Non-functional (perf, security)    | Clear   | Offline + Argon2id/PyNaCl inherited; reconcile tolerance pinned empirically from fixtures (§4); honest limits written (§3/§4). No new dependency. |
| Integration & dependencies         | Clear   | **No new dependency** — hand-rolled in numpy (research `memory/research/2026-07-23-f4-fuzzy-reconcile.md`; decision logged). No TECH-PICK triggered. |
| Edge cases & failure modes         | Clear   | Reuse F1 mic-error + F3 "need more audio"; no-vault → enroll first; wrong-passphrase → outer REJECT; wrong-voice → middle REJECT; v1 vault → re-enroll. |
| Completion signals                 | Clear   | §5 pinned: fixture tests (same→unlock / different→middle REJECT / wrong-pass→outer REJECT / distinct-reject + no-leak / v1 refused) + required live Booth manual demo. |
| Terminology (matches `CONTEXT.md`) | Clear   | Vault · Outer lock · Middle lock · Voiceprint · Helper data · Enroll · Booth · Impostor (all already in `CONTEXT.md`). |

## 3. Non-goals

- **No face, camera, faceprint, inner lock, liveness, or challenge** (F5–F8). The
  voice at unlock is matched by **identity only** — there is no spoken-phrase
  challenge yet (that is F8), so this feature does **not** resist replay of a
  recording of the enrolled voice.
- **No enrollment-quality gate and no tolerance-tuning UI** (F9). F4 pins one
  fixed, provisional reconcile tolerance chosen empirically from fixtures.
- **No multi-profile** — a single Vault at `~/.voicelock/vault.vl`, as F2.
- **No account recovery** — lose the passphrase or the voice match → the Vault
  stays sealed (as the roadmap states).
- No claim of cryptographic hardness: biometric key binding for a **learning
  demo**, honestly framed. Helper data is **non-secret** and leaks bounded
  information about the voiceprint; the middle key is only as strong as the
  voiceprint's entropy and the chosen reconcile tolerance (stretched by Argon2id)
  — **not product-grade**. There is a small false-reject rate and a non-zero
  false-accept risk for a very similar voice; F4 does not stop replay of the
  enrolled voice (that is F8); no FAR/FRR guarantees.
- Out-of-scope discoveries during build: record in `.out-of-scope/`, never build.

### Interaction & UX flow

**Enroll flow (RESOLVED 2026-07-23; capture quality refined 2026-07-26):** enroll
becomes name + passphrase + a **5-sentence voice capture** (suggested sentences
shown to read; each take embedded, a too-short/silent take rejected with F3's
"need more audio", the valid takes averaged), producing the middle-lock helper
data. **Sentence quality (2026-07-26 amendment):** the five prompts are full
sentences of roughly 3–5 s each (not fragments) and are **phonetically varied and
vowel/voiced-heavy** — vowels and voiced consonants carry the speaker-identity
signal, unvoiced fricatives carry much less. The count stays **five** (the
human's 2026-07-23 choice); only their length and wording improve. The reader is
asked for one **consistent, natural** speaking voice across all five —
deliberately varying emotion, pitch or vocal effort is explicitly **rejected**,
because it widens the spread between takes and directly degrades the cross-take
stability filter in §4. The voice binds the
middle key at enroll; this is the vault's enrollment voiceprint and **supersedes**
F3's plaintext diagnostic reference for lock purposes.

**F3 diagnostic panel (RESOLVED 2026-07-23):** keep the existing F3 live-match
meter / "Set reference" / "Reset" panel **as-is** — an independent diagnostic that
still writes the plaintext `~/.voicelock/voiceprint.ref`, separate from the lock.
Least churn/risk in a crypto-heavy feature; the meter still visualizes close-vs-far.
The F4 demo path uses the new enroll/unlock voice capture, not the F3 diagnostic.
Keep F1 Record/Stop/Play unchanged.

**Unlock flow (RESOLVED 2026-07-23; take quality refined 2026-07-26):** unlock =
type passphrase + record **one** short utterance (any speech; identity-only, no
challenge phrase). **Take quality (2026-07-26 amendment):** it stays ONE recording
and one user action, but the Booth asks for a full sentence and the engine
requires meaningfully more speech than F3's 0.4 s diagnostic floor (a raised
F4-specific minimum, pinned as a module constant); the single take is embedded as
the **average of 2–3 overlapping windows** rather than one point sample. Reason:
enrollment averages five takes while unlock had only one, so the unlock side was
the noisier half of the comparison and was inflating the reconcile error rate.
The bridge peels
**outer first, then middle**, returning a distinct reason per failure so the Booth
shows two **visibly distinct** messages:
- outer decrypt fails → `auth_outer` → "Wrong passphrase";
- outer opens but the voice fails to reconcile / middle decrypt fails → `auth_voice`
  → "Voice didn't match".
A too-short/silent unlock take → F3's "need more audio" **signal** (reused copy
and error path), now measured against F4's raised minimum, re-record (no penalty).
Right passphrase + enrolled voice → **unlocked** (display name shown).

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv; engine/crypto
  in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in `tests/`; **Python owns
  all crypto/DSP, JS renders only**; **offline-only — no network at runtime**.
- Entry point remains `uv run voicelock` (Booth window). Keep F1 Record/Stop/Play
  and the F3 voiceprint engine (`voiceprint.py` — `embed`, cosine, cutoffs)
  unchanged as the identity source.
- Reuse the F2 outer lock unchanged: PyNaCl Argon2id + SecretBox, `vault.py`. The
  middle lock is a second AEAD layer using the same primitives with a
  voice-derived key.

**Keystone — the fuzzy-reconcile construction (RESOLVED 2026-07-23, human-approved):**

Hand-rolled **code-offset fuzzy commitment** in **pure numpy — NO new dependency**
(the recognized Juels–Wattenberg / fuzzy-extractor construction; research
`memory/research/2026-07-23-f4-fuzzy-reconcile.md`, decision in `memory/decisions.md`).
The pipeline, all Python-owned:
- **Binarize + expand (refined 2026-07-26):** a seeded random-hyperplane **LSH**
  projection binarizes the 192-dim L2-normalized ECAPA embedding (the projection
  seed is non-secret helper data). Raw 192 sign-bits give ~25% genuine bit-error —
  too high — so expansion + masking is required, not optional. **Project to a
  LARGE candidate pool (~2048–4096 bits) and mask it down to ~512 reliable bits**,
  rather than projecting straight to ~512. Same final bit count, far higher
  selection pressure: keeping the best 1-in-8 candidates is a much stronger filter
  than keeping 1-in-2, and the pool costs nothing at rest because only the seed is
  stored. Exact pool and kept-bit sizes are pinned empirically (see Reconcile
  tolerance below).
- **Reliability mask (refined 2026-07-26):** keep only the most stable bits,
  learned at enrollment **across the five individual takes** — the primary filter
  is **cross-take sign unanimity** (a bit must come out the same way in all five
  takes), with large projection margin as the ranking tiebreak among the
  survivors. Unanimity is a direct measurement of stability under exactly the
  within-speaker variation we must survive; margin alone is only a proxy for it.
  Target: genuine bit-error down toward ~10–15%. The kept-bit mask is non-secret
  helper data.
- **Inner code (refined 2026-07-26):** a **repetition ECC with confidence-weighted
  (soft-decision) majority decoding** over the reliable bits. Enroll picks a random
  secret `s`, encodes it to codeword `c`, stores helper `P = b XOR c` plus `H(s)`.
  Unlock computes `b' XOR P` and decodes each secret bit by summing its copies'
  **signed projection magnitudes** (confidence-weighted) instead of counting hard
  sign votes, succeeding iff `H(s)` matches (same speaker within the correction
  radius). A near-zero-margin measurement is close to a coin flip and must not
  outvote a large-margin one; hard voting throws that information away for free.
  Plain hard-decision majority remains the fallback if soft decoding does not
  measurably help on the fixtures.
- **Key (refined 2026-07-26):** the recovered `s` is stretched via Argon2id/HKDF
  into a PyNaCl SecretBox key for the **middle lock**. Modest secret entropy is
  acceptable for a labeled learning demo (honest limits below); the KDF does the
  stretching. **Deliberately prefer a SHORT secret (tens of bits) over a long one**
  — the reliable-bit budget is split between key length and repetition depth, and
  depth is what absorbs genuine noise (e.g. 512 reliable bits as a 32-bit key
  repeated 16× is far more robust than a 128-bit key repeated 4×). This is sound
  here because the middle lock sits INSIDE the passphrase lock: the voice key is
  never attacked directly until Argon2id on the outer lock has already fallen.
- **Rejected:** `bchlib`/`reedsolo` (both fail the ~12-month liveness bar), and
  `komm`/`galois` (live but add a dependency for only the easy last step). A new
  dependency was considered and declined — no TECH-PICK is triggered.

**Helper-data storage + v2 vault layout (RESOLVED 2026-07-23):** helper data lives
**inside the outer-passphrase box** — a deliberate refinement of the roadmap's
high-level "sibling" sketch. Nested SecretBox layout, format **version bumped
v1 → v2**:
- innermost plaintext = the profile JSON (`{name, schema_version}`, as F2) →
  sealed with the **voice-derived middle key** → **middle ciphertext**;
- outer plaintext = JSON `{helper_data, middle_ciphertext}` where `helper_data` =
  {LSH seed, reliability-bit mask, XOR offset `P`, `H(s)`} → sealed with the
  **passphrase-derived outer key** (F2's Argon2id + SecretBox, unchanged);
- on-disk file = `VLCK` magic + **version 2** + opslimit + memlimit + salt +
  outer ciphertext.
This hides the (non-secret) helper data at rest and orders the rejects: peel outer
(passphrase) first → then reconcile + peel middle (voice).
**v1 back-compat (RESOLVED):** a pre-existing F2 **v1** vault has no voice layer;
F4 unlock **refuses it with a re-enroll prompt** ("this vault predates voice —
re-enroll to add the voice lock"). No passphrase-only bypass, so "voice is now
required" stays true. Enroll always writes v2.

**Reconcile tolerance (RESOLVED 2026-07-23; knob list extended 2026-07-26):** the
correction radius is the "how close is close enough" knob — the analog of F3's
ACCEPT/REJECT cutoffs. It and every sizing knob beside it — **LSH candidate-pool
size · kept reliable-bit count · repetition factor · secret-key length · the
raised unlock minimum** — are pinned **empirically from the fixtures** as module
constants the tests import, so that same-speaker takes reconcile (unlock succeeds)
and a clearly-different speaker does not (middle REJECT) — deterministic, not
judgment. One fixed, provisional set for F4; the full tolerance-tuning UI +
enrollment-quality gate stay **F9**.

**Fixture-vs-reality caveat (2026-07-26):** the committed speaker-A source audio
is only ~3.3 s in total, so fixture "takes" are ~1 s each — materially SHORTER and
noisier than the 3–5 s sentences a real enrollment produces. The fixtures are
therefore a HARDER test than the live demo, which is a safe direction to be wrong
in, but it means a failure to separate on fixtures may indict the fixtures rather
than the construction. If tuning cannot separate the clusters, the first thing to
question is fixture length — not the approach — and the honest remedy is better
fixture audio, not a widened radius. Widening the radius until the demo "works"
is forbidden: a voice lock that accepts everyone is worse than none, because it
looks like security.

**Accuracy levers (RESOLVED 2026-07-23; extended 2026-07-26):** maximize honest-
voiceprint stability so the you-vs-different clusters sit far apart —
**5-sentence averaged enrollment** (human chose richer than F3's 3 takes), the
reliability mask above, and LSH bit-expansion. Enrollment shows suggested
sentences to read; a per-take "need more audio" floor rejects a silent/too-short
take. The five levers agreed 2026-07-26 (human-approved; rationale in
`memory/decisions.md`) are, in order of expected effect: (1) confidence-weighted
soft-decision decoding; (2) cross-take unanimity as the reliability filter;
(3) a large LSH candidate pool masked hard down to ~512 bits; (4) a short key
traded for repetition depth; (5) longer, window-averaged captures on BOTH sides.
A sixth — embedding centering / mean-subtraction — is **test-only, low
confidence**: check whether the vendored model's `mean_var_norm_emb.ckpt` already
applies it and measure, but do not depend on it (we have two fixture speakers, far
too few to estimate a background mean properly). **Explicitly rejected:**
deliberately varying emotion / pitch / vocal effort across the enrollment takes —
it sounds like useful coverage but widens the between-take spread, which starves
the unanimity filter and leaves the unlock voice at the edge of the enrolled range
instead of its centre. Enrollment and unlock should sound like the same person in
the same conditions (same natural voice, mic, distance, room). Accepted honest limits (not
product-grade): a small false-reject rate, a non-zero false-accept for a *very*
similar voice, and — because F4 has no challenge phrase — a **recording of the
enrolled voice still passes** (replay is defended in **F8**). No FAR/FRR guarantees.

- Booth UX: reuse existing mock chrome; add the enroll voice-capture step and the
  unlock voice-capture step; keep Record/Stop/Play and the F3 diagnostic panel
  unchanged; two distinct reject messages (outer vs middle), per §3.
- Edge cases (visible, no crash): no vault → "enroll first"; wrong passphrase →
  outer REJECT; right passphrase + wrong voice → middle REJECT; short/silent take
  → F3 "need more audio"; no mic → F1 mic-error path; v1 vault → re-enroll prompt.
- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
  `uv run pytest` → exit 0.
- **No new dependency** — F4 is built on the existing ECAPA + PyNaCl + numpy stack;
  nothing installed without a fresh TECH-PICK + human sign-off.

## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Harness rules find this
section by its NAME ("Verification"). Two parts, both required.

Runtime budget: `uv run pytest` loads torch + the vendored ECAPA model (up to
~2 min first run) plus Argon2id KDF cost (the middle lock adds a second KDF).
Whole-suite budget: within the 10-minute default (declare a longer budget here
only if that proves false during build).

Standing (project regression net, from `project.md`), pinned:
- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed — existing suite still green)

Feature-specific (proves THIS feature works), pinned:

- `uv run pytest tests/test_middlelock.py -q` → exit 0; final summary reports 0
  failed. Must cover, using fixed audio fixtures + the **vendored** ECAPA model
  loaded fully offline (`HF_HUB_OFFLINE`, no network), and a temp vault path:
  (1) **enroll** binds a middle key from the (5-take averaged) enrollment
  voiceprint, emits helper data (LSH seed + reliability-bit mask + XOR offset `P`
  + `H(s)`), and seals a nested **v2** vault (`VLCK` magic, version byte = 2);
  (2) **same-speaker** unlock voiceprint reconciles → `H(s)` matches → the middle
  lock opens → the enrolled display name is returned;
  (3) **different-speaker** voiceprint fails to reconcile → **middle REJECT**
  (`auth_voice`) and **no name/plaintext** is returned;
  (4) **wrong passphrase** → **outer REJECT** (`auth_outer`) and **no name** —
  raised **before** the voice is ever consulted (peel order: outer then middle);
  (5) the reconcile tolerance (correction radius / reliability params) are
  module-level constants the test imports — same-speaker fixtures reconcile and a
  clearly-different speaker does not, with a margin (deterministic, not judgment);
  (6) a pre-existing **v1** vault is **refused** with the re-enroll signal (no
  passphrase-only open);
  (7) **no-leak / helper-data-at-rest:** neither reject path returns the name, and
  the raw v2 file bytes do not expose the reference embedding or the middle
  plaintext (helper data sits inside the outer ciphertext).

- `uv run pytest tests/test_booth_api.py -q` → exit 0; final summary reports 0
  failed. Must cover (using a temp vault path + stub/fixture capture, no real mic):
  the bridge **enroll** captures the 5 takes and seals the nested v2 vault; the
  bridge **unlock** returns **distinct** reasons — `auth_outer` for a wrong
  passphrase vs `auth_voice` for a wrong voice — and neither returns the name.

Proof surface: the highest real surface F4 touches is the live pywebview Booth.
Automated tests prove the Python crypto path on fixtures; they do **not** drive the
real window or a live mic — that gap is covered by the required manual line below
(a required check, not accepted risk).

- Manual (required for F4 done — Verification check): run `uv run voicelock` →
  **enroll** (name + passphrase + read the 5 sentences) → **unlock** with the right
  passphrase + the enrolled voice → **unlocked** (name shown); **wrong passphrase**
  → **outer REJECT** ("Wrong passphrase"); a **different person** speaks with the
  right passphrase → **middle REJECT** ("Voice didn't match"). Each reject names
  its distinct cause.
  Observable: real-mic enroll seals a v2 vault, the genuine speaker unlocks live
  (real cross-recording, not a fixture), and the two impostor classes separate
  into two **visibly distinct** rejects.

**Mode 3 "if every gate passed but it were still wrong" (RESOLVED 2026-07-23):**
the fixture tests prove the crypto + fixture-level separation but cannot prove
real-mic **cross-session robustness** (enroll today / unlock later on another mic),
which is why the live manual demo above is **required** (a required check, not
accepted risk). The second failure mode — the two rejects silently collapsing or a
reject leaking the name — is caught by the automated **distinct-reject / no-leak**
checks (cases 3, 4, 7 above + the booth-api distinct-reason case). Known
limitation, recorded: fixture same-speaker probes overlap the enrollment takes
(inherited from F3), so automation cannot prove cross-session generalization — the
manual demo mitigates it.

Out-of-scope discoveries during build (Mode 3 default): record in `.out-of-scope/`,
never build.

---

*Spec-anchored: amendments follow the F2/F3 path — update this file, re-scan
changed sections, human re-checks box 2, re-plan.*

# Spec: F7 — Face as the inner lock (innermost)

Feature: Feature 7 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [x] Approved by human

- **Mode: Mode 3 — Spec-to-done.** Set by the human 2026-07-27. Build↔verify
cycles and the feature-end wrap-up run unattended within this feature; the
human is checked in with at the feature-end checkpoint (final-verdict
review + commit/push approval). Mode 4 was mechanically unlocked (F6
completed cleanly at Mode 3) but not chosen.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Make the **faceprint** a real cryptographic lock, not just an on-screen meter.
**Fuzzy-reconcile** the enrolled faceprint into a **stable key** (with non-secret
**helper data**) and use it to seal an **inner lock** — a third, innermost AEAD
layer wrapping F4's voice middle lock, which already wraps F2's passphrase outer
lock. After F7 the profile Vault is sealed by **three nested locks**: passphrase
(outer) around voice (middle) around face (inner) around the payload. Unlock now
requires the passphrase **and** the enrolled speaker's voice **and** the enrolled
person's face: the outer lock peels with the typed passphrase, the middle lock
peels only when a fresh voiceprint reconciles to the voice key, and the inner
lock peels only when a fresh faceprint reconciles to the face key.

Demo (four impostor outcomes, each **visibly distinct**):

- right passphrase **and** the enrolled voice **and** the enrolled face →
**unlocked** (display name shown);
- **wrong passphrase** → REJECT at the **outer** lock ("wrong passphrase");
- right passphrase but a **different person's voice** → REJECT at the **middle**
lock ("voice didn't match");
- right passphrase **and** the enrolled voice but a **different person's face**
→ REJECT at the **inner** lock ("face didn't match").

This is F4's construction, one lock layer deeper, for the face instead of the
voice — the same keystone (code-offset fuzzy commitment), reparameterized for
SFace's 128-dim embedding instead of ECAPA's 192-dim one. F6's diagnostic
faceprint meter is untouched by this feature — it stays an independent,
non-lock diagnostic exactly as F3's voiceprint meter survived F4 untouched.

## 2. Grilling record — ambiguity scan

**Status: CLEAR.** All four must-answer markers resolved interactively with
the human (2026-07-27) — a search for the `NEEDS-CLARIFICATION` token returns
zero hits in this file.


| Category                           | Verdict      | State                                                                                                                                             |
| ---------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Functional scope & behavior        | **Resolved** | Face = inner lock; unlock needs passphrase + voice + face; four visibly distinct outcomes (§1).                                                   |
| Domain & data model                | **Resolved** | Q3 — vault v3, v1/v2 both refused, re-enroll required. Q2 — sizing knobs reused from F4, radius measured on thin fixture data.                    |
| Interaction & UX flow              | **Resolved** | Q4 — new enroll/unlock face-capture steps, F6's diagnostic panel untouched.                                                                       |
| Non-functional (perf, security)    | **Resolved** | Offline + Argon2id/PyNaCl inherited from F4; no new dependency (construction already proven, `memory/research/2026-07-23-f4-fuzzy-reconcile.md`). |
| Integration & dependencies         | **Resolved** | New `facelock.py` sibling module to `middlelock.py` (Q1/Q2's resolutions assume this); no new dependency.                                         |
| Edge cases & failure modes         | **Resolved** | Reuse F6's `NoFaceError`/no-reference path; wrong-face → inner REJECT; v1/v2 vault → re-enroll (Q3).                                              |
| Completion signals                 | **Resolved** | Q1 — reuse F6's 3-take pattern + A1/A2/B fixtures, thin-evidence radius disclosed. Q2 — F4's constants reused, radius measured.                   |
| Terminology (matches `CONTEXT.md`) | **Clear**    | Uses **Inner lock**, **Faceprint**, **Helper data**, **Vault**, **Impostor** exactly as the glossary defines them. No new terms.                  |




### The questions

**Q1 — How many live enrollment takes does face-lock enrollment need, and what
proves the construction works, given this repo has far less independent face
data than voice does?**

F4's reliability mask is built on **cross-take sign unanimity** across 5
separately-spoken sentences — real, meaningfully-varied samples of the same
speaker. F6's Q4 already flagged the face analog is weaker: "three frames
captured seconds apart are far more correlated than three separate spoken
sentences." Two compounding problems for F7:

1. **Live enrollment.** If face-lock enrollment averages/masks across N frames
  from one short live-camera burst, those frames are nearly identical pixels —
   cross-take unanimity would come out ~100% unanimous almost regardless of N,
   which defeats the mask's purpose (it is supposed to measure genuine
   within-person variation, not rubber-stamp near-duplicate frames).
2. **Automated Gate test data.** F6's Q1 research found exactly ONE genuine
  independent same-person pair in this repo (Douglass A1/A2) and forbade
   deriving a second "take" by cropping/rescaling/re-encoding one image — that
   is the exact vacuous-test failure F5.5 was created to remove. F7's Gate test
   needs to prove the REAL construction (fuzzy commitment, not just `compare()`)
   separates same-face from different-face — but multi-take cross-take-unanimity
   masking has no honest multi-take face data to run on beyond one pair.

**RESOLVED (2026-07-27, human-approved).** Reuse existing data rather than
commissioning new `research`:

- **Live enrollment** reuses F6's already-established `REFERENCE_TAKES = 3`
burst pattern (same Booth code path, no new UX invented for this).
- **Automated Gate test** enrolls with **A1 alone** (a single genuine take —
`middlelock.py`'s own `_reliability_mask` docstring already documents
graceful degradation to pure margin-ranking when there are too few unanimous
candidates, so this is an anticipated fallback, not a hack), then tests
reconcile with **A2** (genuinely independent, never seen at enroll) for the
accept case and **B** for the reject case. No derived probes, no new
fixtures.
- **Disclosed honestly** (module docstring + this spec): the Gate test enrolls
with fewer genuine takes (1) than live production (3) — a thinner test than
production, in the opposite direction from F4's own disclosed fixture
caveat ("fixtures are a harder test than the live demo"). The required live
manual check (§5) is what actually exercises real 3-take enrollment.
Resolved by: human decision (declined the research-first alternative).

**Q2 — Sizing knobs for the face fuzzy commitment (candidate bits, reliable
bits, key bits, repetition, correction radius) — measured, adopted from F4 by
ratio, or something else?**

F4's `CORRECTION_RADIUS = 110` (and its sibling constants) were measured
empirically over 200 independent commits on many voice fixture comparisons.
F6's Q5 already established that face has nowhere near that much comparison
data (two comparisons total), which is why F6's diagnostic cutoffs were
*adopted* from OpenCV's vendor numbers rather than measured. F7's fuzzy
commitment has no equivalent vendor-published operating point to adopt — it is
a bespoke construction, so "adopt a published number" is not available the way
it was for F6's diagnostic.

**RESOLVED (2026-07-27, human-approved).** `CANDIDATE_BITS`, `RELIABLE_BITS`,
`KEY_BITS`, and `REPETITION` are kept **identical** to F4's values (4096, 512,
32, 16) — these size the ECC bit-budget, not the input embedding width, so
there is no real mathematical reason to scale them by 128/192. Only
`CORRECTION_RADIUS` is set from actual measurement using Q1's fixture plan:
the residual-bit count for the one genuine pair (enroll A1, reconcile against
A2) versus the residual-bit floor for the impostor cases (reconcile against
B) — midpoint of that gap, same method F4 used to pick 110 from its 63..156
gap. **Disclosed explicitly** (module docstring + here): this radius rests on
n=1 genuine and n=2 impostor measurements, categorically thinner evidence than
F4's 200-commit measurement — a real measurement, not an invented number, but
a weak one, and the code says so.

**Q3 — Vault format bump and legacy handling — v2 → v3, and what happens to an
existing v1 or v2 vault?**

F4 bumped v1 → v2 and refused v1 outright (`LegacyVaultError`, re-enroll
required, no passphrase-only bypass). F7 needs the same shape one layer
deeper: v2 → v3, nesting `{helper_data_face, inner_ciphertext}` inside the
existing middle layer.

**RESOLVED (2026-07-27, human-approved).** Bump to `FORMAT_VERSION = 3`. Both
a v1 **and** a v2 vault are refused via the same `LegacyVaultError` family
(the message names the actual missing layer — "predates voice" vs. "predates
face") — re-enroll required, no bypass, mirroring F4's precedent exactly.
Layout: innermost profile JSON → sealed with the **face-derived inner key** →
inner ciphertext; middle plaintext becomes `{helper_data_face, inner_ciphertext}` → sealed with the **voice-derived middle key** (unchanged
from F4) → middle ciphertext; outer plaintext `{helper_data_voice, middle_ciphertext}` → sealed with the passphrase key (unchanged). Peel order
stays outer → middle → **inner**, so each impostor class fails at its own
named layer before the next is ever consulted.

**Q4 — Booth enrollment flow — where does live face-lock enrollment fit
relative to F6's existing diagnostic panel?**

F4 precedent: keep F3's voiceprint diagnostic panel completely untouched, and
add a **separate** enroll-voice capture step to the enroll flow. F6's
diagnostic faceprint panel (3-band meter, "Set face reference", "Reset")
already exists and writes `~/.voicelock/faceprint.ref` — a plaintext,
non-lock file, independent of anything F7 seals into the vault.

**RESOLVED (2026-07-27, human-approved).** Mirror F4 exactly — F6's
faceprint diagnostic panel stays untouched (still writes its own plaintext
reference file, still an independent diagnostic, still not consulted by the
lock). F7 adds a **new**, separate enroll-face capture step to the enroll
flow (after the existing enroll-voice step), whose captured frames (F6's
`REFERENCE_TAKES = 3` pattern, per Q1) are consumed only by `facelock.commit`
and never touch `faceprint.ref`. Unlock's face capture (reusing
`FaceEngine.last_frame`) feeds `facelock.reconcile`, distinct from the
diagnostic's separate `compare_face` polling loop. Two independent code paths
reading the same camera, exactly as voice's diagnostic vs. lock paths are two
independent code paths reading the same microphone.

## 3. Non-goals

- **No liveness, challenge phrase, or lip-sync** (F8). Face-at-unlock is
matched by **identity only** — F7 does not resist replay of a photo/video of
the enrolled person's face (that is exactly F8's job, and F6's §6 blind spot
already disclosed this in the Booth copy).
- **No enrollment-quality gate and no tolerance-tuning UI** (F9). F7 pins one
fixed, provisional set of fuzzy-commitment constants (Q2), the same way F4
pinned a fixed `CORRECTION_RADIUS`.
- **No re-pinning of any voice constant** — `middlelock.py`'s
`CORRECTION_RADIUS`, `CANDIDATE_BITS`, etc. and `voiceprint.py`'s
`ACCEPT_CUTOFF`/`REJECT_CUTOFF` stay untouched. F7 adds a face-specific
sibling module; it does not edit the voice one.
- **No change to F6's diagnostic faceprint panel or** `faceprint.ref` — Q4
keeps it as an independent, non-lock diagnostic.
- **No multi-profile** — a single Vault at `~/.voicelock/vault.vl`, as before.
- **No account recovery** — lose the passphrase, the voice match, or the face
match → the Vault stays sealed.
- No claim of cryptographic hardness: biometric key binding for a **learning
demo**, honestly framed, same as F4. Helper data is non-secret and leaks
bounded information about the faceprint; the inner key is only as strong as
the faceprint's entropy and the chosen reconcile tolerance (stretched by
Argon2id) — not product-grade. No FAR/FRR guarantees.
- Out-of-scope discoveries during build: record in `.out-of-scope/`, never build.



## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv; engine/crypto
in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in `tests/`; **Python
owns all crypto/DSP, JS renders only**; **offline-only — no network at
runtime**.
- Entry point remains `uv run voicelock`. Keep F1–F6 engines
(`capture.py`, `playback.py`, `voiceprint.py`, `middlelock.py`,
`facedetect.py`, `faceprint.py`) unchanged as the identity/detection sources
— F7 consumes `faceprint.embed_frame`/`embed_file`, it does not modify them.
- Reuse F2's outer lock and F4's middle lock unchanged: same PyNaCl Argon2id +
SecretBox primitives, same nested-AEAD pattern, one layer deeper (Q3).
- **No new dependency.** The code-offset fuzzy commitment construction is
already proven in pure numpy (`memory/research/2026-07-23-f4-fuzzy-reconcile.md`);
F7 reparameterizes it for a 128-dim embedding, it does not pick new tech.
- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
`uv run pytest` → exit 0.
- Booth UX: reuse existing mock chrome; add the enroll face-capture step and
the unlock face-capture step (Q4); keep F3/F6's diagnostic panels and F1
Record/Stop/Play unchanged; a third, visibly distinct reject message for the
inner lock, per §1.
- Edge cases (visible, no crash): no vault → "enroll first"; wrong passphrase
→ outer REJECT; right passphrase + wrong voice → middle REJECT; right
passphrase + right voice + wrong face → inner REJECT; no face detected during
enroll/unlock capture → F6's `NoFaceError` surfaced as Booth copy (not a
crash); v1 or v2 vault → re-enroll prompt (Q3).



## 5. Verification — definition of done (runnable)

Fixtures: reuses F6's already-committed `tests/fixtures/face/personA_1.jpg`
(A1), `personA_2.jpg` (A2), `personB.jpg` (B) — no new fixtures (per Q1).

**Standing** (the regression net — `project.md`'s Gate commands):

- `uv run ruff check .` → exit 0.
- `uv run pytest` → exit 0. Reference: **145 passing** at the end of F6; the
count rises by F7's tests and must not fall.

**Feature-specific:**

1. `uv run pytest tests/test_facelock.py -q` → exit 0. Must cover, using the
  real vendored SFace model + the A1/A2/B fixtures (no mocked embeddings):
  - **commit** binds an inner key from an enrollment embedding set (per Q1,
  A1 alone in the fixture test; `REFERENCE_TAKES = 3` live frames in
  production) and emits helper data (LSH seed, reliability mask, XOR
  offset, commitment tag) — same shape as `middlelock.commit`.
  - **same-person reconcile**: enrolling on A1 and reconciling against A2
  recovers the committed secret (inner lock opens).
  - **different-person reconcile**: enrolling on A1 (or A2) and reconciling
  against B fails to reconcile — `ReconcileError`-equivalent raised, no
  secret/plaintext returned.
  - `CANDIDATE_BITS == 4096`, `RELIABLE_BITS == 512`, `KEY_BITS == 32`,
  `REPETITION == 16` (reused unchanged from `middlelock`, per Q2) and
  `CORRECTION_RADIUS` sits strictly between the measured A1↔A2 residual
  and the measured A1/A2↔B residual floor — the test asserts the actual
  measured gap, not just that the constant exists.
2. `uv run pytest tests/test_vault.py -q` (or wherever F2/F4's vault tests
  live) → exit 0. Must cover: enroll seals a **v3** vault (`FORMAT_VERSION ==  3`, `VLCK` magic); unlock with the right passphrase + voice + face returns
   the display name; a wrong passphrase raises before voice or face is
   consulted (outer REJECT); right passphrase + wrong voice raises before
   face is consulted (middle REJECT, unchanged from F4); right passphrase +
   right voice + wrong face raises the new inner REJECT; a v1 **or** v2 vault
   is refused via `LegacyVaultError` naming the missing layer (Q3); no reject
   path returns the name or any plaintext.
3. `uv run pytest tests/test_booth_api.py -q` → exit 0. Must cover the
  bridge's enroll-face capture step (Q4) and unlock returning a **distinct**
   reason per layer (`auth_outer` / `auth_voice` / `auth_face`), none leaking
   the name.
4. **Manual (required)** — run `uv run voicelock`: enroll (name + passphrase +
  voice + face) → unlock with all three correct → **unlocked** (name shown);
   **wrong passphrase** → outer REJECT; right passphrase + **wrong voice** →
   middle REJECT; right passphrase + right voice + **a different face** →
   **inner REJECT**. Each reject names its distinct cause. Attested by the
   human at the feature-end checkpoint.

**Out-of-scope default (Mode 3):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

**"If every gate passed but the feature were still wrong, what would be wrong?"**

**RESOLVED (2026-07-27, human-approved).** The automated test (§5 cmd 1) only
proves the construction separates ONE genuine face pair (Douglass A1/A2, per
Q1's thin-evidence disclosure) from one impostor (B) — it cannot prove the
reliability mask generalizes to a real user's face across a genuine
cross-session gap (enroll today, unlock next week, different lighting/angle/
expression). This is the same generalization gap F4 already accepted for
voice, and it is mitigated the same way: not by a gate, but by the **required
live manual check** (§5 cmd 4) — enroll live, unlock live days or sessions
apart in practice, wrong-face live. The gates cannot catch this because the
gap is structural (thin fixture data), not a bug; the mitigation is disclosure
plus the human's own live exercise of the real path, exactly as F4's spec
recorded for the identical voice-side limitation.

## 7. What F7 inherits (recorded so it survives the next handoff rewrite)

- **From F4:** the entire fuzzy-commitment construction, the nested-vault
pattern, the distinct-reject-per-layer discipline, and the hard-won lesson
that reconcile tolerance must be justified by real measurement or explicit,
disclosed estimation — never tuned until the demo "looks like it works."
- **From F6:** `faceprint.embed_frame`/`embed_file`, the 128-dim SFace
embedding, `NoFaceError`, and the face-data scarcity problem (Q1) that F6's
own Q1/Q5 already surfaced and partially solved (one genuine same-person
pair, one different-person subject) but did not need to solve at F7's
depth — F6 needed one comparison's worth of separation; F7's reliability
mask needs multiple genuine per-person samples, a strictly harder bar.
- **From** `project.md`**:** the per-asset licence rule (if Q1 leads to a new
fixture), the no-unexercised-surface rule, the mutation-sensitivity rule,
and the dry-run-before-pinning rule (verify every concrete Verification
command against reality before it is written into this spec).


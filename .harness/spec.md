# Spec: F8 — Lip-sync liveness (challenge-response)

Feature: Feature 8 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [x] Approved by human

- **Mode: Mode 3 — Spec-to-done.** Set by the human 2026-07-28. Build↔verify
cycles and the feature-end wrap-up run unattended within this feature; the
human is checked in with at the feature-end checkpoint (final-verdict
review + commit/push approval). Same mode as F4 through F7. Mode 4 was
mechanically unlocked (F7 completed cleanly at Mode 3) but not chosen.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Make **liveness** real: each unlock attempt shows a fresh, random **challenge**
phrase, and the user proves — in **one webcam+mic AV capture** — that they are
the enrolled person, speaking, right now. A single capture is pulled apart into
four independent checks:

1. the **spoken words match the challenge** (defeats a pre-recorded clip of
   different words, or silence);
2. the **voiceprint matches** the enrolled voice (F4's middle lock, already
   built — reused, not rebuilt);
3. the **faceprint matches** the enrolled face (F7's inner lock, already
   built — reused, not rebuilt);
4. the **lips move in sync with the audio** over the challenge (defeats a
   still photo, an audio-only replay played at a face, or a muted video with
   different audio dubbed in).

After F8 the full impostor arc from `roadmap.md`'s original idea is reachable:
wrong passphrase, wrong voice, wrong face, and now a **replay/liveness**
failure each reject **visibly and distinctly**.

Demo (five outcomes, each visibly distinct):

- right passphrase + enrolled voice + enrolled face + live challenge speech →
  **unlocked** (display name shown);
- wrong passphrase → REJECT at the **outer** lock (unchanged from F2);
- right passphrase, different voice → REJECT at the **middle** lock
  (unchanged from F4);
- right passphrase, right voice, different face → REJECT at the **inner**
  lock (unchanged from F7);
- right passphrase, right voice, right face, but **liveness fails** (wrong
  words spoken, a replayed recording, a held-up photo, or a muted video) →
  REJECT at the **liveness** gate. **Resolved by precedent** (mirrors F7's
  `showWrongFace()`/`chip-wrong-face` pattern exactly): status text
  `"REJECT · LIVENESS CHECK FAILED"`, a new `chip-liveness-failed` chip
  reading `"Didn't look or sound live"`, sub-text naming that passphrase,
  voice, and face all already passed. Exact copy may be refined at `/plan`
  the way F7's chip wording was — not architecture, no further grilling
  needed.

**RESOLVED (2026-07-28, human-approved, Q6).** Liveness (challenge-word-match
+ lip-sync) is checked **before any lock layer is attempted**. Only once both
pass does the Booth bridge call `vault.unlock()` at all — peeling
outer→middle→inner exactly as today, using the same AV capture's voice/face
embeddings as the reconcile inputs. A liveness failure never touches the
vault, is its own distinct reject, and — symmetric with how a wrong
passphrase never reaches voice or face today — a replay attacker who fails
liveness learns nothing about whether the underlying voice/face would have
matched.

## 2. Grilling record — ambiguity scan

**Status: CLEAR.** All six content markers (Q1–Q6) resolved interactively
with the human (2026-07-28) — a search for the `NEEDS-CLARIFICATION` token
in this file now returns zero hits. (The Mode line in §0 and the Mode 2+
blind-spot question in §6 are set separately, per the `spec` skill's step 5 —
not ambiguity markers.)

| Category                           | Verdict      | State                                                                                                                                             |
| ----------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Functional scope & behavior        | **Resolved** | Liveness = words-match-challenge + voice + face + lip-sync, one AV capture, five visibly distinct outcomes (§1). Gate-ordering: liveness before any lock (Q6). |
| Domain & data model                | **Resolved** | Q1 — Vosk, grammar-constrained. Q4 — lag-windowed normalized cross-correlation for lip-sync.                                                       |
| Interaction & UX flow              | **Resolved** | Q2 — Record/Stop transport, fixed ceiling, phrase shown + stays visible. Q3 — small hand-authored phrase pool, no-immediate-repeat.                |
| Non-functional (perf, security)    | **Resolved** | Offline-only inherited; Vosk adds no new ML runtime; lip-sync is pure numpy.                                                                        |
| Integration & dependencies         | **Resolved** | Q1 (Vosk) · Q6 (liveness gates before outer/middle/inner) · AV capture reuses F1/F5's device threads, adds retention.                              |
| Edge cases & failure modes         | **Resolved** | Q5 — Gate fixture strategy: synthetic unit tests for both scoring functions + real-audio reject-path exercise for challenge-match; required live manual check covers the accept paths and the four replay/photo/muted-video impostor classes. |
| Completion signals                 | **Resolved** | §5 — what's automatable (reject paths, scoring-function correctness) vs. what stays a required manual check (accept paths, real impostor classes), disclosed rather than smoothed over.                                                        |
| Terminology (matches `CONTEXT.md`) | **Clear**    | Uses **Challenge**, **Liveness**, **Lip-sync**, **AV capture**, **Impostor** exactly as the glossary defines them. No new terms needed.             |

### The questions

**Q1 — How is "the spoken words match the challenge" verified — does this
need a new offline speech-recognition dependency, and if so, which one?**

**RESOLVED (2026-07-28, human-approved).** **Vosk**, with its
grammar-constrained recognition (`KaldiRecognizer(model, rate, grammar_json)`,
confirmed from the project's own GitHub issues) decoding directly against a
small JSON list of allowed challenge phrases — a purpose-built fit that avoids
open-vocabulary transcription plus fuzzy text matching entirely. Adds
**zero** new ML runtime (no torch/CTranslate2 dependency;
`cffi`/`requests`/`tqdm`/`srt`/`websockets` only); its small English model
(`vosk-model-small-en-us-0.15`, 40 MB) is Apache-2.0, established from the
model's own distribution page. **Disclosed and explicitly waived by the
human:** Vosk's own PyPI wheel has not been rebuilt since 2023-06-21 —
failing the ~12-month liveness bar on its face — but the underlying GitHub
repo has a commit from 2026-07-02 (26 days before the research), so the
project is not abandoned, only the published wheel is stale. Recorded in
`memory/decisions.md` per the TECH-PICK protocol. Full comparison:
`memory/research/2026-07-28-f8-offline-stt-challenge-match.md`.

**Q2 — How is the single AV (audio+video) capture triggered and bounded?**

**RESOLVED (2026-07-28, human-approved).** The challenge phrase is shown and
**stays visible** (folds in Q3's UI sub-question); the user presses **Record**
when ready (F1's existing transport button, unchanged interaction), speaks
the phrase, and the capture auto-stops at a **fixed ceiling** or an explicit
**Stop** press, whichever comes first — mirrors F1's Record/Stop pattern
exactly, no new interaction pattern. The ceiling's exact value is a `/plan`-
level sizing decision (per `project.md`'s dry-run-before-pinning guardrail,
measured against how long the chosen phrase pool actually takes to speak,
not guessed here) — provisionally ~6–8 s, generous for a short sentence,
confirmed or adjusted when the phrase pool (Q3) is finalized in code.

F1's audio Record and F5's camera preview already run concurrently in the
Booth (independent threads reading the same devices today), but neither
currently **retains** a time-aligned sequence — F5's camera loop composites
and displays frames live without keeping them, and F1's capture retains
audio only. F8's new capture path must retain both, aligned to one clock, for
the lip-sync check (Q4) — an implementation detail for `/plan`, not a further
grilling question, since the shape (reuse both existing device threads,
add retention) is now settled by this answer.

**Q3 — Where does the challenge phrase pool come from, and how is it shown
to the user?**

**RESOLVED (2026-07-28, human-approved).** A small, **hand-authored** list —
~10–20 short, phonetically varied sentences declared as a constant (mirrors
F4/F7's precedent of hand-picked, disclosed literal constants), one picked at
random per unlock attempt with no-immediate-repeat (never the same phrase
twice in a row). A bounded, hand-authored pool also fits Q1's Vosk
grammar-constrained decoding better than a programmatically generated
phrase would — the exact phrase set is exactly what gets passed as Vosk's
grammar. Booth UX for displaying the challenge text: **resolved by Q2** —
shown before Record and kept visible throughout the capture.

**Q4 — Lip-sync scoring: what signal, what construction, what threshold, and
how is the threshold justified given this repo has zero comparison data for
"lips out of sync"?**

**RESOLVED (2026-07-28, human-approved).** **Normalized cross-correlation,
lag-windowed.** Per-frame mouth-aperture (from F5's existing lip-contour
landmarks) correlated against the audio envelope (already computed for the
Visualizer) within a small lag window — mouth movement may lead or trail
audio slightly, so a fixed-lag comparison would be too brittle. No new
dependency; pure numpy; the same hand-rolled, glass-box approach F4/F7 used
for fuzzy commitment. The peak correlation score within the lag window is
the sync signal; **threshold sizing is Q5's territory** (what there is to
measure it against) — this only fixed the construction, not the number.

**Q5 — Automated Gate test strategy given zero AV fixtures exist in this
repo.**

**RESOLVED (2026-07-28, human-approved).** **Synthetic unit tests for the
scoring functions, plus the required live manual check for the real path.**
No new AV fixtures, no new fixture-licensing research. Concretely, per
signal:

- **Lip-sync**: the cross-correlation function (Q4) is tested against
  synthetic time series with a known, deliberately constructed
  relationship — an in-phase mouth-aperture series built directly from a
  real audio envelope (one of the existing voice fixtures) should score
  high; the same series shifted/decorrelated past the lag window, or
  replaced with a flat (non-moving-mouth) series, should score low. This
  proves the *math* — a real still photo or muted video in production is
  exactly the flat/decorrelated case the synthetic reject probes — not
  that it works on a real face's real video.
- **Challenge-word match**: real Vosk decoding is exercised where the
  repo's existing data already supports it honestly — the existing voice
  fixtures (`speakerA_*.wav`, `speakerB.wav`) almost certainly do not say
  any of the hand-authored challenge phrases (Q3), so running Vosk's
  grammar-constrained recognizer against them and asserting **reject** is
  a real, unmocked exercise of the reject path. The **accept** path (a
  real recording actually saying a challenge phrase) has no honest
  existing fixture — proven only by the required live manual check, same
  as the accept path for lip-sync and, going back further, the same gap
  F4/F7 always closed with a live check rather than synthetic accept data.
  Disclosed explicitly, not smoothed over: the automated Gate proves
  challenge-word-match can correctly REJECT on real audio; it cannot prove
  it correctly ACCEPTs without the manual check.
- This mirrors F6/F7's established shape ("the automated Gate proves the
  math; the required live manual check proves the real path") one notch
  further, since even the *reject* side needed care to stay honest here.

**Q6 — Gate-ordering: where does the liveness check sit relative to the
outer/middle/inner cryptographic layers?**

**RESOLVED — see §1.**

## 3. Non-goals

- **No strong deepfake / synced-video resistance.** Per `roadmap.md`'s
  standing honest framing: lip-sync liveness defeats a still photo, an
  audio-only replay, and a muted video — not a sophisticated video where the
  lips already match the dubbed audio. This is stated in the Booth copy, not
  just in `.harness/`.
- **No enrollment-quality gate or tolerance-tuning UI** (F9's job) — F8 pins
  one fixed, disclosed threshold for lip-sync and challenge-word matching,
  the same way F4/F7 pinned fixed fuzzy-commitment constants.
- **No change to F2/F4/F7's lock constructions** — `outerlock`, `middlelock`,
  `facelock`, and `vault.py`'s existing three-layer nesting are reused as-is;
  F8 adds a gate in front of/around them (per Q6), not a fourth AEAD layer.
  Voice and face identity are still proven the same way they always were —
  F8 adds *whose voice said what* and *did the mouth move with it*, not a new
  identity mechanism.
- **No re-pinning of any existing constant** — `ACCEPT_CUTOFF`,
  `CORRECTION_RADIUS` (voice or face), etc. stay untouched.
- **No multi-profile, no account recovery** — unchanged from every prior
  feature's non-goals.
- Out-of-scope discoveries during build: record in `.out-of-scope/`, never
  build.

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv;
  engine/crypto in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in
  `tests/`; **Python owns all crypto/DSP, JS renders only**; **offline-only —
  no network at runtime**.
- Entry point remains `uv run voicelock`. F1–F7 engines
  (`capture.py`, `playback.py`, `voiceprint.py`, `middlelock.py`,
  `facedetect.py`, `faceprint.py`, `facelock.py`, `vault.py`) are reused, not
  modified in their core constructions — F8 consumes their outputs (voice/face
  embeddings, lip landmarks, audio envelope) and adds new modules for the two
  new signals.
- **New dependency `vosk`** (Q1, human-approved TECH-PICK), vendored
  `vosk-model-small-en-us-0.15` (Apache-2.0, 40 MB) offline beside
  `models/ecapa/` and the Face Landmarker bundle, per the existing per-asset
  licence rule. Challenge-word matching uses Vosk's grammar-constrained
  recognition against the current attempt's phrase (and, per Q3, the rest of
  the pool as decoys where useful) — not open transcription.
- Lip-sync construction: no new dependency regardless of Q4's outcome — pure
  numpy over F5's existing lip-contour landmarks and F1's existing audio
  envelope.
- New sibling engine modules (exact call shapes left to `/plan`, naming fixed
  here so the Verification section below can name real files): `challenge.py`
  (the hand-authored phrase pool, Vosk model loading, and grammar-constrained
  match) and `lipsync.py` (the lag-windowed cross-correlation scorer). Both
  live beside `facelock.py`/`middlelock.py` in `src/voicelock/`.
- Booth UX: reuse existing mock chrome; add challenge-phrase display + the AV
  capture UX (Q2/Q3); keep F3/F6's diagnostic panels and F1
  Record/Stop/Play unchanged; a fifth, visibly distinct reject message for
  the liveness gate, per §1.
- Edge cases (visible, no crash): no vault → "enroll first" (unchanged); the
  existing outer/middle/inner REJECT edges (unchanged); no face/no speech
  detected during the AV capture → visible Booth copy, not a crash; a
  too-short or silent capture → visible Booth copy, not a crash.

## 5. Verification — definition of done (runnable)

Fixtures: reuses existing committed fixtures only — `tests/fixtures/voiceprint/*.wav` (for the real-audio reject-path exercise, Q5) — **no new fixtures** (per Q5's resolution: synthetic data + the existing voice fixtures cover the automated Gate; no new AV data is sourced or committed).

**Standing** (the regression net — `project.md`'s Gate commands):

- `uv run ruff check .` → exit 0.
- `uv run pytest` → exit 0. Reference: **186 passing** at the end of F7; the
  count rises by F8's tests and must not fall.

**Feature-specific:**

1. `uv run pytest tests/test_challenge.py -q` → exit 0. Must cover:
   - the hand-authored phrase pool (Q3) is a fixed, non-empty constant, and
     random selection never repeats the immediately-previous phrase across
     consecutive calls (exercised over enough draws to make a false failure
     statistically negligible);
   - Vosk's grammar-constrained recognizer, loaded from the vendored
     `vosk-model-small-en-us-0.15`, run for real (no mocked recognition)
     against `tests/fixtures/voiceprint/speakerA_take1.wav` (or another
     existing voice fixture) constrained to a specific challenge phrase's
     grammar, asserts **reject** — the fixture audio does not say that
     phrase, so a true positive there is not available to this repo's
     existing data, and the test's docstring says so explicitly (Q5's
     disclosed limitation) rather than silently asserting less;
   - the match/no-match decision function itself (independent of Vosk) is
     unit-tested against a synthetic "recognizer said X, challenge was Y"
     table covering an exact match, a case/punctuation-only difference (must
     still accept), and a genuinely different phrase (must reject).
2. `uv run pytest tests/test_lipsync.py -q` → exit 0. Must cover, using the
   **real** audio envelope from an existing voice fixture paired with
   **synthetic** mouth-aperture series (per Q5 — no real video needed to
   test the scoring math):
   - an in-phase synthetic mouth-aperture series (derived directly from the
     real audio envelope, e.g. a monotonic function of it) scores **above**
     `SYNC_THRESHOLD`;
   - the same series shifted outside the lag window, and a flat
     (non-moving) series, both score **below** `SYNC_THRESHOLD` — the flat
     case is the direct analog of a still photo or a muted video in
     production;
   - `SYNC_THRESHOLD` and the lag-window width are named constants, and the
     module docstring discloses that they are picked from this synthetic
     separation, not measured against real human lip-sync data — the
     required live manual check (cmd 4) is what actually exercises real
     synchrony.
3. `uv run pytest tests/test_booth_api.py -q` → exit 0. Must cover the
   bridge's new AV-capture flow (start/stop, retention, release-on-every-exit-
   path per `project.md`'s acquisition/release guardrail — including the
   fixed-ceiling auto-stop), the liveness gate running before `vault.unlock`
   is ever called (Q6 — assert a failed-liveness attempt makes zero calls
   into the vault layer), and the fifth reject reason
   (`auth_liveness`/equivalent) alongside the existing
   `auth_outer`/`auth_voice`/`auth_face`, none leaking the display name.
4. **Manual (required)** — run `uv run voicelock`: enroll (name + passphrase
   + voice + face) → unlock with all four correct (passphrase, voice, face,
   live spoken challenge) → **unlocked** (name shown); **wrong passphrase**
   → outer REJECT; right passphrase + **wrong voice** → middle REJECT; right
   passphrase + right voice + **wrong face** → inner REJECT; right
   passphrase + right voice + right face but **liveness fails** — tried at
   least two ways per §1 (e.g. speaking the wrong words, and one of: holding
   up a photo, playing a silent/muted video, or replaying a separate
   audio-only recording) → **liveness REJECT**. Each reject names its
   distinct cause. This is where the accept-path proof for challenge-match
   and lip-sync actually lives (per Q5's disclosed gap) — not optional,
   attested by the human at the feature-end checkpoint.

**Out-of-scope default (Mode 3+):** anything discovered during the build that
is not in §1 gets recorded in `.out-of-scope/` and is never built.

## 6. Mode 2+ blind-spot question

**"If every gate in this spec passed but the feature were still wrong, what
would be wrong?"**

**RESOLVED (2026-07-28, human-approved).** The automated Gate (§5 cmds 1–3)
can only prove the challenge-match **REJECT** path and the lip-sync scoring
**math** on synthetic data (Q5) — it cannot prove either signal correctly
**ACCEPTs** a real live person, or that lip-sync genuinely resists a
well-produced replay, because this repo has zero real synced audio+video
fixtures. The gates cannot catch this because the gap is structural (no
honest fixture exists, not a bug to fix); the mitigation is disclosure plus
the human's own live exercise of the real path — the required manual check
(§5 cmd 4), which explicitly walks all five outcomes including at least two
distinct liveness-failure modes. Same shape as F4's and F7's own disclosed
generalization gaps for voice and face respectively (spec §6 in each).

## 7. What F8 inherits (recorded so it survives the next handoff rewrite)

- **From F4/F7:** the discipline that a reconcile tolerance (here, a
  lip-sync threshold and an STT match tolerance) must be justified by real
  measurement or explicit, disclosed estimation — never tuned until the demo
  "looks like it works."
- **From F5:** the full 478-point landmark set, including the lip contour,
  was deliberately kept in `facedetect.py`'s output even though only a
  subset is drawn — F8 is the reason.
- **From F6/F7:** the no-repo-owner-biometrics-as-fixture precedent, and the
  general shape of "the automated Gate proves the math; the required live
  manual check proves the real path" for anything with thin or no real
  comparison data.
- **From `project.md`:** the per-asset licence rule (if Q1 leads to a new
  vendored model), the no-unexercised-surface rule, the mutation-sensitivity
  rule, the source-text-meaning rule, the dry-run-before-pinning rule, the
  every-acquisition-must-release rule (an AV capture acquires both mic and
  camera — every exit path, including timeouts, must release both), and the
  Booth-layout manual-smoke-test rule (a challenge-phrase display + capture
  UI is new visible content in the Booth column).

# Spec: F3 — Voiceprint on screen

Feature: Feature 3 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [ ] Approved by human

- **Mode:** Mode 3

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

**Amendment (2026-07-23) — box 2 re-opened, needs fresh approval.** Added a
**Reset** control to F3: clears the stored reference and restarts the 3-take
flow from scratch. Human-requested. Changes are in §1 (Outcome), §4
(Constraints — new "Reset reference" bullet), §5 (Verification — a bridge reset
test + a reset step in the manual demo), and the §2 Interaction/UX row. Mode
unchanged (Mode 3). Per the universal [Modes] rule an amendment needs a fresh
box-2 approval — re-check the box above after reviewing the changed sections.
Re-plan (adding Task 5 = Reset) happens only after that.

## 1. Outcome

Show the **voiceprint** working on screen. Compute a speaker embedding from
captured speech (the F1 mic path) and display a **live match distance** against a
stored **reference voiceprint** in the Booth, colored **accept** (close) vs
**reject** (far). This is a diagnostic only — **not wired into any lock**, no key
derivation, no vault change.
Demo: same person speaks → distance small / accept-colored; a different person
speaks → distance large / reject-colored.
A **Reset** action clears the stored reference and returns the Booth to the
no-reference state, so a fresh reference can be recorded from scratch.

## 2. Grilling record — ambiguity scan

**Status: CLEAR**


| Category                           | Verdict | Resolved by                                                                                                                  |
| ---------------------------------- | ------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Functional scope & behavior        | Clear   | compute voiceprint · show live distance vs reference · accept/reject color                                                   |
| Domain & data model                | Clear   | reference = 3-sentence averaged ECAPA embedding, persisted to `~/.voicelock/voiceprint.ref` (plaintext vector, not in vault) |
| Interaction & UX flow              | Clear   | "Set reference" action + **"Reset"** action (clears the reference + any in-progress takes, no confirm) + live 3-band meter (green/amber/red) in the Booth |
| Non-functional (perf, security)    | Clear   | model vendored in-repo + HF_HUB_OFFLINE; pytest model-load budget declared in §5                                             |
| Integration & dependencies         | Clear   | SpeechBrain ECAPA (human-approved TECH-PICK)                                                                                 |
| Edge cases & failure modes         | Clear   | no reference → prompt to set; short/silent → "need more audio"; no mic → F1 error path                                       |
| Completion signals                 | Clear   | 3-band cosine meter; fixtures assert same→accept / different→reject; manual Booth check                                      |
| Terminology (matches `CONTEXT.md`) | Clear   | Voiceprint · Booth · Impostor                                                                                                |


## 3. Non-goals

- No lock or key derivation, no fuzzy reconcile / helper data (that is F4).
- No face, camera, liveness, or challenge (F5+).
- No change to the vault file or F2 enroll/unlock behavior.
- No tolerance-tuning UI and no enrollment-quality gate (F9) — F3 uses a fixed
provisional threshold only.
- No multi-profile; a single reference voiceprint is enough for F3.
- Out-of-scope discoveries during build: record in `.out-of-scope/`, never build.

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv; engine code in
`src/voicelock/`, UI in `src/voicelock/ui/`, tests in `tests/`; Python owns the
voiceprint compute, JS renders the meter only; **offline-only — no network at runtime**.
- Entry point remains `uv run voicelock` (Booth window).
- Voiceprint method: **SpeechBrain ECAPA-TDNN** (`spkrec-ecapa-voxceleb`),
human-approved TECH-PICK. Research: `memory/research/2026-07-22-f3-voiceprint-embedding.md`.
New deps added via `uv` at build time: `speechbrain`, `torch`, `torchaudio`.
- **Offline enforcement (from the TECH-PICK):** the ECAPA weights are **vendored
in the repo** at `src/voicelock/models/ecapa/` (model is Apache-2.0 — its
LICENSE/NOTICE retained alongside the files; redistribution permitted). The app
and the Gate load ECAPA from that local path with `HF_HUB_OFFLINE=1` (SpeechBrain
pointed at the local dir), so there is **no runtime network**. The Gate is
self-contained: `uv run pytest` loads the vendored model offline, no setup step.
One-time developer action during build: download the official files once and
commit them (~20 MB in git; plain git, no LFS for this local project).
- Reference voiceprint: a Booth **"Set reference"** action records **3 separate
short sentences**, computes an ECAPA embedding for each, and **averages** them
(mean of the L2-normalized embeddings, then re-normalized) into one reference
vector. It persists **just that averaged vector** to `~/.voicelock/voiceprint.ref`
— a small sibling file, **not** inside the vault. Persists across runs;
re-settable by setting again. A take that is too short/silent is rejected with
"need more audio" and re-recorded (that take only), not averaged in. Keeps F3
decoupled from the lock; F4 later supersedes this with vault-stored voice helper
data. This multi-sample averaging deliberately overlaps F9's territory (human
chose robustness); the **full** enrollment-quality gate + tolerance UI remain
F9. Honest limitation: the reference vector is stored in **plaintext** —
acceptable for an F3 diagnostic (real sealing is F4).
- **Reset reference (amendment 2026-07-23):** a Booth **"Reset"** control clears
the stored reference — deletes `~/.voicelock/voiceprint.ref` (a no-op if none
exists) **and** discards any half-finished take run — then empties the 3-take
progress and returns the meter to the "set reference first" state. **No
confirmation prompt** (low-stakes diagnostic, freely re-settable). Re-setting a
reference afterward is the normal 3-take flow. Python owns the clear (a bridge
method deletes the file + resets in-progress takes); **JS renders only** the
reset state — no embedding math in JS. Keep Record/Stop/Play and F2
Enroll/Unlock unchanged.
- Match distance + coloring: **cosine distance** between the live ECAPA embedding
and the reference, shown with **three-band coloring** — accept (green) /
borderline (amber) / reject (red). The concrete accept and reject cutoffs are
chosen **empirically during build** from the test fixtures and pinned in §5 once
measured; the borderline band sits between them. The Gate asserts same-speaker
distance lands in the accept band and different-speaker distance lands in the
reject band on fixed fixtures. Tolerance-tuning UI is F9, not F3.
- Booth UX: reuse the existing mock chrome; add a live distance readout + accept/
reject color; keep Record/Stop/Play and F2 Enroll/Unlock unchanged.
- Edge cases (visible, no crash): no reference set yet → prompt to set one;
speech too short / silent → visible "need more audio" state; no mic → existing
F1 mic-error path.
- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
`uv run pytest` → exit 0.
- No new dependency beyond the approved ECAPA stack without a fresh TECH-PICK.

## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Harness rules find this
section by its NAME ("Verification"). Two parts, both required.

Runtime budget: `uv run pytest` loads torch + the vendored ECAPA model, which can
take up to ~2 minutes on first run. Whole suite budget: **within the 10-minute
default** (declare a longer budget here only if that proves false during build).

Standing (project regression net, from `project.md`), pinned:

- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed)

Feature-specific (proves THIS feature works), pinned:

- `uv run pytest tests/test_voiceprint.py -q` → exit 0; final summary reports 0
failed. Must cover, using fixed audio fixtures + the **vendored** ECAPA model
loaded fully offline (`HF_HUB_OFFLINE`, no network):
(1) same-speaker fixtures → cosine distance ≤ the module's accept cutoff (lands
in the accept band); (2) different-speaker fixtures → cosine distance ≥ the
module's reject cutoff (lands in the reject band) — the test imports the same
cutoff constants the app uses, so the assertion is deterministic, not judgment;
(3) "Set reference" averages 3 per-utterance embeddings into a single
L2-normalized reference vector, and a too-short/silent take is rejected with the
"need more audio" signal (not averaged in); (4) with no reference file present,
the compare path surfaces a set-reference-first signal (no crash); (5) the model
loads from the vendored local path with no network call.

- `uv run pytest tests/test_booth_api.py -q` → exit 0; final summary reports 0
failed. Must cover (amendment 2026-07-23), using a temp ref path (no real mic):
after a reference is set, the bridge **`reset_reference`** clears it — a
subsequent `compare` surfaces the set-reference-first (`no_reference`) signal
again, and the reference file no longer exists.

Proof surface: the highest real surface F3 touches is the live pywebview Booth.
Automated tests prove the Python voiceprint path on fixtures; they do **not** drive
the real window or a live mic — that gap is covered by the required manual line
below (a required check, not accepted risk).

- Manual (required for F3 done — Verification check): run `uv run voicelock`, use
**Set reference** and speak 3 sentences to store a reference → the same person
reads a sentence → live meter shows a small distance / **accept (green)** → a
**different** person reads → meter shows a large distance / **reject (red)** →
click **Reset** → the meter returns to "set reference first" and a fresh
reference can be set again.
Observable: real-mic Set reference works, the live 3-band meter updates, a
real same-vs-different speaker separates into accept vs reject, and Reset clears
the reference back to the no-reference state.

Out-of-scope discoveries during build (Mode 3 default): record in `.out-of-scope/`,
never build.

---

*Spec-anchored: amendments follow the path in the closing note of the F2 spec —
update this file, re-scan changed sections, human re-checks box 2, re-plan.*
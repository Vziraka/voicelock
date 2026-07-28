# Handoff

## F8 — Lip-sync liveness (challenge-response) · SPEC DRAFTED, at approval gate

**2026-07-28.** `spec.md` fully drafted and grilled interactively with the
human. Grilling record: `Status: CLEAR`, zero `NEEDS-CLARIFICATION` hits.
Box 1 (Grilling CLEAR) is checked. **Box 2 (human approval) is open —
this is what remains before `/plan` can start.**

### What got resolved this session

- **Q1 (TECH-PICK, new dependency):** `vosk` for offline, grammar-constrained
  challenge-phrase matching — human-approved, explicitly waiving the
  disclosed stale-PyPI-wheel signal (repo itself is active; the published
  wheel isn't). Research: `memory/research/2026-07-28-f8-offline-stt-challenge-match.md`.
  Decision: `memory/decisions.md` (2026-07-28, F8 TECH-PICK entry).
- **Q2:** AV capture = existing Record/Stop transport, fixed ceiling
  (~6–8 s provisional, to be confirmed at `/plan` against the actual phrase
  pool).
- **Q3:** Challenge phrase pool = small hand-authored constant (~10–20
  phrases), random pick, no-immediate-repeat.
- **Q4:** Lip-sync = lag-windowed normalized cross-correlation, mouth
  aperture (F5's lip contour) vs audio envelope (F1's), pure numpy.
- **Q5:** Gate fixture strategy = synthetic unit tests for both scoring
  functions, plus a real (unmocked) Vosk reject-path exercise against an
  existing voice fixture — no new AV fixtures sourced or committed. The
  accept-path proof for both signals lives only in the required manual
  check (§5 cmd 4) — disclosed explicitly in §5 and §6, not smoothed over.
- **Q6:** Liveness gates **before** any of the three crypto lock layers are
  attempted — a liveness failure never calls `vault.unlock()`.
- **Mode: Mode 3** (same as F4–F7). Recorded: `memory/decisions.md`.
- **Blind-spot question (§6):** accepted as drafted — the Gate can't prove
  either new signal's ACCEPT path or real replay-resistance; only the
  required live manual check does. Same shape as F4/F7's own disclosed
  generalization gaps.

### next_action

**Human**: open `spec.md`, read §1 (Outcome) and §5 (Verification), confirm
the Mode line still reads right, and check box 2. Then, in a fresh session,
run `/plan` to break this into tasks — Vosk vendoring (mirrors F5/F6's
model-vendoring pattern) is a natural first task since `challenge.py` and
the Booth bridge both depend on it landing first, the same shape F7's
`facelock.py` had relative to its own Task 2.

### Session commits

Base → head: see the commit this session makes at its close (state-file
commit checkpoint, proposed to the human before running).

### Open items for whoever picks up `/plan`

- The exact AV-capture ceiling duration (~6–8 s provisional) should be
  confirmed against the actual authored phrase pool's real speaking time
  before being pinned as a constant — per `project.md`'s
  dry-run-before-pinning guardrail.
- `SYNC_THRESHOLD` and the lag-window width (Q4) are Gate-test constants
  derived from synthetic separation, not real human data — the module
  docstring must say so, mirroring `facelock.py`'s Q2 disclosure pattern.
- The exact Booth copy for the fifth reject chip (`chip-liveness-failed`,
  proposed text in `spec.md` §1) may be refined at `/plan`, same as F7's
  chip wording was.

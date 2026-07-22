# Decision log (append-only)

The cheap paper trail. ADRs (`formats/ADR.md`) are for the rare hard-to-reverse
calls; EVERY approved decision lands here, so the next session inherits the
*why*, not just the code. A decision that exists only in chat does not exist.

Newest first. Never edit or delete old entries — supersede them with a new one.
One exception: `curate` may MOVE a superseded entry, whole and unchanged, into
the `## Archive` section at the bottom — human-approved, position changes,
content never does (see `skills/curate/SKILL.md` step 3).

Format:
- {YYYY-MM-DD} · **{decision in one line}**
  - why: {one line}
  - rejected: {alternatives and the one-line reason, or "none — human directed"}
  - link: {spec section · ADR · TECH-PICK table · commit}

<!-- entries go below this line -->

- 2026-07-22 · **F2 Mode 3 + live Booth enroll/unlock/REJECT as required Verification**
  - why: Mode 3 autonomy; Gate must not pass if only temp-path tests work and the Booth never seals ~/.voicelock/vault.vl
  - rejected: treating live Booth as accepted risk / waived check
  - link: `spec.md` Approval · Verification · Constraints

- 2026-07-22 · **F2 no-vault unlock copy: "No vault yet — enroll first"**
  - why: actionable status when Unlock is hit before enroll
  - rejected: "Vault missing"; custom wording
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 vault file layout: VLCK magic + version + salt + ciphertext**
  - why: one self-describing file; version leaves room for F4 format bumps
  - rejected: salt+ciphertext only; JSON sidecar + separate blob
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 Argon2id cost: OPSLIMIT_MODERATE / MEMLIMIT_MODERATE**
  - why: demo-snappy stretch of the passphrase without pretending product-grade hardness
  - rejected: INTERACTIVE (weaker story); SENSITIVE (sluggish demo)
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 Booth UX: wire mock Enroll + passphrase Unlock; keep F1 record/play**
  - why: mock already sketches the flow; end-to-end demo without a throwaway panel
  - rejected: separate minimal panel; engine-only / script unlock
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 enroll: name + passphrase only; sealed payload = display name (no audio)**
  - why: outer lock is passphrase; recording already proven in F1; voice auth is F3/F4
  - rejected: required recording placeholder; optional take-if-present
  - link: `spec.md` Constraints · Non-goals

- 2026-07-22 · **F2 vault path: single profile at ~/.voicelock/vault.vl; re-enroll overwrites after confirm**
  - why: fixed, inspectable demo location outside the repo; one vault keeps F2 thin
  - rejected: project-local cwd vault; multi-profile in F2
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 outer lock crypto: PyNaCl (Argon2id + SecretBox)**
  - why: one dep covers passphrase KDF + AEAD seal for the learning vault demo
  - rejected: cryptography (broader, more wiring); stdlib-only (no suitable AEAD)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f2-outer-lock-crypto.md`

- 2026-07-22 · **F1 visualizer: bars**
  - why: clearest “levels reacting” demo signal; mock default
  - rejected: orb / rings (prettier, less obvious as loudness)
  - link: `spec.md` Constraints

- 2026-07-22 · **F1 capture format: 16 kHz mono**
  - why: speech band is enough for demo + later voiceprint; smallest sensible buffers
  - rejected: 48 kHz mono (heavier, little identity gain); stereo hi-rate (waste for who-are-you)
  - link: `spec.md` Constraints

- 2026-07-22 · **F1 UI: use voicelock-mock.html chrome; only record/viz/play live**
  - why: mock already sketches the full product; polish later; avoids a throwaway minimal booth
  - rejected: booth-only strip-down (loses project context); full mock interactive in F1 (scope creep)
  - link: `spec.md` Constraints · Non-goals

- 2026-07-22 · **F1 Mode 3 + live Booth manual check in Verification**
  - why: Mode 3 autonomy; blind spot is pywebview/live mic not covered by fake-stream tests
  - rejected: waiving the live-window check (would let Gate pass a dead Booth)
  - link: `spec.md` Approval · Verification

- 2026-07-22 · **F1 audio: sounddevice + numpy**
  - why: live PortAudio bindings with array I/O and injectable streams for Gate tests
  - rejected: PyAudio (fails ~12-month liveness bar); DIY WASAPI/ctypes (F1 time sink)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f1-audio-capture.md`

- 2026-07-22 · **F1 UI shell: pywebview**
  - why: light native webview + JS↔Python bridge fits Booth without Chromium weight
  - rejected: PySide6+WebEngine (heavy Qt/Chromium); Eel (Alpha, Chrome-shaped)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f1-ui-shell.md`

- 2026-07-22 · **Stack: Python 3.11 + uv; JS UI for looks; UI shell TECH-PICK at F1**
  - why: offline audio/crypto/voiceprint brain in Python; mock-based booth stays HTML/CSS/JS
  - rejected: Electron/TS-first (ML path harder); bare pip (no lockfile discipline)
  - link: `constitution/topics/conventions.md` · `constitution/project.md`

- 2026-07-22 · **Layout: src/voicelock (+ ui/), tests/, design/ mock reference**
  - why: clear brain/looks split; mock is starting chrome not final
  - rejected: none — human accepted recommendation
  - link: `constitution/topics/conventions.md`

- 2026-07-22 · **Gate: uv run ruff check . · uv run pytest**
  - why: simple, standard Python checks; promises until F1 wires them
  - rejected: none — human accepted recommendation
  - link: `constitution/project.md`

- 2026-07-22 · **Approach B — two stacked locks for the profile vault**
  - why: always-both factors with crisp, independent impostor rejects for a learning demo
  - rejected: A voice-as-gate-only (voice wouldn't seal bytes); C single combined key (failures blur)
  - link: `roadmap.md` Approach · `adr/0001-two-stacked-locks.md`

- 2026-07-22 · **Anti-spoof bar: speaker match + challenge-response; no deepfake-proof claim**
  - why: full three-impostor demo without lying about live voice cloning
  - rejected: strong anti-deepfake as a must-have (research-heavy, oversell risk); robotic heuristic parked as optional F7
  - link: `roadmap.md` Intent · Out of scope

- 2026-07-22 · **Must-build F1–F6; park F7 (weak robotic heuristic)**
  - why: full demo arc at F5; F6 makes it presentable; F7 is optional exploration only
  - rejected: bundling F7 into the must-build path
  - link: `roadmap.md` Features

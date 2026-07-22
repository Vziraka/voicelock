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

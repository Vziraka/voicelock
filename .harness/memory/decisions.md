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

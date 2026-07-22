# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 5 Gate `ESCALATE_HUMAN` → `BLOCKED`.
  Soft-cap take-ready fix is in build `586943c`. Automated Verification commands
  exit 0; required Manual demo cannot be attested by the subagent verifier.
- **Commits:** base 11e4bf34f41e212dc67bbe4772180184cb258f6d → head
  586943c4f3a3b2dc5f103f8e3508df440daecc68 (retry build)
- **Failed + lesson:** Mode 3 still needs a human for the live Booth line —
  that is the accepted blind spot, not a waiver.
- **Next action:** Human — run `uv run voicelock`, then Record → speak until
  the visualizer moves → Stop → Play; confirm the take is audible. Then say
  the demo passed (or failed) so Task 5 can leave `BLOCKED` and finish
  verify/wrap-up. (New here? `GUIDE.md` walks the loop.)
- **Pending guardrail:** none
- **Where the rest lives:** `spec.md` Verification · `plan.md` Task 5 ·
  `src/voicelock/app.py` · `src/voicelock/ui/index.html` ·
  `memory/verdicts/2026-07-22-F1-T{1..4}.json`
- **Wrap-up:** not run — blocked on human manual demo

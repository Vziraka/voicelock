# Handoff

Generated at session end so a fresh session (any model) continues cleanly.
Rule: **reference, don't restate** — point to spec/plan/ADRs/commits; don't copy them.

- **Changed since last session:** Task 5 retry — `_pump_loop` calls
  `onCaptureEnded(samples)`; JS sets `hasTake` so Play works after soft-cap.
- **Commits:** base 11e4bf34f41e212dc67bbe4772180184cb258f6d → head
  586943c4f3a3b2dc5f103f8e3508df440daecc68
- **Failed + lesson:** prior REJECT: auto-stop must surface take-ready (see plan feedback)
- **Next action:** Mode 3 — clean-context verifier for Task 5 retry
- **Pending guardrail:** none
- **Where the rest lives:** `plan.md` Task 5 feedback · `src/voicelock/app.py` ·
  `src/voicelock/ui/index.html`
- **Local smoke (implementor, disclosed):** ruff · pytest · capture/playback -q — exit 0
- **Wrap-up:** not run — awaiting verifier

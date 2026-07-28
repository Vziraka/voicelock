# Handoff

## F8 Task 4 — Booth UI: challenge display + AV capture UX + fifth reject chip · REVIEW, awaiting verification

**2026-07-28.** Built and committed. Task 4 (LAST task) moved `TODO → DOING → REVIEW`.

### Changed

- `src/voicelock/ui/index.html` — challenge-phrase display (`.challenge-display`,
  shown before Record and kept visible through the capture), `refreshChallenge()`
  (calls `new_challenge()` at Booth init and after every completed unlock
  attempt), Record/Stop routed to `start_unlock_capture()`/
  `stop_unlock_capture()` during an unlock attempt vs. the plain
  `start_record()`/`stop_record()` pair enroll keeps unmodified,
  `chip-liveness-failed` + `showLivenessFailed()` for the `auth_liveness`
  reject (status `"REJECT · LIVENESS CHECK FAILED"`, sub-text naming that
  passphrase/voice/face already passed).

### A plan-note correction made during build (not a BLOCKED stop)

Task 4's own `plan.md` notes said the new bridge pair's routing should be
"gated on which panel is active (mirrors the existing per-panel branching
already in `btnRecord`'s handler)" — on inspection, no such branching exists
(`btnRecord` unconditionally called `start_record()`), and there is no
separate "Unlock panel" toggle in this Booth's DOM at all (Enroll has its
own slide-out `aside` panel; the passphrase/Record/Unlock controls in
`main` are one persistent view). Read against universal.md's "rule you
cannot follow literally" clause: the core instruction (gate the routing on
context) was still followable, only the parenthetical's claimed precedent
didn't hold — so implemented a sound design instead of stopping the
feature's last task. Full reasoning and the design (passphrase-focus +
"enroll panel not open", decided once per Record press): `plan.md` Task 4's
build notes.

### Manual smoke test performed (Booth-layout guardrail)

Headless-Chromium screenshots of `index.html` at the app's real 1100×740
window size, three states: default (challenge box + unlock row visible, no
clipping), scrolled to the bottom (voiceprint/faceprint/inert panels all
reachable — the F6-era `margin: auto` fix still holds), and a simulated
liveness-reject (status/prompt/sub-text/chip all render correctly). No
clipping in any state.

### Verification run this session (build-time only, not the Gate)

- `node --check` on the extracted inline `<script>` → syntax OK
- `uv run ruff check .` → clean
- `uv run pytest` → 222 passed (unchanged — UI-only, no new Python tests)

None of the above substitutes for the fresh-context Gate.

### The required manual check is SEPARATE and still pending

Spec §5 cmd 4 — the live 5-outcome demo (enroll, then unlock with all four
correct; wrong passphrase; wrong voice; wrong face; liveness fails at least
two ways) — needs a real microphone and camera and can only be attested by
the human. It is not something this session (or any automated verifier) can
run. Per Mode 3's contract, this is exactly what "the human is checked in
with at the feature-end checkpoint" means. **Task 4 (and F8 as a whole)
cannot be marked DONE until this is attested**, per spec §5 cmd 4's own
"PENDING — this is what remains after Task 4" line and `plan.md`'s
done-criteria.

### next_action

**Verifier**: spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, used verbatim; task id `Task 4 (LAST task)`,
base `1854e87`, head `eff074e`) for the automatable parts of spec §5's full
Verification list (cmds 1–3, `ruff`, `pytest`, spec/standards compliance).
**If the verifier's Gate/Review comes back clean, the session does NOT
self-declare F8 done** — it presents the automated results to the human
and asks them to run spec §5 cmd 4 (the live demo) before wrap-up finalizes
Task 4 and the feature completion report. This is the feature-end
checkpoint Mode 3 reserves for the human, not a self-verification.

### Session commits

Base (DOING) → head (build): `1854e87` → `eff074e`. Files this session:
`src/voicelock/ui/index.html`, `.harness/plan.md` (DOING → REVIEW + build
notes), `.harness/handoff.md` (this file, committed separately as
bookkeeping).

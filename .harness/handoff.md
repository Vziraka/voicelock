# Handoff

## F8 Task 3 — Booth bridge: liveness gate before `vault.unlock` · DONE

**2026-07-28.** Verified and wrapped up. `rejects: 0` — the first F8 task to
pass on the first review (see `memory/verdicts/2026-07-28-F8-T3.json`).

### Changed (final state)

- `src/voicelock/app.py` — `LIVENESS_CAPTURE_CEILING_SECONDS = 10.0`,
  `_audio_envelope()`, new `BoothApi` state (`_retain_landmarks`,
  `_liveness_mouth_series`, `_current_challenge`), `new_challenge()`,
  `start_unlock_capture()`/`stop_unlock_capture()`, `unlock()` reshaped to
  gate on `_liveness_passes()` before `vault_unlock`, `_push_face_frame()`
  retention, and a fix inside `_pump_loop()`'s auto-stop branch.
- `tests/test_booth_api.py` — 8 existing unlock tests updated to bypass the
  liveness gate via `_force_liveness_pass()`; 17 new tests.

### A real bug found and fixed during build

The fixed-ceiling auto-stop path lives in `_pump_loop()` (it notices a take
self-ended, bypassing `stop_unlock_capture()` entirely), so the first cut
left `_retain_landmarks`/`capture.max_seconds` permanently set after an
auto-stopped liveness take — silently capping the next enroll take too.
Caught by the task's own exit-path Gate test, fixed by repeating the reset
inside `_pump_loop()`. Third confirmed occurrence of `project.md`'s
acquisition/release guardrail's predicted failure shape (after F4.5 and F5
Task 7) — full reasoning in the verdict file, no new guardrail needed.

### ADR written

`adr/0005-liveness-gates-in-front-of-the-vault.md` — the Q6 gate-ordering
decision (liveness wraps `vault.unlock()` from outside `app.py`, zero
`vault.py` touch) passes the 3-condition gate; mirrors ADR 0002/0004's
precedent of recording at the implementing task, not only the spec session.

### next_action

**Task 4 (LAST task) — Booth UI**: challenge display + AV capture UX +
fifth reject chip. Needs Task 3's bridge methods
(`start_unlock_capture()`/`stop_unlock_capture()`, `new_challenge()`,
`auth_liveness`). Mode 3's standing approval covers task-to-task
progression — this wrap-up completing is the precondition. Task 4's
done-criteria is the FULL spec Verification list, including the **required
manual 5-outcome check** — not automatable, attested by the human at the
feature-end checkpoint. Per the earned Booth-layout guardrail: the
challenge-phrase display is new visible content in the `main`/`.booth`
column — smoke-test it manually before calling Task 4 done.

### Where the rest lives

Full task history and the bug/mutation-check trail: `plan.md` Task 3
(notes + build notes), `memory/verdicts/2026-07-28-F8-T3.json`,
`adr/0005-liveness-gates-in-front-of-the-vault.md`.

### Session commits

Task 3 full history: `08676fa` (DOING) → `e571695` (build) → `6856cc5`
(handoff) → next commit is this wrap-up's state-file checkpoint (plan.md
DONE + verdict + ADR + this handoff).

### Pending guardrail

None.

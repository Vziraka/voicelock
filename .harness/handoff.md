# Handoff

## F8 — Lip-sync liveness (challenge-response) · COMPLETION REPORT (updated)

**2026-07-29.** All 4 tasks `DONE` (`rejects: 1/1/0/0`). The human's first
live run of spec §5 cmd 4 (2026-07-28) found liveness failing almost every
attempt despite correct passphrase/voice/face — a real defect, exactly what
the required manual check exists to catch (Q5/§6's disclosed gap: the
automated Gate cannot prove either liveness signal's ACCEPT path). Diagnosed
with temporary debug prints (removed once confirmed fixed, not left in) and
fixed same session — three independent root causes, all in
`plan.md`'s Task 4 build notes in full. **Still nothing from this feature is
committed** — this report is the feature-end checkpoint Mode 3 reserves for
you.

### What was actually wrong, and the fix

1. **Frame/audio misalignment (the dominant cause).** Real camera frames
   don't arrive on the fixed 30fps grid the audio envelope assumed —
   `lipsync.score()`'s index-for-index comparison silently desynced over a
   take's length. Fixed by timestamping each retained mouth-aperture
   sample and resampling onto the envelope's real time grid
   (`_resample_mouth_series`, `app.py`). Measured, not assumed: the exact
   dropped-frame shape from your log scores 0.34–0.46 (fail) under the old
   alignment, 0.93+ (pass) after the fix — both numbers are pinned into a
   test.
2. **`matches()` required an exact full-string match.** Real Vosk decoding
   glued on stray words / repeated the phrase in your log
   (`"my wild horses run across the plain"`). Relaxed to substring
   containment — safe because `check()`'s grammar is constrained to only
   the challenge + decoy pool + `[unk]`, so the phrase can only appear if
   actually said.
3. **The Record/Stop routing heuristic was unreliable.** Your very first
   take fell back to the plain 30s pair before liveness retention ever
   armed — the exact risk flagged (uncertain) in `memory/deviations.md` at
   Task 4. Replaced with a deterministic rule (enroll panel open/closed)
   rather than a focus heuristic — your approval on this is recorded
   2026-07-29.

Also added, at your request and outside spec's original scope (parked, not
formally speced): a **Lock** button that resets the display without
touching the vault. Also parked to `roadmap.md`'s F9 entry (not built):
detecting a covered/occluded mouth during capture and stopping early —
infeasible today, MediaPipe's landmarks can't distinguish "occluded" from
"just not moving."

### Outcome vs. spec §1 (updated)

| Demo outcome (spec §1) | Status |
|---|---|
| Right passphrase + voice + face + live challenge → **unlocked** | You confirmed this now works live ("much better") |
| Wrong passphrase → outer REJECT | Automated-tested, unchanged since F2 — **not re-confirmed live since the fix** |
| Right passphrase, wrong voice → middle REJECT | Automated-tested, unchanged since F4 — **not re-confirmed live since the fix** |
| Right passphrase, right voice, wrong face → inner REJECT | Automated-tested, unchanged since F7 — **not re-confirmed live since the fix** |
| Right passphrase/voice/face, **liveness fails** → liveness REJECT | You confirmed one method live (covering your mouth); spec wants **a second method** too |

None of today's fixes touched the outer/middle/inner lock paths or their
tests, so those three are low-risk, but per this repo's own standard
("required means required," not "probably fine") they should still get a
quick live re-confirmation before this closes out.

### Full Gate evidence (command → exit code, after the fix)

- `uv run ruff check .` → 0 (clean)
- `uv run pytest` → 0 (**229 passed**, up from the original Task 4
  completion's 222 — +7 tests covering all three fixes)
- `node --check` on the extracted Booth `<script>` → 0 (syntax OK)
- Manual layout smoke test: headless-Chromium screenshot confirms the new
  Lock button fits cleanly next to Unlock, no clipping.
- **Spec §5 cmd 4 (live 5-outcome demo): partially run by the human,
  in-progress — see the table above for what's confirmed vs. not.**

### Retry counts per task (unchanged from the original completion)

Task 1: `rejects: 1` (unused exception class). Task 2: `rejects: 1`
(untested lag-search loop). Task 3: `rejects: 0`. Task 4: `rejects: 0`. The
live-demo bugfixes above happened AFTER Task 4's wrap-up, at the
feature-end checkpoint — they're not counted against any task's retry
budget (that budget governs the build↔verify cycle, not post-wrap-up fixes
found by the human's own required check).

### `memory/deviations.md` entries made during this feature

One, at Task 4 (2026-07-28): the plan-note claiming an "existing per-panel
branching" precedent that didn't actually exist. Logged for your review
rather than silently resolved. **Update, 2026-07-29:** the live demo then
found the resulting design (passphrase-focus heuristic) genuinely
unreliable in practice — your first take silently used the wrong capture
pair. Replaced it with the deterministic rule described above, which you
approved in chat. The original deviations.md entry is left as-is (it's an
append-only historical log of the judgment made at the time); this note is
the forward pointer to what actually happened next.

### Anything escalation-worthy that resolved itself

Task 3's `_pump_loop()` auto-stop bug (found by the task's own Gate test) —
third confirmed occurrence of the acquisition/release guardrail's own
predicted failure shape. No new guardrail needed.

### What's left

1. Re-run the live demo, confirming: wrong passphrase / wrong voice / wrong
   face still reject correctly (should be unaffected, but not yet
   re-checked since the fix), and a **second** liveness-fail method (photo,
   muted video, or an audio-only replay — you've already covered "covering
   your mouth" as one).
2. Tell me the results.
3. Your commit/push approval — proposed message below, unchanged in shape
   from before, now covering the fix session too.

### Session commits (this feature, newest first — all local, nothing pushed)

`11d00bd` (Task 4 handoff bookkeeping) ← `eff074e` (Task 4 build) ←
`1854e87` (Task 4 DOING) ← `1311123` (Task 3 wrap-up) ← `6856cc5` (Task 3
handoff) ← `e571695` (Task 3 build) ← `08676fa` (Task 3 DOING) ← `04c9cf4`
(Task 2 wrap-up) ← `9230111` (Task 2 handoff, retry 1) ← `1e42625` (Task 2
build, retry 1) ← `0f21cdd` (Task 2 DOING retry 1) ← `16d6769` (Task 2
REJECT 1) ← `c81a34e` (Task 2 handoff) ← `6959dee` (Task 2 build) ←
`bc91244` (Task 2 DOING) ← next commit covers BOTH the original Task 4
wrap-up checkpoint AND the 2026-07-29 live-demo bugfix session in one
commit (nothing from either was committed separately). Base of the whole
feature: `fc03108` (prior HEAD, F8 plan session).

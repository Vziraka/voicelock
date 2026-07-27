# F7 — Task 3 (LAST task) · BUILT, IN REVIEW

**Base:** `6ea3d9c` (Task 3 set `DOING`, before any code touched).
**Build commit:** `30f4add` — `src/voicelock/ui/index.html` + `plan.md`
(Task 3 → `REVIEW`).

## What this session did
Built Task 3 exactly as `plan.md` scoped it: a new `#enroll-face-step` block
in the enroll panel (3-dot take progress, hint line, "Bank this frame"
button wired to `enroll_face_take`), mirroring `#enroll-voice-step`
verbatim in structure. A third result chip (`chip-wrong-face` /
`showWrongFace()`) mirrors `showWrongVoice()` exactly. Added
`showUnlockNoFace()` for unlock's `no_face` edge — not explicitly named in
`plan.md`'s notes, but required by spec §4's edge-case list ("no face
detected during enroll/unlock capture → F6's `NoFaceError` surfaced as
Booth copy, not a crash"). `refreshEnrollButton()` now gates the Enroll
button on BOTH steps being done (previously voice-only) — a necessary
consequence of adding the parallel face step, not spelled out verbatim in
the plan but implied by it. `btnEnrollOpen`/`btnEnrollCancel` now await
both `resetEnrollVoiceStep()` and `resetEnrollFaceStep()`, same ordering
rule as the existing voice reset.

## Gate commands run this session
- `node --check` on the extracted inline `<script>` block → syntax OK
  (mirrors F6's precedent for inline-script changes; not itself a spec
  Verification command, an extra local check)
- `uv run ruff check .` → exit 0
- `uv run pytest` → exit 0, **186 passed** (Task 3 is UI-only — HTML/CSS/JS,
  no Python changed, so the count is unchanged from Task 2's end)

Since this is the feature's LAST task, its done-criteria are the FULL list
from spec.md's Verification section. Automatable items (ruff, full pytest,
§5 cmds 1–3 — all part of the same pytest run) all pass. **§5 cmd 4 — the
live 3-way manual check — is REQUIRED and still PENDING.** Only the human
can attest it, and per Mode 3 that happens at the feature-end checkpoint,
not mid-build.

## What the verifier should know
- **Scope:** only `src/voicelock/ui/index.html` changed (plus `plan.md`
  bookkeeping). No Python file touched — `vault.py`, `app.py`, `facelock.py`
  etc. are all exactly as Task 2 left them.
- **§5 cmd 4 cannot be run by an automated Gate** — it is a live webcam+mic
  walkthrough. Score the Gate on the automatable items; cmd 4's PENDING
  status is expected at this point in the pipeline, not a defect. It gates
  the feature-end checkpoint, not this task's REVIEW.
- **CSS/layout risk, disclosed honestly (per `project.md`'s Booth-layout
  guardrail):** the new take-progress block sits inside `.enroll-panel` →
  `.profiles`, which uses `overflow-y: auto` with default top-anchored flex
  alignment (no `justify-content: center`) — the specific CSS property that
  caused F6 Task 5's clipping bug is absent here, so by reasoning this
  should NOT reproduce that failure mode. This is reasoning from the CSS
  source, not a substitute for the guardrail's mandatory manual smoke-test
  — this repo has no headless-browser tooling (deliberately, per that
  guardrail's own text) and the agent cannot render pixels to verify. Since
  opening the enroll panel is a required step of cmd 4's own live
  walkthrough, the human's cmd 4 attestation covers this smoke-test too.
- `enroll_face_take`'s `no_face` progress-preserving behavior, the
  `need_face_takes` guard, and the `auth_face` reject were all already
  covered by Task 2's bridge tests (`test_booth_api.py`) — this task only
  wires the UI to bridge methods that already exist and are tested.

## next_action
Mode 3 is the standing "go". Spawn the clean-context verifier now
(`formats/VERIFIER-PROMPT.md`, verbatim, task id `Task 3`, base `6ea3d9c`,
head `30f4add`) — this session proceeds immediately. On APPROVE, `wrap-up`
runs — since this is the feature's last task, that means the **feature-end
checkpoint**: the human attests §5 cmd 4 live, reviews the final verdict,
and approves commit/push. On REJECT, Task 3 returns to `TODO` with feedback
appended to `plan.md`, `rejects:` increments (cap 3).

## Pending guardrail
None — the guardrail earned this feature (signature-change/caller-coupling
planning rule) was already written to `project.md` during Task 2's wrap-up.

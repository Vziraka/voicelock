# F6 — Faceprint on screen · Task 3 WRAP-UP

**Session date: 2026-07-27.** Task 3 built, hit a real spec-vs-reality
blocker, was unblocked by a human-approved spec amendment, REJECTed once on
an unexercised branch, fixed, verified APPROVE, and wrapped up — all in
this session.

## What happened this session

- Spawned the clean-context verifier a second time (retry 1). Verdict:
  **GATE PASS, REVIEW APPROVE**, no feedback. The verifier independently
  reproduced the mutation check on the fix and independently re-verified
  the earlier spec amendment was genuinely human-approved (not just
  asserted). Full reasoning: `memory/verdicts/2026-07-27-F6-T3.json`.
- Wrap-up checklist run in full:
  - **ADR:** none — fails condition 1 (hard to reverse). Neither the test
    fix nor the spec's resize-parameter amendment is an architecture
    decision.
  - **`learn` scan:** ran. One NEW lesson cleared the bar — see **Pending
    guardrail #2** below. (The REJECT itself was the EXISTING
    no-unexercised-branch guardrail correctly firing — not a new lesson,
    confirmation the guardrail works.)
  - No idea was declined by a human this task (the human approved the
    spec-amendment recommendation as given) — no `.out-of-scope/` entry
    owed.
  - **Roadmap:** unchanged — 2 tasks remain in Feature 6 (Tasks 4–5).
  - **`plan.md`:** Active context, memory spine, and Task 3's line
    refreshed; Task 3 → `DONE`.

## Pending guardrails (TWO, both still awaiting separate human decisions)

**#1 — carried from Task 2, unchanged, still open:**

> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. It carries face-tracker state (an ROI prior) across
> `detect_for_video` calls, so feeding it unrelated stills back-to-back
> silently drops the face (0 detections, no error) on any frame after the
> first whose face falls outside the prior frame's tracked region. Use a
> fresh instance per unrelated image, or `IMAGE` mode outright, for any
> script/test that compares or checks multiple independent photographs.
> `warn` · expires: 2027-01-31
> - _Evidence:_ F6 Task 2 (2026-07-27), commit `4c8f880`,
>   `tests/fixtures/face/README.md`'s "Detection re-verified" section.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

**#2 — NEW, from this task's `learn` scan:**

> **[Done]** A Verification command that exercises a real vendored model
> (image/audio/ML inference) on constructed test data — a resize, a
> synthetic signal, a specific parameter combination — must be dry-run
> against that real model BEFORE being pinned into `spec.md`. A
> plausible-looking parameter set can silently produce input no honest
> implementation can process, and that is indistinguishable from a real
> code defect until someone actually runs it. `warn` · expires: 2027-01-31
> - _Evidence:_ F6 Task 3 (2026-07-27). `spec.md`'s §5 cmd 4 pinned
>   `cv2.resize(img, (1280, 720))` against `personA_1.jpg` (816×1024,
>   portrait) at spec-drafting time, before `faceprint.py` existed to test
>   it against. The resize was a non-uniform stretch that no honest
>   implementation could pass: confirmed by elimination, not assumed — the
>   identical distorted array run through F5's own already-shipped,
>   unmodified `facedetect.load_landmarker()` also found 0 faces; a
>   `min_face_detection_confidence` sweep (0.5→0.01) made no difference;
>   an aspect-preserving resize at a comparable scale (574×720) detected
>   the same face fine on the same model. Cost a full `BLOCKED` stop, a
>   multi-step elimination investigation, and a human escalation before a
>   fix could even be attempted — real rework, not a one-off. **Sibling to
>   the existing guardrail on source-text verification criteria** ("must
>   match the behaviour's meaning, not one exact spelling") — same root
>   cause (a criterion authored before the code existed to validate it
>   against), different failure side: that rule catches brittle TEXT
>   matching; this one catches impossible DATA parameters. Whether this
>   should also change the `spec`/`plan` skills' own process (dry-run
>   before pinning) is a separate skill-authoring decision beyond what
>   `learn` may apply unattended — flagging that possibility, not deciding
>   it.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

Verdict file records `"lesson": "proposed — pending approval"` for #2. A
human needs to approve, decline, or amend both #1 and #2 before either
lands in `project.md` — they are independent proposals; approving one is
not approving the other.

## next_action

**Mode 3 — the approved spec's Mode line is the standing "go."** This same
session continues to **Task 4** (Booth bridge: `~/.voicelock/faceprint.ref`,
on-demand set/compare/reset) — Task 3's wrap-up is the precondition, and it
just completed. **Both pending guardrails above need a human's attention at
the next touchpoint** — neither blocks Task 4.

## Commits

Session base → head: `adbe26b` → (this wrap-up's commits: verdict file +
`handoff.md` + `plan.md` DONE state). Nothing pushed.

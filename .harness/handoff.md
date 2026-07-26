# Handoff — F5 Tasks 1–2 `DONE`; Task 3 is next

Session of 2026-07-26. Tasks 1 and 2 built, verified (subagent) and wrapped up
`DONE`. Task 2's designed licence STOP condition fired, escalated, and resolved.
Tasks 3–7 `TODO`.

**One guardrail proposal is parked below and needs your yes/no.**

## Changed (Task 2)

- **`src/voicelock/models/face_landmarker/`** — `face_landmarker.task`
  (3 758 596 B, SHA-256 `64184E22…4E0BC9FF`), `LICENSE` (Apache-2.0, 11 357 B),
  `NOTICE` (source, date, size, hash, and the licence evidence chain).
- **Zero engine code.** `facedetect.py` is Task 4.

Gate 5/5 exit 0 (`pytest` **88 passed in 52.98 s**); Review APPROVE both axes,
first pass, `rejects: 0`. Verdict: `memory/verdicts/2026-07-26-F5-T2.json`.

The verifier re-derived the SHA-256 itself and re-ran the "the artifact embeds no
licence" scan rather than taking the `NOTICE`'s word — both held.

## ⚠ BUILDING IS PAUSED — `spec.md` box 2 needs your `x`

You approved **both** halves of the `learn` proposal (2026-07-26). The prose
guardrail is written into `project.md`. The enforcement check went into
`spec.md`'s Verification **Standing** list — and editing the spec is a **spec
amendment**, so per the spec's own footer and the universal `[Approval]` rule
("the standing go … never reaches past an amendment"), **box 2 is re-opened and
I stopped rather than starting Task 3.**

**What you do:** open `.harness/spec.md`, and in the Approval gate change
`- [ ] Approved by human` to `- [x] Approved by human`. I may never check that
box myself. Then say go and I continue at Task 3.

The amendment is narrow and is described in a note directly under the box: one
line added to the Standing list, nothing else — no scope, outcome, non-goal or
constraint changed. Re-scan of the changed section: **zero** clarification
markers, Grilling record stays `CLEAR`. Tasks 1–2 are unaffected (the new check
passes against both vendored model dirs today, verified before pinning).

If you would rather not amend mid-feature, the clean alternative is to revert the
spec line and let the check land in **F6's** spec instead — F6 adds the second
vendored model dir for SFace, which is arguably where it earns its keep anyway.
Say the word and I will back it out.

## The guardrail that was approved (now written)

The `learn` scan produced a lesson that cleared the bar. **Nothing has been
written to `project.md`**; that needs a human in every mode.

**Why it cleared:** it will recur *immediately* — Task 3 vendors `portrait.jpg`
behind its own licence STOP point, and roadmap **F6 adds a second vendored model
dir** for OpenCV's SFace — and it cost a full escalation cycle plus your
involvement, with the enabling technique taking well over 5 tool calls to find.
Overlap-checked against all three existing guardrails across problem, root cause,
fix, files and prevention: **zero overlap**.

**Proposed prose rule, in `project.md` format:**

> - **[Approval]** A vendored third-party asset's licence must be established
>   from a source that names **that asset** — the artifact itself, its
>   distribution page, or its model card. A permissive licence on the framework,
>   the wheel, or the source repo does **not** license separately-hosted weights
>   or data files. `block` · expires: 2027-01-31
>   - _Evidence:_ F5 Task 2 (2026-07-26). Eight primary sources said nothing
>     about `face_landmarker.task`'s licence: the artifact embeds none (all four
>     zip entries scanned, zero hits; TFLite metadata `license` field
>     unpopulated), the GCS bucket 404s on `LICENSE` at three paths, the official
>     guide licenses only "page content" and "code samples", the **Apache-2.0
>     `mediapipe` wheel ships zero model files**, and the **Apache-2.0
>     `google-ai-edge/mediapipe` repo ships only `.pbtxt` graphs and zero `.task`
>     bundles**. The answer was in Google's three model cards, which map 1:1 onto
>     the bundle's three `.tflite` models. Had "MediaPipe is Apache-2.0" been
>     accepted, the repo would have vendored a 3.7 MB binary on reasoning the
>     spec explicitly rules insufficient — and `spec.md` §4's own counter-example
>     shows it fails outright, since MediaPipe's face_detector sample ships a
>     **Pixabay**-licensed image whose terms restrict redistributing unaltered
>     copies.
>   - _Added:_ 2026-07-26

**Proposed enforcement to go with it** (`learn` step 5 prefers a mechanism over
remembered prose where one exists). The checkable half really is mechanical:

> add to the spec's standing Verification commands —
> every directory under `src/voicelock/models/*/` must contain a non-stub
> `LICENSE` **and** a `NOTICE`.

That enforces the *artifact* exists; whether the evidence behind it is
*sufficient* still needs judgment, which is why the prose rule stays too. Per the
`learn` skill this changes real code and goes through the normal spec/approval
path — **it is not applied during wrap-up**.

Say yes/no to each. Declining is a fine answer and I will record it as declined.

## Still open for the human

1. **Task 3 carries the second licence STOP point** (`portrait.jpg`), and it is
   **unrelated to Task 2's** — do not read this resolution as precedent. The
   spec's cited counter-example is that MediaPipe's own face_detector sample
   ships a **Pixabay**-licensed image. It may well not clear as easily, and if it
   does not, the spec's remedy is a **spec amendment** (human-only).
2. **`project.md`'s Environment section is stale** — *"Tool(s): Cursor only"*,
   *"Setup run: 2026-07-21"*, while this session ran in Claude Code. Re-running
   `setup` refreshes it.

## Carried forward, unchanged

- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback: `TARGET_FPS`
  30 → 20 → 15 **on measured evidence**, never by loosening the assertion, and
  never by reopening the rejected loopback-MJPEG transport without a fresh
  human decision.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit** — `read()` is the real
  path the fake must deliver through, `release()` the teardown it must trip on,
  with a **`BaseException`** subclass, since F4.5 proved a plain `Exception` is
  swallowed by blanket handlers.
- **The verifier path is settled** — subagent, human-authorized this session
  (`memory/decisions.md`), which closed the previous handoff's open item 1.

## Where the rest lives

- Task verdicts: `memory/verdicts/2026-07-26-F5-T1.json`, `-F5-T2.json`
- The licence investigation: `memory/research/2026-07-26-f5-face-landmarker-licence.md`
  (blocked) → `…-licence-resolved.md` (resolved; supersedes it)
- Decisions this session: `memory/decisions.md` (verifier path; licence resolution)
- Task ledger + the pinned `facedetect.py` module contract: `plan.md`

## next_action

**BLOCKED on the human re-checking `spec.md`'s box 2** (see the top of this
file). The approved `Mode:` line does not reach past an amendment.

Once checked: **`/implement` F5 Task 3 — "Vendor the `portrait.jpg` face fixture
+ its provenance README, licence verified at download".** Expect a possible
second escalation — and note Task 2's outcome is **not** precedent for it.

## Commits

- Task 1: `878186c` → `19b63e5` → `79b022e` → `b21b8ae` (`DONE`)
- Task 2: `be938c1` (DOING) → `e533720` (BLOCKED) → `6585761` (resumed +
  resolution) → `1ddf831` (build) → `bded558` (bookkeeping) → this wrap-up commit
- Task 2's Gate diff was `6585761..1ddf831`

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

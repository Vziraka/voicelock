# F5 — Camera booth · COMPLETION REPORT (Mode 3)

**Feature complete 2026-07-26.** 7/7 tasks `DONE`, live demo attested by the
human. Roadmap box checked, codebase map refreshed, ADR written.

**Awaiting only the feature-end commit checkpoint** — the proposed message is at
the bottom, and nothing is committed for it until you approve.

---

## Outcome vs the spec's Outcome section

`spec.md` §1 required three things to be true. All three are:

1. **The camera reaches the Booth.** Record opens the webcam and the face disk
   shows a live image instead of the smiley; Stop reverts it and releases the
   device; a second Record works. *Attested live.*
2. **The face is found and drawn.** Every frame goes through the vendored
   MediaPipe Face Landmarker; an **oval** (not a rectangle — it would clip
   against the circular mask) and a landmark overlay **including the lip
   contour** are composited in Python before the frame reaches the page. No face
   in view is a normal state, not an error. *Attested live + pinned by tests.*
3. **It stays offline.** The `.task` bundle is vendored and loaded from a local
   path. A source-level Gate assertion pins that `facedetect.py` contains
   `model_asset_path` and no URL.

The demo the spec asked for — *press Record → your face appears in the round
disk → an oval and landmarks track it → press Stop → the smiley comes back and
the camera light goes out* — was run and confirmed.

## Final Gate evidence (command → exit code)

| Command | Exit |
|---|---|
| `uv run ruff check .` | **0** — "All checks passed!" |
| `uv run pytest` | **0** — **122 passed**, 0 failed, 0 skipped |
| `uv run pytest tests/test_facedetect.py -q` | **0** — 26 passed |
| `uv run pytest tests/test_booth_api.py -q` | **0** — 27 passed |
| real model detects a real face vs the vendor reference | **0** |
| `facedetect.py`: `model_asset_path` present, no `http(s)` | **0** |
| `face_landmarker.task` present, > 1 MB | **0** |
| `mediapipe` + `opencv-contrib-python` declared, `opencv-python` absent | **0** |
| `tests/test_facedetect.py` mentions `release` / `read` | **0** |
| every `models/*/` carries a non-stub `LICENSE` + `NOTICE` | **0** |
| face fixture present (fetched-not-committed) | **0** |
| **throughput floor** | **0** — **10.3 ms/frame** vs a 33 ms budget |
| **manual live camera demo** | **human-attested 2026-07-26** |

Suite runtime ~36 s — well under the spec's 5-minute disclosure threshold, so no
disclosure is owed.

**The measured number that matters: 10.3 ms/frame**, from the Gate run, ~3×
headroom. **`TARGET_FPS` stayed at 30 on evidence**; §4's fallback ladder
(30 → 20 → 15) was never needed and the assertion was never loosened.

## Retry counts per task

| Task | `rejects` |
|---|---|
| 1 declare deps · 2 vendor bundle · 3 fixture · 4 composite · 6 Booth `<img>` | **0** |
| 5 camera lifecycle | **1** |
| 7 `BoothApi` wiring | **1** |

Both rejects were earned, and both were the same underlying weakness — surface
that *looked* covered:

- **Task 5:** drop-don't-queue was pinned only as a pure function; the
  loop-level assertion was true by construction. The verifier proved it by
  replacing `wait(pacing_delay(...))` with a flat `wait(FRAME_INTERVAL)` —
  deleting the behaviour — and watching all 23 tests still pass.
- **Task 7:** F4.5's 30-second cap ends a take with nobody pressing Stop, and
  `_pump_loop` never released the camera on that path. Record and walk away →
  the webcam light stays on indefinitely. Writing the test then exposed a second
  ordering bug (pump started before the camera).

Both fixes were **mutation-checked** — break the code, confirm the test fails —
and both verifiers repeated it independently.

## Escalations, both designed and both fired

`spec.md` §4 made each vendored asset's licence a stop condition. Both fired:

- **The model bundle CLEARED.** Eight primary sources say nothing about the
  weights' licence — the artifact embeds none, the bucket 404s, the docs cover
  only page content and code samples, the Apache-2.0 wheel ships **zero** model
  files, and the Apache-2.0 repo ships `.pbtxt` graphs and **zero** `.task`
  bundles. It was settled by Google's three **model cards**, all citing
  Apache-2.0, mapping 1:1 onto the bundle's three `.tflite` models.
- **The fixture did NOT clear.** MediaPipe's canonical `portrait.jpg` is a
  **White House press photograph** (EXIF `Artist: Pete Souza`) forbidding
  reproduction without written permission. Its "personal use only" clause is
  granted to *the subjects of the photograph*, not to personal projects — the
  correction that changed the decision. Resolved as **fetched-not-committed**:
  the image is `.gitignore`d and verifiably absent from all git history, while
  its Apache-2.0 vendor reference **is** committed, preserving an assertion
  against Google's own published coordinates that exists for this image and no
  other.

Two **spec amendments** followed, each with a fresh box-2 approval from you: the
enforcement check for the new licence guardrail, and the fixture arrangement.

## Deviations

`memory/deviations.md` has **no new entries** for F5. No rule proved impossible
to follow literally, and every judgment call went through a decision entry or an
escalation instead.

## Escalation-worthy things that resolved themselves

- **The verifier path** (`handoff.md`'s old open item 1) — `project.md` recorded
  "Verifier path: subagent" while this session ran under a no-subagent default.
  You authorized subagents at the top of the session; recorded before any build.
- **`mediapipe` 0.10.35 ships only `tasks`** — no `mediapipe.solutions`, so the
  familiar `FACEMESH_*` constants do not exist. The Tasks API's
  `FaceLandmarksConnections` was used instead, so the drawn subset comes from
  the vendor rather than hand-copied indices.

## What F6 inherits

- **The fetched-not-committed arrangement**, and the fact that it inverts F3's
  committed-fixture precedent. A fresh clone skips the real-model test until the
  image is fetched; the Gate's presence check makes that loud, not silent.
- **The two-faces gap** — F6 needs a same-person-close and a different-person-far
  probe, and F5 has one image. A researched CC0 shortlist is in
  `memory/research/2026-07-26-f5-fixture-replacement-candidates.md`.
- **`FrameResult.landmarks` carries all 478**, unflipped, so F6/F8 need not
  reopen `facedetect.py`.
- **SFace is F6's**, needing a second vendored model dir — and now a second
  per-asset licence check.
- **A camera error currently paints the *mic*-error banner** and never clears —
  logged to **F9**, which owns per-cause messaging.

---

## THREE things need your decision

### 1 · Three parked guardrail proposals (none written to `project.md`)

**A — from Task 5.** *Recommend: adopt.* Distinct from the existing
"no unexercised branch" rule: that catches surface with *no* test, this catches
surface with a test that would still pass if the behaviour were deleted.
> **[Forbidden]** A test must assert something that would **break if the
> behaviour were removed**. Before claiming a test covers behaviour X, delete or
> neuter X and confirm the test fails. `warn` · expires 2027-01-31

**B — from Task 3.** *Recommend: adopt.* An **update** to the existing
`[Approval]` licence rule, not a new guardrail.
> Append: **check the asset's own embedded metadata first (EXIF/XMP for images,
> bundle metadata for models)** — the most authoritative statement available and
> the cheapest to read.

**C — from Task 7.** *Recommend: adopt — the evidence is the strongest of the
three.* The same code path has now caused a defect in **two consecutive
features**: F4.5 existed because the 30-second cap deadlocked the audio
callback; F5 Task 7 was rejected because that same cap failed to release the
camera.
> **[Forbidden]** When an operation acquires a device or resource, **every path
> that ends the operation must release it** — including paths that end it
> without user action (timeouts, soft caps, error exits), not just the explicit
> Stop the tests and the manual check naturally drive. `warn` · expires
> 2027-01-31

Declining any is a fine answer and I will record it as declined.

### 2 · Curate is due: 10 tasks since the last curate

`project.md`'s stamp says *"verdicts then: 19"*; there are now **29**. That is
the threshold. Adding three guardrails on top of four makes it more pressing,
not less — you may prefer to run `/curate` first and decide the proposals inside
it.

### 3 · The feature-end commit checkpoint

Proposed message:

```
F5 complete: camera booth — live preview with face landmarks

7/7 tasks DONE, human-attested live demo. rejects: 1 on Tasks 5 and 7.

The Booth has an eye: pressing Record replaces the decorative smiley
with a live, mirrored, circular webcam preview in the same 172 px disk,
with an oval outline and landmarks — including the lip contour F8 needs
— tracking the face in real time. Stop, the 30s auto-stop, and window
close all release the camera.

Python owns the camera because file:// documents get no secure context
(adr/0004-python-owns-the-camera.md). It composites in Python because
this repo's Gate has zero JS tests, so that is the only arrangement the
Gate can assert on.

Engine throughput 10.3 ms/frame against a 33 ms budget, so TARGET_FPS
stayed at 30 on evidence rather than aspiration.

Both designed licence escalations fired. The model bundle cleared as
Apache-2.0 via Google's model cards. The fixture did not: MediaPipe's
portrait.jpg is a White House press photograph, so it is fetched and
gitignored, never committed, while its Apache-2.0 vendor reference is.

Suite: 122 passed.
```

**Remote: none** — this is a local commit only; there is nothing to push.

## next_action

**Human: approve the commit message** (and answer the three proposals + the
curate prompt). After that, F6 — Faceprint on screen — is the next roadmap
feature, and it starts with `/spec`. **(curate due)**

# Handoff — F5 spec APPROVED, ready for `/plan`

Session of 2026-07-26 (after F4.5 closed). Ran `/spec` for **F5 — Camera booth**.
No code was written and **nothing was installed** — `pyproject.toml` and
`uv.lock` are untouched.

**Approval gate: BOTH boxes checked 2026-07-26.** `Status: CLEAR`, zero
clarification markers, `Mode: Mode 3`. The gate is satisfied, so `/plan` is
unblocked.

**Repair recorded honestly:** the human's editor reformatted `spec.md` on
approval and, alongside harmless table/wrap changes, **deleted the 8-line
"that check has teeth" licence paragraph** in §4 — the entire content of commit
`beb21b3`, which the human had explicitly approved one message earlier. It was
restored verbatim on the human's instruction before the approval was committed.
The same formatter transposed backtick/asterisk in three places
(`` `**BaseException` ``, `` `**VIDEO**` ``, `` `**opencv-contrib-python` ``),
breaking emphasis without losing content; all three were corrected. A
word-level diff against `beb21b3` was used to confirm **nothing else** was lost —
not an eyeball pass.

> F4.5's completion report was previously here. It is closed and its evidence
> lives in `memory/verdicts/2026-07-26-F4.5-T1/-T2/-T3.json` and in git
> (`93bc887`, the feature-end commit).

## What this session produced

- **`spec.md`** — F5, `Status: CLEAR`, zero clarification markers, box 1 checked,
  **box 2 open for the human**. `Mode: Mode 3`, set by the human.
- **`memory/research/2026-07-26-f5-face-stack.md`** — the TECH-PICK research:
  four candidates, registry dates quoted, two ruled out on evidence.
- **`memory/research/2026-07-26-f5-camera-preview-transport.md`** — why the
  camera cannot be opened from JavaScript in this Booth.
- **`memory/decisions.md`** — two new entries (the TECH-PICK; the FaceView
  architecture), newest first.
- **`plan.md`** — memory-spine bullet 5 and the Active-context line updated to say
  the ledger is still F4.5's and is replaced by `/plan` after approval.

## The decisions the human made this session

1. **TECH-PICK → `mediapipe` + `opencv-contrib-python>=4.13,<5`** (candidate A).
   The discriminator was **F8**, not F5: MediaPipe gives 478 landmarks with a
   full lip contour and a `jawOpen` blendshape, where OpenCV's YuNet gives 5
   points — two mouth *corners*, which cannot express whether a mouth is open.
   InsightFace was blocked on a **non-commercial-research-only** model licence;
   facenet-pytorch failed the liveness bar (2024-04-29, ~27 months) **and** pins
   `torch<2.3.0` / `numpy<2.0.0` against this repo's `torch>=2.13.0` /
   `numpy>=2.0`.
2. **Python owns the camera; it composites the overlay and pushes one JPEG per
   frame.** The JS-owned alternative was eliminated on Microsoft's own WebView2
   docs, not on preference — `getUserMedia` is unavailable to `file://`
   documents, and `app.py:405` loads the Booth from a `file://` URL.
3. **FaceView replaces the Booth's decorative smiley in its existing 172 px
   disk, while recording.** The human's placement. Expanding it to a 440 px
   rectangle was explicitly **deferred, not refused** — "we can try 172px and we
   can expand if i want".
4. **The preview is round, and the face is outlined with an ellipse.** The human
   asked at the commit checkpoint whether it would be "a circle not a camera
   box", which caught that the draft's phrase "face box" blurred two shapes: the
   *container* (a circle, since `.face-disk` is `border-radius: 50%`) and the
   *drawn outline* (a rectangle, which would clip its corners against that mask).
   Resolved to an ellipse. The 4:3 frame is centre-cropped to a square, but
   **detection runs on the full frame first**, so an edge-of-frame face is still
   found.
4. **Mode 3**, and for the mandatory Mode-3 blind-spot question the human chose
   **both** mitigations: a required human-attested live check **and** an
   automated camera-release tripwire, plus a Gate-measurable throughput floor.

## Open items for the human

1. **Check box 2 in `spec.md`** — the agent never checks it.
2. **Five defaults the agent pinned rather than asked about.** None is
   architectural, all are reversible before `/plan`, and none was dropped
   silently — say the word on any and the spec is amended before planning:
   - capture at 640×480, downscale the composited image to 172 px;
   - target ~15 fps on a dedicated daemon thread, not `app.py`'s 50 ms pump loop;
   - draw the face box plus a landmark **subset** (face oval, eyes, lip contour)
     rather than all 478 dots on a 172 px disk;
   - MediaPipe `VIDEO` running mode, not `LIVE_STREAM` — synchronous and
     deterministic, so Gate tests cannot go flaky;
   - **no startup camera probe** — a missing camera surfaces on Record, so the
     app does not stall for seconds on every launch. This diverges from
     `_probe_mic` deliberately.
3. **A face-photo fixture with a permissive licence** is wanted so one test runs
   the **real** vendored model rather than an injected fake. Spec §4 says that if
   no suitably licensed image can be obtained, the limitation is **written into
   the Verification section** — never replaced by a silent proxy. Worth deciding
   before `/plan`.

## Two things carried in from F4.5, both honored

- **Task 2's fake-stream shape is the pattern F5's camera fake must copy.**
  Spec §4 says how that reads for a **polling** device: `cv2.VideoCapture` has no
  callback, so `read()` **is** the real path the fake must deliver through, and
  `release()` is the teardown it must trip on — with a `BaseException` subclass,
  as F4.5 proved is necessary against blanket `except Exception` handlers.
- **A per-module tripwire in the Verification section.** F4.5's was
  `assert 'callback' in <test file>`; F5's pins `release` and `read` in
  `tests/test_facedetect.py`, for the same reason and adapted to the real API.

## next_action

**`/plan` in a fresh session. Box 2 is checked — the gate is open.**

Expect roughly this task shape (the plan session decides for real): declare the
two dependencies · vendor the `.task` bundle and check its licence at download ·
build `facedetect.py` on an injectable fake camera · wire `BoothApi` to the
Record/Stop path · swap the smiley for the `<img>` in the Booth · land the live
check last, since it is the one Gate line an agent cannot run.

**Known risk to carry into the build:** nobody has measured what frame rate
`evaluate_js` sustains across pywebview's WebView2 bridge on this machine, and it
cannot be measured without installing the dependency. The 172 px preview is the
mitigation (~8 KB per frame); the required live check is the detector. If it is
choppy, the fallback ladder is: lower the frame rate → lower the JPEG quality →
reconsider the loopback MJPEG transport (rejected here, and the rejection is
recorded with its reason in `memory/decisions.md`).

## Commits

Base for this session: `a114a49` → head `cf97c77` (the spec commit), plus this
bookkeeping commit recording the pair.
Remote: **none** — local history only, nothing pushed.

## The eight defaults — four changed after review, four kept

Listed so none was dropped silently (the `grilling` skill's step 5). All were put
to the human; four were changed before approval, so they are plain edits, not
amendments.

**Changed:**

1. **Preview is now mirrored** (selfie view). `cv2.flip(img, 1)` runs **after**
   the overlay is drawn, so pixels flip and **no landmark coordinate does** — the
   cheap way, and the way that avoids mirror bugs. Detection stays on the
   unflipped frame, so F6/F7/F8 data is unaffected. Text, if ever added, must be
   drawn after the flip.
2. **Frame rate 15 → 30 fps** (human: 15 was too choppy). Two conditions carry
   more weight than the number: the rate is a **named constant**, and frames are
   **dropped, never queued** — a queueing pipeline drifts progressively behind
   reality, which looks like a freeze rather than a low frame rate. The Gate's
   throughput floor moved to **<33 ms/frame, set AT the target**, with an
   evidence-driven fallback to 20 then 15 if the hardware cannot meet it.
3. **Gate fixture pinned: MediaPipe's own `portrait.jpg`**, plus its published
   `portrait_expected_face_landmarks.pbtxt` as a vendor reference where practical.
   Same shape as F3's precedent. Explicitly **not** the owner's face — see below.
4. **The engine returns all 478 landmarks** while drawing only the subset, so F8
   does not have to reopen `facedetect.py` for the lip points.

**Kept as-is:** 640×480 capture (the bridge is the bottleneck, not the sensor) ·
MediaPipe `VIDEO` mode (deterministic Gate tests) · no startup camera probe ·
camera device index 0.

## The fixture-vs-identity distinction, since it came up

The human asked how they would verify it is *them* if the fixture is a stock
portrait. The two never meet, and the repo already works this way for voice:

| | Committed (the Gate) | Live, never committed (the human) |
|---|---|---|
| Voice | `speakerA_*.wav` / `speakerB.wav` — VoxCeleb strangers | their voice → `~/.voicelock/vault.vl` at runtime |
| Face | `portrait.jpg` — MediaPipe's test image | their face → the live check, and the vault at F7 |

The fixture proves the **model detects a face** with no camera and no human
present. **Identity** is proven by the required manual check and, from F7, by a
real enrollment. Committing the owner's photo would not make enrollment more
theirs — it would put their biometrics in git and make the fixture withdrawable,
i.e. a test that breaks later.

**Flagged for F6, not solved here:** F6 needs *two* faces (same-person-close,
different-person-far) and `portrait.jpg` is one image. F3 hit the same wall and
solved it by windowing one recording — a photo cannot be split that way. **F6's
spec must say where face B comes from.**

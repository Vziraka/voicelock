# Decision log (append-only)

The cheap paper trail. ADRs (`formats/ADR.md`) are for the rare hard-to-reverse
calls; EVERY approved decision lands here, so the next session inherits the
*why*, not just the code. A decision that exists only in chat does not exist.

Newest first. Never edit or delete old entries — supersede them with a new one.
One exception: `curate` may MOVE a superseded entry, whole and unchanged, into
the `## Archive` section at the bottom — human-approved, position changes,
content never does (see `skills/curate/SKILL.md` step 3).

Format:
- {YYYY-MM-DD} · **{decision in one line}**
  - why: {one line}
  - rejected: {alternatives and the one-line reason, or "none — human directed"}
  - link: {spec section · ADR · TECH-PICK table · commit}

<!-- entries go below this line -->

- 2026-07-26 · **F5 Task 2 UNBLOCKED: the Face Landmarker bundle is Apache-2.0 — established from Google's three model cards, per-asset, after eight other primary sources said nothing**
  - why: the task's designed licence STOP condition fired first, and correctly — the `.task` artifact carries **no** licence text in any of its four zip entries, the GCS bucket 404s on `LICENSE` at three paths, the official guide licences only *page content and code samples*, the Apache-2.0 `mediapipe` wheel ships **zero** model files, the Apache-2.0 `google-ai-edge/mediapipe` repo ships only `.pbtxt` graphs and zero `.task` bundles, Kaggle is JS-gated, and web results traced back to Apache-2.0 headers in *code samples* — the exact evidence class `spec.md` §4 rules insufficient. The answer was in the one place a machine could not read it: Google's three **model cards**, which are image-only PDFs with no extractable text and no OCR in this environment. **The human read them and reported the Apache-2.0 licence link (2026-07-26).** That report was then corroborated **mechanically** rather than taken on trust: PDF link annotations are plain objects even when the page is a flat scanned image, so extracting every `/URI` action showed `https://www.apache.org/licenses/LICENSE-2.0.html` present in **all three** cards — `Model Card MediaPipe Face Mesh V2.pdf` (the 478-landmark model), `MediaPipe BlazeFace Model Card (Short Range).pdf` (the detector) and `Model Card Blendshape V2.pdf` (the expression model) — which are exactly the three models the bundle repackages (`face_landmarks_detector.tflite`, `face_detector.tflite`, `face_blendshapes.tflite`). This satisfies the spec's demand that provenance be established **per asset on its own terms**, not inherited from the project that references it. Bundle vendored at 3 758 596 bytes, SHA-256 `64184E229B263107BC2B804C6625DB1341FF2BB731874B0BCC2FE6544E0BC9FF`.
  - rejected: **waiving the check and accepting "MediaPipe is Apache-2.0"** — offered to the human and declined in favour of reading the cards; it is the precise reasoning `spec.md` §4 forbids, and the spec's cited counter-example is real (MediaPipe's own face_detector sample ships a **Pixabay**-licensed image, whose terms restrict redistributing unaltered copies). **Substituting a different model** — forbidden outright by `spec.md` §4. **Fetching the weights to `~/.voicelock/` at first run instead of committing them** — a legitimate way to avoid redistribution entirely, but §4 mandates vendoring into the repo and §5 asserts the file exists under `src/`, so it would have been a spec amendment; unnecessary once the licence cleared. **Copying the `mediapipe` wheel's `LICENSE`** as the vendored licence text — rejected on inspection: it is Apache-2.0 **plus** appended third-party notices (Lucent/Plan 9) covering the wheel's *code*, so it would misdescribe the model. The repo's existing `models/ecapa/LICENSE` is pristine, unmodified Apache-2.0 (its appendix still reads `Copyright [yyyy] [name of copyright owner]`), so it was reused for consistency across both vendored model dirs.
  - accepted limits: the licence is established from the **model cards**, not from the `.task` file, which demonstrably embeds none — the vendored `NOTICE` states it that way rather than implying the artifact is self-describing. The three cards were read by a human and confirmed only by their *link annotations*; the surrounding sentence was not machine-verified, so the `NOTICE` records what was actually checked. A second, independent avenue (the Kaggle model page's licence field) remains unread because it is JS-gated — noted in case anyone wants belt-and-braces confirmation later.
  - link: `spec.md` (F5) §4 "The model" · `plan.md` Task 2 · `memory/research/2026-07-26-f5-face-landmarker-licence.md` (the blocked finding) · `memory/research/2026-07-26-f5-face-landmarker-licence-resolved.md` (the resolution) · commit `e533720` (the BLOCKED state this supersedes)

- 2026-07-26 · **F5 verification runs on the subagent path — the human explicitly authorized clean-context subagent verification for this feature**
  - why: `handoff.md`'s open item 1 parked a real conflict for the human. `constitution/project.md`'s Environment section already records *"Verifier path: subagent"*, but this build session runs in **Claude Code** under a standing instruction not to spawn subagents unless explicitly asked — and `universal.md`'s BUILD gate says a host with no clean-context subagent must NOT self-verify, it must commit, hand off, and stop for a fresh session. Asked at the top of the implement session, the human chose **subagent**, which resolves the conflict in favour of the already-recorded environment rather than changing it. Concretely: after each F5 task reaches `REVIEW`, this session spawns the verifier with `formats/VERIFIER-PROMPT.md` **verbatim** (filling only task id / base / head), and is the **executor** of the returned verdict per that template's closing frame — it runs the bookkeeping but never overrides, softens, or re-litigates the verdict; wanting to override is `ESCALATE_HUMAN`. Mode 3 therefore runs as designed across all 7 tasks instead of degrading to ~14 session restarts.
  - rejected: **fresh session per verify** — the documented default if the human said nothing, and legitimate (the handoff spelled out that not deciding means this happens); rejected because it costs a human touchpoint per task for no gain in context cleanliness, and the environment already declares the subagent path. **Self-verification** — never on the table in any mode; it is what both options exist to avoid.
  - accepted limits: a subagent is clean-context but not a fresh process — it inherits the repo, not the reasoning. The verbatim-template rule is what keeps it fresh eyes, so any temptation to "help" the verifier by shaping its prompt is a violation, not an optimization.
  - link: `handoff.md` open item 1 (2026-07-26 plan session) · `constitution/project.md` Environment · `constitution/universal.md` BUILD gate · `formats/VERIFIER-PROMPT.md`

- 2026-07-26 · **F5 refinements before approval: mirrored preview · 30 fps target with frame-dropping · MediaPipe's own `portrait.jpg` as the Gate fixture · the engine returns all 478 landmarks**
  - why: four changes made after the spec's first commit (`cf97c77`) and before box 2 was checked, so they are plain edits rather than amendments. **(a) The preview is mirrored.** Initially deferred as cosmetic, which was wrong: an unmirrored self-view makes people move the wrong way when centring themselves, and centring the face is the interaction F5 exists to support. What made it cheap is the composite-in-Python architecture — `cv2.flip(img, 1)` runs **after** the overlay is drawn, so the oval and landmarks are already in the pixels and flip with them; **no landmark coordinate is ever flipped**, which is exactly where mirror bugs come from. Detection runs on the unflipped frame, so the data F6/F7/F8 consume is unaffected. Recorded consequence: any text must be drawn after the flip or it renders backwards. **(b) 30 fps, not 15** (human's call — 15 read as too choppy), with two conditions that matter more than the number: the rate is a **named constant**, and frames are **dropped, never queued**. A queueing pipeline does not merely run slow, it drifts — the preview falls progressively behind reality, which reads as a freeze rather than a low frame rate. The Gate's throughput floor was moved from <100 ms/frame to **<33 ms/frame, i.e. set AT the target**: if the engine cannot sustain 30 fps alone, a 30 fps target is a fiction, and a red Gate is a better place to learn that than a stuttering demo. If it fails, the constant drops to 20 then 15 **on the measured evidence**, recorded in the completion report — never by loosening the assertion. **(c) The Gate fixture is MediaPipe's own `portrait.jpg`**, from the same project as the vendored bundle — the exact shape of F3's precedent, whose voice fixtures came from the SpeechBrain model repo's own example clips (Apache-2.0), the same source as the vendored ECAPA. MediaPipe additionally publishes `portrait_expected_face_landmarks.pbtxt` for that image, so the test can assert against a **vendor reference** rather than a self-generated expectation. **(d) The engine returns all 478 landmarks** even though only a subset (face oval, eyes, lip contour) is drawn — 478 dots on a 172 px disk is a blob, but a *display* decision must not narrow the *data* contract, or F8 has to reopen `facedetect.py` to reach the lip points that are F5's whole reason for existing.
  - rejected: **a photo of the repo's owner as the fixture** — the human asked the right question ("how am i going to test and to make sure its me... at enrollment"), which exposed a conflation worth recording: the *fixture* proves the model detects a face with no camera and no human present; *identity* is proven live, in the required manual check, and at F7 by enrolling into `~/.voicelock/`. The two never meet. The repo already works this way for voice — it holds two VoxCeleb strangers while the owner's actual voice exists only at runtime, outside git. Committing the owner's face would not make enrollment more theirs; it would put their biometrics in version control and make the fixture withdrawable, i.e. a test that breaks later. **Flipping landmark coordinates instead of pixels** to achieve the mirror — more code, and the classic source of overlay-on-the-wrong-side bugs; a Gate test now pins that the coordinates stay unflipped. **Leaving the frame rate at 15** — the human judged it too choppy, and 30 is achievable in principle at 172 px (~8 KB/frame).
  - accepted limits: 30 fps is a **target, not a measurement** — nobody has yet run MediaPipe on this machine, and the `evaluate_js` bridge remains unmeasured. The floor-at-target Gate line is designed to fail loudly if the engine cannot keep up. **F6 inherits an unsolved problem, named on purpose:** it needs *two* faces (same-person-close, different-person-far) and `portrait.jpg` is one image — the same wall F3 hit, and a photo cannot be windowed the way a recording was. F6's spec must say where face B comes from; F5 does not quietly settle it.
  - link: `spec.md` (F5) §1/§2/§4/§5 · commit `cf97c77` (the spec this refines) · `tests/fixtures/voiceprint/README.md` (the precedent followed)

- 2026-07-26 · **F5 FaceView: Python owns the camera and pushes a composited JPEG; the preview replaces the Booth's decorative smiley face in its existing 172 px circle, only while recording**
  - why: **(a) Python owns the camera — this is a fact, not a preference.** `app.py:405` loads the Booth with `url=UI_PATH.as_uri()`, a `file://` URL, and Microsoft's WebView2 documentation (page `updated_at` 2026-06-12) states that APIs requiring a secure context "are not available to documents loaded by file URLs. This includes APIs such as `navigator.mediaDevices.getUserMedia()`". So the JS-owned-camera architecture does not exist here without rebuilding F1's window bootstrap onto virtual host name mapping, a WebView2-native API pywebview's Python surface does not expose. It also happens to match `project.md`'s standing division of labor and MediaPipe's Python API, which takes frames it is handed rather than opening a device. **(b) Composite in Python** — OpenCV draws the box and landmarks onto the frame, which is JPEG-encoded, base64'd and pushed into an `<img>` via `evaluate_js`. Chosen over pushing raw frames plus landmark coordinates for JS to draw: this repo's entire Gate is pytest with **zero** JS tests, so compositing in Python is the only option whose visible output the Gate can actually assert on, and it makes overlay-vs-frame drift structurally impossible rather than merely unlikely. **(c) The preview replaces the decorative smiley** (`index.html:590-600`, a 118 px SVG face on the 172 px `.face-wrap` disk) **in place, while recording, and reverts on stop** — the human's call, and a good one: it is the Booth's existing focal point, so FaceView becomes the visual analog of the Visualizer with **zero layout shift**. **(d) 172 px, staying inside the circle** — also the human's call, with expanding to a larger rectangle explicitly kept open as a later change if the small preview disappoints. The size is a material risk reduction, not just an aesthetic: a 172 px JPEG is roughly 8 KB where a 440 px one is ~5× that, and `evaluate_js` throughput across pywebview's WebView2 bridge is the single unmeasurable risk in this feature. **(e) the preview is round, and the face is outlined with an ellipse rather than the conventional rectangle** — the human asked the right question at the commit checkpoint ("will it be a circle not a camera box?"), which exposed that "face box" in the draft blurred two different shapes. `.face-disk` carries `border-radius: 50%`, so the 4:3 frame is centre-cropped to a square and masked to the circle, and a rectangular detector box would clip its corners against that mask whenever a face nears the edge. Detection still runs on the **full** frame before the crop, so an edge-of-frame face is found even when the crop hides it.
  - rejected: **JS `getUserMedia`** — eliminated on Microsoft's documentation, above; it is not a matter of granting a permission, the API is absent from the document's context. **Raw JPEG + landmark coordinates drawn on a JS `<canvas>`** — prettier, matches the Booth's CSS language, and genuinely tempting; rejected because none of that JS would be covered by the Gate and the dots can lag their frame when image and coordinates are applied separately. **A loopback MJPEG HTTP server** — by far the best throughput and the browser decodes natively, but it adds a listening socket to an app whose stated rule is "offline-only — no network at runtime"; loopback is not egress, yet it is new surface and a new failure mode for a demo that does not need the frame rate. **Expanding the disk into a 440 px screen on Record** — deferred, not refused: the human asked to try 172 px first and expand only if wanted.
  - accepted limits: the overlay is drawn by OpenCV, so it looks like OpenCV rather than like the Booth's CSS — restyling is F9 polish, not F5. The sustainable frame rate through `evaluate_js` is **unmeasured** and cannot be measured without installing the dependency, which TECH-PICK forbids before approval; the spec therefore pins a measurable floor instead of assuming smoothness. Camera-open failure has no startup probe (unlike `_probe_mic`) — a missing camera surfaces when Record is pressed, to avoid a multi-second stall on every app launch.
  - link: `roadmap.md` F5 · `memory/research/2026-07-26-f5-camera-preview-transport.md` · `spec.md` (F5) §3/§4 · `src/voicelock/ui/index.html:590-600`

- 2026-07-26 · **F5 TECH-PICK: MediaPipe Face Landmarker for detection + landmarks, `opencv-contrib-python` (pinned `>=4.13,<5`) for camera frames**
  - why: F5 only needs "a box and some dots that track a face", but the pick has to carry to **F8**, whose liveness mechanism is mouth-aperture-vs-audio-envelope. MediaPipe outputs **478 landmarks including a full lip contour**, plus a `jawOpen` blendshape — a ready-made aperture signal — where OpenCV's YuNet gives only 5 points (two of them mouth *corners*, which cannot express whether a mouth is open). Everything else follows the ECAPA precedent: the `.task` bundle loads from a local path via `BaseOptions(model_asset_path=...)`, so it vendors offline exactly like `models/ecapa/`, and it is Apache-2.0 throughout. MediaPipe's `LIVE_STREAM` mode delivers through a `result_callback`, which fits the callback-testing guardrail added 2026-07-26 rather than fighting it. Liveness quoted: mediapipe 0.10.35 wheel `mediapipe-0.10.35-py3-none-win_amd64.whl` uploaded `2026-04-27T17:45:33.946332Z` (PyPI JSON), 2,515,402 downloads last month; opencv-contrib-python 4.13.0.92 released 2026-02-05, 8,487,096 downloads last month. **OpenCV enters the manifest no matter which candidate wins** — nothing in the candidate set opens a webcam, and `cv2.VideoCapture` is the path; it also brings `FaceRecognizerSF` (SFace) in-box, so F6's embedding costs no further dependency. `opencv-contrib-python` and not `opencv-python`: both install a top-level `cv2` and installing both shadows; MediaPipe pulls the contrib build, so declaring **that** one keeps a single `cv2` and closes the undeclared-transitive gap before it bites (the F4.5 `soundfile` lesson applied in advance). Resolution proved, not assumed: `uv pip compile --python-version 3.11` against the repo's current eight dependencies plus the candidates resolves to `mediapipe==0.10.35`, `opencv-contrib-python==4.13.0.92`, `numpy==2.2.6`, `torch==2.13.0` — nothing moves, so F3's `ACCEPT_CUTOFF` and F4's `CORRECTION_RADIUS` are undisturbed. Nothing was installed; `git status --porcelain` was empty before and after.
  - rejected: **OpenCV alone (YuNet detect + SFace embed)** — one dependency instead of two and genuinely sufficient for F5's own demo, but YuNet emits 5 landmarks and the zoo README still says "5-landmark warping for now", so F8 would need a second face TECH-PICK and a second vendored model; it defers cost rather than avoiding it. **InsightFace `buffalo_l`** — technically the strongest single answer (SCRFD detect + 106-point landmarks incl. lips + ArcFace), but its pretrained models are licensed "for **non-commercial research purposes only**, including both auto-downloading models and manual-downloading models", where every other model in this repo is Apache-2.0; it also needs `onnxruntime` **and** OpenCV (three new entries) and a 326 MB pack to vendor, and its release history is 0.7.3 (2023-04-02) → 1.0.1 (2026-05-23), a ~3-year gap. **facenet-pytorch** — the instinctive pick because torch is already installed, and **wrong on evidence**: 2.6.0 released 2024-04-29 (~27 months, fails the ~12-month bar) and it pins `torch<2.3.0` / `numpy<2.0.0` against the repo's `torch>=2.13.0` / `numpy>=2.0`, an unresolvable conflict that would downgrade the stack F3 and F4 were measured against. **`opencv-contrib-python>=5`** — 5.0.0.93 is real and live (2026-07-02) but three weeks old and a major-version bump; F5 uses nothing from it, so 4.13.0.92 spends less risk for the same `VideoCapture`.
  - accepted limits: MediaPipe provides **no** face-identity embedding — its `ImageEmbedder` is a general image embedder, not a face-recognition model — so F6/F7 will key on OpenCV's SFace, meaning **two** vendored model directories by F7 rather than one. The `.task` bundle's exact byte size and its own licence text are `unconfirmed` at pick time (the model page states neither) and must be checked at download, before vendoring. No registry can answer whether a Python-side OpenCV camera loop co-operates with a pywebview window on this machine; that is an architecture question settled in the spec, not a liveness question.
  - link: `roadmap.md` F5 · `memory/research/2026-07-26-f5-face-stack.md` · `spec.md` (F5) §4 Constraints · `formats/TECH-PICK.md` comparison run 2026-07-26

- 2026-07-26 · **F4.5 inserted into the roadmap as a pre-F5 hygiene feature, at Mode 3**
  - why: the 2026-07-26 calibration run found a live self-deadlock in the PortAudio callback (`capture.py:110-121` calls `stream.stop()` from inside the callback, which blocks until the callback returns) and the reason it was never caught — `tests/test_capture.py`'s `FakeStream` never invokes the callback it is handed, so `_on_audio` has **zero** coverage. The human chose to fix both BEFORE F5 rather than folding them into F9, because F5 adds a camera stream with its own frame callback and would copy today's fake-stream pattern. Fixing the test pattern before it is inherited is cheaper than fixing two copies of it. Recorded as roadmap entry **F4.5** (rather than off-roadmap) so wrap-up has a checkbox and the gap in the build sequence stays explained; F5's `blocked-by` now names it.
  - rejected: **folding these into F9 — Demo reliability** (where the calibration findings originally filed them — rejected because F5 would inherit the broken fake-stream pattern first, which is the entire point of the pause); **off-roadmap `Feature: none`** (leaves wrap-up no box to check and the roadmap unable to explain the pause); **front-loading F5's TECH-PICK research into this session** (legal — it writes to `memory/research/`, not `spec.md` — but splits attention across two features and the findings would sit unused until F4.5 lands)
  - link: `roadmap.md` F4.5 · `.out-of-scope/2026-07-26-calibration-findings.md` items 1–2 · `memory/verdicts/2026-07-26-CALIBRATION-RUN.md`

- 2026-07-26 · **F4.5 TECH-PICK: declare `soundfile` as a MAIN dependency (`uv add soundfile`) — no code change**
  - why: `voiceprint.py:150` imports `soundfile` inside `load_wav`, but it is in no manifest — it reaches the environment only as a SpeechBrain transitive (`uv.lock` line 1372). If SpeechBrain drops or renames that transitive, every voiceprint and middlelock test breaks with no local change. Declaring it is a one-line `pyproject.toml` edit with **zero** code change, which is what makes it the right call here: F3's `ACCEPT_CUTOFF = 0.45` and F4's `CORRECTION_RADIUS = 110` were both pinned against soundfile-decoded fixtures, so any option that alters the decode path risks invalidating measured constants for no functional gain. Liveness: soundfile 0.14.0 published `2026-06-06T08:58:47.869Z` (`uv.lock` registry metadata) — ~7 weeks old, well inside the ~12-month bar; adoption is evidenced by its being a SpeechBrain requirement; docs current.
  - rejected: **`torchaudio` (already a declared dep)** — looked like the zero-cost answer and is what the calibration note suggested first, but it is **DEAD on evidence**: `torchaudio.load` on 2.11.0 raises `ImportError: TorchCodec is required for load_with_torchcodec`, so it would add torchcodec, a genuinely new dependency. (`torchaudio.functional.resample` is unaffected and stays.) **`--group dev soundfile`** — more honest, since `load_wav` has no caller in `src/` and only three test files use it, but it leaves a production module importing a dev-only package; doing it properly means relocating `load_wav` into `tests/`, which is bigger than this feature. **stdlib `wave` + numpy** — genuinely viable (all 11 fixtures verified mono/16-bit/16 kHz) and adds nothing to the manifest, but it is the only option that edits `voiceprint.py`, and it would require proving decoded samples are bit-identical before F3/F4's measured cutoffs could be trusted.
  - accepted limits: this declares a main dependency that **no runtime code path currently uses** — `load_wav` is exercised only by tests today. Accepted knowingly: the module offers the capability, the app installs all dependencies anyway, and the alternative costs more than it saves.
  - link: `spec.md` (F4.5) Constraints · `formats/TECH-PICK.md` comparison run 2026-07-26 · `.out-of-scope/2026-07-26-calibration-findings.md` item 2

- 2026-07-26 · **F4 Task 2 build-time choices: Argon2id-backed commitment · INTERACTIVE cost · soft decoding kept despite a null fixture result · centering measured and dropped**
  - why: **(a) the commitment tag and the SecretBox key both derive from ONE Argon2id stretch under different info strings.** Spec §4 pins `H(s)` in the helper data, and with `KEY_BITS = 32` a plain `sha256(s)` would let anyone who has already peeled the outer lock enumerate 2³² candidates in seconds — the middle lock would add nothing. Making each guess cost a memory-hard KDF restores the point of the layer without changing the helper's pinned structure. **(b) Argon2id at INTERACTIVE, not MODERATE:** the outer passphrase lock already pays MODERATE and this layer is only reachable once the outer lock has fallen; two stretches run per unlock and the whole suite still finishes in ~11 s. **(c) soft-decision decoding kept** even though it made no measurable difference on the fixtures (worst genuine 51 either way; impostor floor 167 soft vs 165 hard) — the fixtures never approach the decision boundary, so no reweighting *can* change the outcome there; it cannot lose to hard voting and the fixtures under-represent the noise a live cross-session unlock brings. **(d) tolerance pinned from 200 independent commits**, not one lucky projection: genuine 0, harder same-speaker 63, impostor floor 156, so `CORRECTION_RADIUS = 110` is the midpoint of a real gap.
  - rejected: **a bare `sha256(s)` commitment** (brute-forceable behind the outer lock at this key length — see ADR 0003); **switching to hard-decision majority** on the strength of the null fixture result (spec §4's fallback clause is permissive, `plan.md` lists lever 1 as required, and optimizing for an easy fixture set is optimizing against the live demo); **adopting lever 6 (centering)** — the vendored `mean_var_norm_emb.ckpt` is genuinely NOT applied (`encode_batch`'s `normalize` defaults to `False` and `voiceprint.embed` never passes it), but enabling it moved the genuine/impostor gap by 1 bit and would require editing F3's `voiceprint.py`, which spec §4 forbids; **a longer secret** (steals the bit budget from repetition depth, the thing that absorbs real voice noise).
  - accepted limits: 32 bits of secret entropy is weak by product standards — the honest defence is the KDF cost per guess plus the fact that this layer sits inside the passphrase lock, exactly as spec §3's non-goals already state. The correction radius cannot admit a wrong voice at any width (the commitment tag is authoritative); it only trades a cheap early reject against genuine false-rejects.
  - link: `adr/0003-middle-lock-commitment-costs-a-kdf.md` · `src/voicelock/middlelock.py` · `plan.md` Task 2 build-notes · commit `469a4cd`

- 2026-07-26 · **F4 reconcile accuracy: five required levers added by spec amendment (§3/§4); emotion-varied enrollment rejected**
  - why: the approved construction alone left a genuine bit-error of ~25 % against an impostor's ~45 % — too narrow a gap to both admit the real speaker and reject an impostor. The five levers attack it from independent angles: (1) **soft-decision decoding** — weight each vote by projection magnitude instead of counting hard signs, roughly doubling absorbable noise for ~5 lines of numpy; (2) **cross-take unanimity** as the reliability filter — a direct measurement of stability across the 5 enrollment takes, where large-margin alone is only a proxy; (3) **large LSH candidate pool (~2048–4096) masked hard down to ~512** — same final bit count, 1-in-8 selection pressure instead of 1-in-2, free at rest since only the seed is stored; (4) **short key (~32 bits) with deep repetition (~16×)** instead of a long shallow key — depth absorbs noise, and the middle lock sits INSIDE the passphrase lock so the voice key is never attacked until Argon2id has already fallen; (5) **longer, window-averaged captures on both sides** — enrollment averaged 5 takes while unlock had 1, making unlock the noisier half.
  - rejected: **deliberately varying emotion / pitch / vocal effort across enrollment takes** (human's idea, thought through and declined — it sounds like useful coverage but widens between-take spread, starving lever 2's unanimity filter, and leaves the unlock voice at the edge of the enrolled range rather than its centre; phonetic variety yes, stylistic variety no); **raising the enrollment count above 5** (total speech time is the real lever and 5 longer sentences already covers it; the count is a human spec choice and changing it buys nothing); **a 128-bit key** (steals the bit budget from repetition depth — the failure mode is an ~18 % lockout rate); **relying on centering / mean-subtraction** (kept as test-only, low confidence: `mean_var_norm_emb.ckpt` may already apply it, and two fixture speakers cannot estimate a background mean); **skipping the spec amendment and recording this in `decisions.md` alone** (the verifier reads only universal/project/spec/plan/handoff — `decisions.md` is invisible to it, so an unamended spec would have put the Spec axis at real REJECT risk on the "~512 bits" and "majority-vote" wording)
  - accepted limits: the research's binomial estimates assume independent bit flips; with only 192 real dimensions the expanded bits are correlated, so measured results will be **worse** than the arithmetic predicts. Fixture takes are ~1 s (source audio is ~3.3 s total) versus 3–5 s in a real enrollment, so fixtures are a harder test than the live demo — a failure to separate may indict the fixtures, not the construction. Widening the correction radius to force a pass is forbidden.
  - link: `spec.md` §0 AMENDMENT 2026-07-26 · §3 Enroll/Unlock flow · §4 keystone + Accuracy levers + Reconcile tolerance · `plan.md` Tasks 1/2/4/5 · `memory/research/2026-07-23-f4-fuzzy-reconcile.md`

- 2026-07-23 · **F4 fuzzy reconcile: hand-rolled pure-numpy code-offset fuzzy commitment (NO new dependency)**
  - why: the ECC library is NOT the hard part — research shows raw 192 sign-bits give ~25% genuine bit-error, which no code absorbs while carrying a key; the real work is seeded LSH bit-expansion + reliability masking (pure numpy). Glass-box, offline-trivial, honest for a learning demo. Recognized construction (Juels–Wattenberg 1999 / Dodis et al. fuzzy extractor).
  - rejected: `bchlib` (liveness FAIL — ~22mo stale, native C extension); `reedsolo` (liveness gray-zone ~14.5mo + Reed-Solomon is symbol-based, poor bit-level Hamming fit); `komm` (live, numpy-only, ships a real BCH decoder — offered as the "named ECC library" option, GPL-3.0; human chose hand-roll since the dep buys only the easy last step); `galois` (live but heavy — numba/llvmlite)
  - link: `roadmap.md` F4 · `memory/research/2026-07-23-f4-fuzzy-reconcile.md` · `spec.md` §4 Constraints
- 2026-07-23 · **F4 accuracy: 5-sentence averaged enrollment + reliability mask + fixture-pinned correction radius; full tuning + enrollment-quality gate stays F9**
  - why: enrollment richness + reliability selection are the real accuracy levers; human chose a richer 5-sentence read over F3's 3-take for a steadier voiceprint. Correction radius pinned empirically from fixtures with a deterministic same-accepts / different-rejects test (analog of F3's ACCEPT/REJECT cutoffs).
  - rejected: 3-take (F3 parity, less enrollment data); pulling F9's full tolerance-UI + quality-gate into F4 (scope creep)
  - accepted limits: not product-grade — small false-reject rate, non-zero false-accept for a very similar voice, replay of the enrolled voice still passes (defended in F8), no FAR/FRR guarantees
  - link: `spec.md` §3/§4 · `roadmap.md` F4/F9
- 2026-07-23 · **F4 Mode 3 (Spec-to-done)**
  - why: F3 completed cleanly at Mode 3 (Mode 4 now unlockable); human chose Mode 3. The security-critical keystone is human-approved inside the spec (above) before any building, bounding Mode 3's autonomy to an approved design.
  - rejected: Mode 2 (extra final-verdict touchpoint — not wanted); Mode 4 (auto-draft F5 — not wanted now)
  - link: `spec.md` §0 Approval gate

- 2026-07-22 · **F3 voiceprint method: SpeechBrain ECAPA-TDNN (`spkrec-ecapa-voxceleb`)**
  - why: best-quality + actively-maintained speaker embedding for crisp same-vs-different separation; human chose quality over offline-friction
  - rejected: Resemblyzer (liveness FAIL — abandoned 2023 — + unconfirmed Py3.11/torch install); librosa DIY MFCC (maintained + offline but muddier separation)
  - cost accepted: weights must be **vendored locally + `HF_HUB_OFFLINE`** so no runtime network (SpeechBrain downloads from HuggingFace at first use); heaviest install (torch 2.1 + torchaudio)
  - link: `roadmap.md` F3 · `memory/research/2026-07-22-f3-voiceprint-embedding.md` · `spec.md` Constraints (F3)

- 2026-07-22 · **Pivot: augment to three biometric factors (voice + face + lips), not replace voice**
  - why: richest demo arc — wrong passphrase / voice / face / replay each fail a distinct factor
  - rejected: face+lips replacing voice (loses the voice work); face for liveness only (weaker identity story)
  - link: `roadmap.md` The idea · Approach · `adr/0002-three-nested-locks.md`

- 2026-07-22 · **Approach B′ — three nested locks: passphrase → voice → face**
  - why: keeps each factor an independent, nameable failure; extends the two-lock Approach B rather than fusing keys
  - rejected: fusing voice+face into one inner key (blurs which factor failed — same reason a combined key was rejected in F1/F2 era); face as a match-gate only (wouldn't seal bytes)
  - link: `roadmap.md` Approach · `adr/0002-three-nested-locks.md` · supersedes `adr/0001-two-stacked-locks.md`

- 2026-07-22 · **Passphrase stays typed (not spoken)**
  - why: outer key needs exact bytes (Argon2id); a spoken passphrase via STT is fragile (one misheard char = lockout), leaks the secret aloud, and needs a new dependency
  - rejected: spoken passphrase via offline STT; dropping the passphrase (undoes F2, loses "something you know")
  - link: `roadmap.md` Approach

- 2026-07-22 · **Liveness = audio-visual lip-sync to a spoken challenge**
  - why: one capture proves words match challenge (anti-replay) + voiceprint + faceprint + lips move in time (live person); defeats photo, audio-only replay, muted video
  - rejected: mouth-movement-only (any talking-head passes); visual lip-reading (offline lip-reading model, brittle, heavy)
  - link: `roadmap.md` The idea · F8

- 2026-07-22 · **Build order (Order A): voice fully, then face, then liveness, then reliability**
  - why: each modality is a complete working lock before the next starts; always a working thing
  - rejected: both on-screen signals first then both locks (no full lock until later); coarser one-feature-per-modality slices (thicker, less demoable)
  - link: `roadmap.md` Features

- 2026-07-22 · **F2 Mode 3 + live Booth enroll/unlock/REJECT as required Verification**
  - why: Mode 3 autonomy; Gate must not pass if only temp-path tests work and the Booth never seals ~/.voicelock/vault.vl
  - rejected: treating live Booth as accepted risk / waived check
  - link: `spec.md` Approval · Verification · Constraints

- 2026-07-22 · **F2 no-vault unlock copy: "No vault yet — enroll first"**
  - why: actionable status when Unlock is hit before enroll
  - rejected: "Vault missing"; custom wording
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 vault file layout: VLCK magic + version + salt + ciphertext**
  - why: one self-describing file; version leaves room for F4 format bumps
  - rejected: salt+ciphertext only; JSON sidecar + separate blob
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 Argon2id cost: OPSLIMIT_MODERATE / MEMLIMIT_MODERATE**
  - why: demo-snappy stretch of the passphrase without pretending product-grade hardness
  - rejected: INTERACTIVE (weaker story); SENSITIVE (sluggish demo)
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 Booth UX: wire mock Enroll + passphrase Unlock; keep F1 record/play**
  - why: mock already sketches the flow; end-to-end demo without a throwaway panel
  - rejected: separate minimal panel; engine-only / script unlock
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 enroll: name + passphrase only; sealed payload = display name (no audio)**
  - why: outer lock is passphrase; recording already proven in F1; voice auth is F3/F4
  - rejected: required recording placeholder; optional take-if-present
  - link: `spec.md` Constraints · Non-goals

- 2026-07-22 · **F2 vault path: single profile at ~/.voicelock/vault.vl; re-enroll overwrites after confirm**
  - why: fixed, inspectable demo location outside the repo; one vault keeps F2 thin
  - rejected: project-local cwd vault; multi-profile in F2
  - link: `spec.md` Constraints

- 2026-07-22 · **F2 outer lock crypto: PyNaCl (Argon2id + SecretBox)**
  - why: one dep covers passphrase KDF + AEAD seal for the learning vault demo
  - rejected: cryptography (broader, more wiring); stdlib-only (no suitable AEAD)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f2-outer-lock-crypto.md`

- 2026-07-22 · **F1 visualizer: bars**
  - why: clearest “levels reacting” demo signal; mock default
  - rejected: orb / rings (prettier, less obvious as loudness)
  - link: `spec.md` Constraints

- 2026-07-22 · **F1 capture format: 16 kHz mono**
  - why: speech band is enough for demo + later voiceprint; smallest sensible buffers
  - rejected: 48 kHz mono (heavier, little identity gain); stereo hi-rate (waste for who-are-you)
  - link: `spec.md` Constraints

- 2026-07-22 · **F1 UI: use voicelock-mock.html chrome; only record/viz/play live**
  - why: mock already sketches the full product; polish later; avoids a throwaway minimal booth
  - rejected: booth-only strip-down (loses project context); full mock interactive in F1 (scope creep)
  - link: `spec.md` Constraints · Non-goals

- 2026-07-22 · **F1 Mode 3 + live Booth manual check in Verification**
  - why: Mode 3 autonomy; blind spot is pywebview/live mic not covered by fake-stream tests
  - rejected: waiving the live-window check (would let Gate pass a dead Booth)
  - link: `spec.md` Approval · Verification

- 2026-07-22 · **F1 audio: sounddevice + numpy**
  - why: live PortAudio bindings with array I/O and injectable streams for Gate tests
  - rejected: PyAudio (fails ~12-month liveness bar); DIY WASAPI/ctypes (F1 time sink)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f1-audio-capture.md`

- 2026-07-22 · **F1 UI shell: pywebview**
  - why: light native webview + JS↔Python bridge fits Booth without Chromium weight
  - rejected: PySide6+WebEngine (heavy Qt/Chromium); Eel (Alpha, Chrome-shaped)
  - link: `spec.md` Constraints · `memory/research/2026-07-22-f1-ui-shell.md`

- 2026-07-22 · **Stack: Python 3.11 + uv; JS UI for looks; UI shell TECH-PICK at F1**
  - why: offline audio/crypto/voiceprint brain in Python; mock-based booth stays HTML/CSS/JS
  - rejected: Electron/TS-first (ML path harder); bare pip (no lockfile discipline)
  - link: `constitution/topics/conventions.md` · `constitution/project.md`

- 2026-07-22 · **Layout: src/voicelock (+ ui/), tests/, design/ mock reference**
  - why: clear brain/looks split; mock is starting chrome not final
  - rejected: none — human accepted recommendation
  - link: `constitution/topics/conventions.md`

- 2026-07-22 · **Gate: uv run ruff check . · uv run pytest**
  - why: simple, standard Python checks; promises until F1 wires them
  - rejected: none — human accepted recommendation
  - link: `constitution/project.md`

- 2026-07-22 · **Anti-spoof bar: speaker match + challenge-response; no deepfake-proof claim**
  - why: full three-impostor demo without lying about live voice cloning
  - rejected: strong anti-deepfake as a must-have (research-heavy, oversell risk); robotic heuristic parked as optional F7
  - link: `roadmap.md` Intent · Out of scope

## Archive

Superseded entries, MOVED here by `curate` (2026-07-26) — never edited, never
deleted. They were true when made; a later decision replaced them. Kept so the
reasoning chain stays readable.

- 2026-07-22 · **Approach B — two stacked locks for the profile vault**
  - why: always-both factors with crisp, independent impostor rejects for a learning demo
  - rejected: A voice-as-gate-only (voice wouldn't seal bytes); C single combined key (failures blur)
  - link: `roadmap.md` Approach · `adr/0001-two-stacked-locks.md`
  - _Superseded by:_ 2026-07-22 **Approach B′ — three nested locks: passphrase → voice → face** (and `adr/0002-three-nested-locks.md` supersedes `adr/0001`). Archived 2026-07-26.

- 2026-07-22 · **Must-build F1–F6; park F7 (weak robotic heuristic)**
  - why: full demo arc at F5; F6 makes it presentable; F7 is optional exploration only
  - rejected: bundling F7 into the must-build path
  - link: `roadmap.md` Features
  - _Superseded by:_ the three-factor pivot and the Order A build order — the feature numbering this entry describes no longer exists (today's F7 is "Face as the inner lock", F8 is lip-sync liveness, F9 is demo reliability). Archived 2026-07-26.

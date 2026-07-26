# Research — F5 offline face detect / landmark / embedding stack

- Date: 2026-07-26
- Question: which offline Python stack gives the Booth a live camera preview with
  face detection + facial landmarks (F5), and carries through to a face embedding
  (F6/F7) and **lip** landmarks for lip-sync liveness (F8)?
- Playbook loaded: `formats/source-playbooks/library-evaluation.md`
- CUI status: `constitution/topics/cui.md` says **INACTIVE** → normal research tier,
  external primary sources allowed.
- Prompted by: `roadmap.md` F5's `TECH-PICK:` marker.

One claim per line, each with its source and the date of the evidence.

## Scope note — this is a stack question, not a single-library question

Three capabilities are needed across F5–F8, and no single candidate covers all
three well:

1. **Camera frames** — open the webcam, pull frames.
2. **Face detection + landmarks** — box + landmark points on the preview (F5),
   and specifically **lip contour points** later (F8).
3. **Face embedding** — a vector for identity distance (F6) and the inner-lock
   key (F7).

The landmark requirement is the discriminator. F8's liveness is *lip-sync*:
correlating **mouth aperture over time** with the audio envelope. Two mouth-corner
points cannot measure aperture; a lip contour can. So a 5-point detector is a
dead end for F8 even though it is fine for F5's own demo.

## Candidate A — MediaPipe Face Landmarker (+ OpenCV for camera frames)

- `mediapipe` latest is **0.10.35**, wheel `mediapipe-0.10.35-py3-none-win_amd64.whl`
  uploaded **`2026-04-27T17:45:33.946332Z`** — PyPI JSON `upload_time`, read
  2026-07-26. ~3 months old → **inside the ~12-month bar**.
  Source: <https://pypi.org/pypi/mediapipe/0.10.35/json>
- Date cross-check: the GitHub release page for tag `v0.10.35` renders
  "**28 Apr 17:55**" with **no year** — GitHub omits the year only for the current
  year, so the tag is 2026-04-28, consistent with the PyPI upload. Recorded because
  a first read of the rendered releases list reported "April 28, 2025"; the
  year-less rendering is what caused it. Evidence read 2026-07-26.
  Source: <https://github.com/google-ai-edge/mediapipe/releases/tag/v0.10.35>
- Adoption: **2,515,402 downloads in the last month**; 65,139 on 2026-07-25.
  Source: <https://pypistats.org/api/packages/mediapipe/recent>, read 2026-07-26.
- License: **Apache 2.0** (PyPI `license` field, 0.10.35).
- Python support: classifiers list 3.9–3.12; wheels are `py3-none-<platform>`, so
  **3.11 is covered**. Repo runs 3.11.14 (`.python-version` = `3.11`).
- Declared dependencies (PyPI `requires_dist`, 0.10.35), verbatim:
  `absl-py~=2.3`, `certifi`, `numpy`, `sounddevice~=0.5`, `flatbuffers~=25.9`,
  `opencv-contrib-python`, `matplotlib`.
  - `numpy` is **unpinned** → compatible with the repo's `numpy>=2.0,<2.3`.
  - `sounddevice~=0.5` → the repo already declares `sounddevice>=0.5.5`. No conflict.
  - **`opencv-contrib-python` is a hard transitive** — see the OpenCV note below.
- Capability, from the official task docs (read 2026-07-26):
  - Outputs "**478 landmarks for each face**" as 3-D normalized coordinates —
    includes a full lip contour, which is what F8 needs.
  - Also outputs **52 blendshapes** when `output_face_blendshapes` is enabled,
    including **`jawOpen`** — a ready-made mouth-aperture signal for F8.
  - Running modes `IMAGE` / `VIDEO` / `LIVE_STREAM`; `LIVE_STREAM` delivers results
    through a **`result_callback`** — relevant to the earned guardrail about test
    doubles driving the real callback.
  - Model loaded from a local file via `BaseOptions(model_asset_path=...)` → the
    `.task` bundle can be **vendored offline**, the same shape as F3's ECAPA.
  - Bundle contains three models: BlazeFace short-range detector, the face-mesh
    model (478 landmarks), and the blendshape model. Canonical URL:
    `https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/latest/face_landmarker.task`
  - Sources: <https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker>
    and `.../face_landmarker/python`
- **`unconfirmed`:** the exact byte size and the license *of the `.task` bundle
  file itself* are not stated on the model page. Must be checked at download time,
  before vendoring.
- **`unconfirmed`:** MediaPipe provides **no face-recognition embedding** task.
  Its `ImageEmbedder` is a general image embedder, not a face-identity model. So
  candidate A needs a separate answer for F6/F7 — see the SFace note.

## The OpenCV sub-question (applies to every candidate)

Nothing in the candidate set opens a webcam; `cv2.VideoCapture` is the standard
path, so **OpenCV enters the manifest no matter which candidate wins**.

- `opencv-contrib-python` **5.0.0.93** released **2026-07-02**; newest 4.x is
  **4.13.0.92**, released **2026-02-05**. Both inside the bar.
  Source: <https://pypi.org/project/opencv-contrib-python/#history>, read 2026-07-26.
- Adoption: **8,487,096 downloads last month**.
  Source: <https://pypistats.org/api/packages/opencv-contrib-python/recent>
- `opencv-python` (the non-contrib build) tracks the same version numbers —
  5.0.0.93 on **2026-07-02**, 4.13.0.92 on **2026-02-05**.
  Source: <https://pypi.org/project/opencv-python/#history>
- **Which OpenCV package matters.** `opencv-python` and `opencv-contrib-python`
  both install a top-level `cv2` module; installing both is a known shadowing
  hazard. MediaPipe pulls `opencv-contrib-python`, so if MediaPipe is chosen the
  correct move is to declare **`opencv-contrib-python`** explicitly and never add
  `opencv-python` — one `cv2`, and the transitive is declared rather than
  inherited (the F4.5 `soundfile` lesson, applied before it bites).
- OpenCV ships a face detector and a face recognizer in-box: **`cv2.FaceDetectorYN`**
  (YuNet) and **`cv2.FaceRecognizerSF`** (SFace), both loading ONNX files from
  the `opencv/opencv_zoo` repo — so an embedding for F6/F7 costs **no new
  dependency** once OpenCV is present.
  Source: <https://docs.opencv.org/4.13.0/d0/dd4/tutorial_dnn_face.html>, read 2026-07-26.
- opencv_zoo is actively maintained: `face_detection_yunet_2026may.onnx` is a
  2026 re-export of the 2023 model with symbolic H/W dims for OpenCV 5.
  Source: <https://github.com/opencv/opencv_zoo/blob/main/models/face_detection_yunet/README.md>
- **YuNet outputs 5 landmarks only** (eye centres, nose tip, mouth corners) —
  the zoo README still says "5-landmark warping for now". Enough to draw a
  tracked face on the preview; **not** enough for F8's mouth aperture.
- SFace: MobileFaceNet trained with the SFace loss, Apache-2.0, model files in
  `opencv_zoo/models/face_recognition_sface/`.
  **`unconfirmed`:** exact file size and embedding dimensionality were not stated
  on the README page fetched; check at vendoring time (F6, not F5).

## Candidate B — OpenCV only (YuNet detect + SFace embed)

- Liveness: **PASS** — see the OpenCV note above (4.13.0.92 on 2026-02-05).
- One dependency covers camera + detect + embed. Smallest possible manifest delta.
- **Fails the F8 requirement**: 5 landmarks, no lip contour, no mouth aperture.
  Adopting it means a second face-stack TECH-PICK before F8, and a second model
  vendoring job — i.e. it defers cost rather than avoiding it.

## Candidate C — InsightFace (buffalo_l: SCRFD detect + 106-pt landmarks + ArcFace)

- `insightface` **1.0.1** released **2026-05-23T06:43:00Z**; the prior release was
  0.7.3 on **2023-04-02**. So it is live *today* but sat idle for ~3 years.
  Source: <https://pypi.org/pypi/insightface/json>, read 2026-07-26.
- Covers detect + 106-point landmarks (lips included) + a strong ArcFace
  embedding — technically the most complete single answer.
- **License blocker:** the project page states the pretrained models are
  "available for **non-commercial research purposes only**, including both
  auto-downloading models and manual-downloading models". The code is MIT; the
  weights are not. Every other model in this repo (ECAPA Apache-2.0) is
  permissive.
  Source: <https://pypi.org/project/insightface/>, read 2026-07-26.
- **Cost:** requires `onnxruntime` as a second new dependency ("Starting from
  insightface>=0.2, we use onnxruntime as inference backend"), plus OpenCV for
  the camera → three new manifest entries. Default `buffalo_l` pack is **326 MB**
  and auto-downloads to `~/.insightface/models/` — it would need the same
  offline-vendoring treatment as ECAPA, at 6× the size.

## Candidate D — facenet-pytorch (MTCNN + InceptionResnetV1) — **FAIL**

- Latest **2.6.0**, released **2024-04-29** → ~27 months old at 2026-07-26.
  **Fails the ~12-month liveness bar.**
  Source: <https://pypi.org/pypi/facenet-pytorch/json>, read 2026-07-26.
- Independently disqualifying: its pins are `torch<2.3.0,>=2.2.0` and
  `numpy<2.0.0,>=1.24.0`. The repo declares `torch>=2.13.0` and
  `numpy>=2.0,<2.3`. **Direct, unresolvable conflict** — it would force a
  downgrade of the stack F3 and F4 were measured against.
- Recorded because it was this model's first instinct (torch is already installed,
  so it *felt* free). The registry dates and the pins say otherwise. That delta is
  the reason the playbook is loaded before searching.

## Resolution evidence (does the pick actually install here?)

Run 2026-07-26 with `uv pip compile --python-version 3.11` against the repo's
current eight declared dependencies **plus** the candidates. This resolves only —
nothing was installed, and `git status --porcelain` was empty before and after.

    mediapipe==0.10.35
    opencv-contrib-python==5.0.0.93
    numpy==2.2.6
    torch==2.13.0
    torchaudio==2.11.0
    sounddevice==0.5.5
    absl-py==2.5.0
    flatbuffers==25.12.19
    matplotlib==3.11.1

A second run pinning `opencv-contrib-python>=4.13,<5` also resolves cleanly:

    mediapipe==0.10.35
    opencv-contrib-python==4.13.0.92
    numpy==2.2.6

So MediaPipe + OpenCV co-exist with the F3/F4 stack at **both** OpenCV major
versions, and `numpy` stays at 2.2.6 — inside the repo's `<2.3` ceiling, so F3's
`ACCEPT_CUTOFF` and F4's `CORRECTION_RADIUS` are not disturbed by the resolution.

**Recommendation on the OpenCV pin:** `>=4.13,<5`. OpenCV **5.0.0 is three weeks
old** (2026-07-02) and is a major-version bump; F5 needs nothing from it, and
4.13.0.92 (2026-02-05) is mature and well inside the bar. Taking 5.x here would
buy nothing and spend the risk budget on a library the demo only asks for
`VideoCapture` from.

## Comparison

| Candidate | Live? (quoted evidence) | Fits our stack because | Cost / risk |
|---|---|---|---|
| **A — MediaPipe + OpenCV** | mediapipe 0.10.35 uploaded `2026-04-27T17:45:33.946332Z`; 2,515,402 downloads/month · opencv-contrib-python 4.13.0.92 on 2026-02-05; 8,487,096 downloads/month | 478 landmarks incl. a **lip contour** and a `jawOpen` blendshape → F8's lip-sync is reachable; `.task` bundle loads from a local path (offline, ECAPA precedent); Apache-2.0 throughout; `LIVE_STREAM` `result_callback` matches the repo's callback-testing guardrail; OpenCV is needed for the camera anyway and brings SFace for F6 free | **2** new manifest entries; a second vendored model dir; MediaPipe has **no** face-identity embedding, so F6 leans on OpenCV's SFace (a second vendored model then); `.task` size/license unconfirmed until download |
| **B — OpenCV only** | opencv-contrib-python 4.13.0.92 on 2026-02-05; 8,487,096 downloads/month | smallest possible delta — **1** dependency covers camera + detect + embed | **5 landmarks only** — no mouth aperture, so **F8 is not reachable**; forces a second face TECH-PICK and a second model vendoring before F8 |
| **C — InsightFace** | 1.0.1 on 2026-05-23 (but the release before it was 0.7.3, 2023-04-02) | most complete single library: detect + 106 landmarks + strong ArcFace embedding | **models are non-commercial-research-only** (every other model here is Apache-2.0); needs `onnxruntime` **and** OpenCV → 3 new entries; 326 MB default pack to vendor; 3-year maintenance gap before the current release |
| **D — facenet-pytorch** | 2.6.0 on **2024-04-29** → ~27 months | — | **FAIL on liveness**, and pins `torch<2.3.0` / `numpy<2.0.0` against the repo's `torch>=2.13.0` / `numpy>=2.0` |

## Answer to the question that prompted this

Take **A**: `mediapipe` for face detection + landmarks, `opencv-contrib-python`
(pinned `>=4.13,<5`) for camera frames — declared explicitly rather than
inherited through MediaPipe. It is the only candidate that clears the liveness
bar, stays Apache-2.0, resolves against the existing torch/numpy pins without
moving them, and reaches **all the way to F8's lip-sync** rather than stopping at
F5's own demo. Its honest cost is two manifest entries instead of one, and a
second vendored model directory beside `models/ecapa/`.

The one thing this research does **not** settle, because no registry can:
whether a Python-side OpenCV camera loop and a pywebview window co-operate on
this machine, and how the frames reach the preview. That is an architecture
question for the spec, not a library-liveness question.

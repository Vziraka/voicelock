# Handoff — F5 Task 1 `DONE`; **Task 2 `BLOCKED` — human decision needed**

Session of 2026-07-26. Ran `/implement` for **F5 — Camera booth**: Task 1 built,
verified (subagent) and wrapped up `DONE`; Task 2 hit its **designed licence
STOP condition** and is `BLOCKED`. Tasks 3–7 `TODO`.

The plan predicted this exact stop: *"Tasks 2 and 3 each download an asset and
verify its licence at download… If either licence is not permissive, that task
goes `BLOCKED` and stops for the human — that is the designed behaviour, not a
failure of the plan."*

## THE DECISION WAITING FOR YOU

**The MediaPipe Face Landmarker bundle's licence is `unconfirmed`.** Not
"non-permissive" — *unstated by every primary source checked*. Per `spec.md` §4
and the research skill's "Gray zone = FAIL", it was **not committed**.

**Cheapest path to resolving it — about a minute, and it needs eyes not tools.**
Google's three model cards for the models inside this bundle are almost
certainly where the licence is written, but they are **image-only PDFs** with no
extractable text, and no OCR exists in this environment. They are already
downloaded:

```
%TEMP%\claude\c--Users-zvent-Downloads-Testing-V5\d4b97a37-f1bc-43b4-9528-abf29fe81c9c\scratchpad\
  facemeshv2.pdf  ·  blazeface.pdf  ·  blendshape.pdf
```

Open them, read the licence / terms section, and tell me what it says. Second
avenue if they are silent: the Kaggle model page
(`https://www.kaggle.com/models/mediapipe/face-landmarks-detection`) in a real
browser — it is JS-gated and unreadable to me, but Kaggle model pages normally
show an explicit licence field.

If it turns out permissive → I vendor the bundle with that evidence recorded and
continue. If it is genuinely restrictive, or you want a different approach
(e.g. fetching the model to `~/.voicelock/` at first run instead of committing
it), that is a **spec amendment** — human-only in every mode, needing a fresh
box-2 approval, because §4 mandates vendoring into the repo and §5 asserts the
file exists at `src/voicelock/models/face_landmarker/face_landmarker.task`.

## What was checked, and why "it's Google's, it's Apache-2.0" was not accepted

Full evidence with sources and dates:
`memory/research/2026-07-26-f5-face-landmarker-licence.md`. Summary:

| Source | Result |
|---|---|
| The `.task` artifact itself | **No licence text.** All four zip entries scanned for `Apache`/`licen`/`copyright` — zero hits. TFLite metadata has a `license` field; unpopulated. |
| The GCS bucket | **No `LICENSE`** — 404 at three probed paths. |
| Official Face Landmarker guide | States a licence only for **page content and code samples**, not the weights. |
| The three model cards | **Image-only PDFs** — unreadable without OCR. *The likeliest answer, unread.* |
| `mediapipe` 0.10.35 wheel | `License: Apache 2.0`, but ships **zero** model files; its LICENSE has no weights carve-out. |
| `google-ai-edge/mediapipe` repo | Apache-2.0, but `modules/face_landmark/` holds only `.pbtxt` graphs — **no `.tflite`**, and **0** `.task` files repo-wide. |
| Kaggle model page | JS-gated 5.6 KB shell; no licence field in raw HTML. |
| Web search | Only Apache-2.0 headers in **code samples** — the exact class `spec.md` §4 rules insufficient. |

`spec.md` §4 is explicit that *"it came from Google's MediaPipe project" is NOT
sufficient evidence*, and cites the precedent: MediaPipe's own face_detector
sample ships a **Pixabay**-licensed image, not an Apache-2.0 one. So the
framework being Apache-2.0 does not license the weights.

Worth flagging honestly: the TECH-PICK's working assumption was *"it is
Apache-2.0 throughout"*, and that is **not** established. The TECH-PICK did flag
the bundle's licence as `unconfirmed` under its accepted limits, which is why
this STOP condition existed at all.

## The artifact, quarantined not lost

Downloaded and verified as a real bundle, then moved **out of the repo tree** so
no `git add -A` could vendor it accidentally:

- 3 758 596 bytes — clears `spec.md` §5's `> 1_000_000` assertion
- SHA-256 `64184E229B263107BC2B804C6625DB1341FF2BB731874B0BCC2FE6544E0BC9FF`
- Contents: `face_detector.tflite`, `face_landmarks_detector.tflite`,
  `face_blendshapes.tflite`, `geometry_pipeline_metadata_landmarks.binarypb`
  — mapping 1:1 onto the three model cards
- Now at `…\scratchpad\face_landmarker.task`; re-fetching is one command

`git status` is clean. Nothing unlicensed is staged or committed.

## Task 1 — `DONE` (for the record)

- `pyproject.toml` + `uv.lock`: `mediapipe==0.10.35`,
  `opencv-contrib-python==4.13.0.92`. **Zero code.**
- Nothing moved underneath F4: `numpy 2.2.6`, `torch 2.13.0`, lock diff purely
  additive — so `CORRECTION_RADIUS = 110` and `ACCEPT_CUTOFF = 0.45` hold.
- Gate 5/5 exit 0 (`pytest` **88 passed in 59.14 s**); Review APPROVE both axes,
  first pass, `rejects: 0`. Verdict:
  `memory/verdicts/2026-07-26-F5-T1.json`. `learn`: no lesson met the bar.

## Also still open

1. **`project.md`'s Environment section is stale** — says *"Tool(s): Cursor
   only"*, *"Setup run: 2026-07-21"*, while recent sessions ran in Claude Code.
   Re-running `setup` refreshes it. Cosmetic now that the verifier path is
   settled (subagent, human-authorized this session — `memory/decisions.md`).
2. **Task 3 carries the second licence STOP point** (`portrait.jpg`), unrelated
   to this one and still ahead.
3. **No guardrail proposal is pending.**

## Carried forward, unchanged

- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback: `TARGET_FPS` 30 →
  20 → 15 **on measured evidence**, never by loosening the assertion.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit** — `read()` is the real
  path the fake must deliver through, `release()` the teardown it must trip on,
  with a **`BaseException`** subclass.

## next_action

**Human decision on the bundle licence** (see "THE DECISION WAITING FOR YOU").
Nothing in F5 proceeds past it except Task 3, which the plan deliberately split
out so a blocked model would not also block the fixture — Tasks 4–7 all need the
bundle. Say the word if you want Task 3 started while you settle Task 2.

## Commits

- Task 1: `878186c` (DOING) → `19b63e5` (build) → `79b022e` (bookkeeping) →
  `b21b8ae` (wrap-up, Task 1 `DONE`)
- Task 2: `be938c1` (DOING) → this escalation commit (state + research only; **no
  model bundle**)

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

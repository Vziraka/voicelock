# Handoff — F5 Task 2 built, now `REVIEW` (licence escalation resolved)

Session of 2026-07-26. Task 1 `DONE`; Task 2 hit its designed licence STOP
condition, was **escalated to the human and resolved**, and is now built and
`REVIEW`. Tasks 3–7 `TODO`.

## Changed

- **`src/voicelock/models/face_landmarker/face_landmarker.task`** — the vendored
  bundle. 3 758 596 bytes, SHA-256 `64184E22…4E0BC9FF`.
- **`src/voicelock/models/face_landmarker/LICENSE`** — Apache-2.0, 11 357 bytes.
- **`src/voicelock/models/face_landmarker/NOTICE`** — source URL, fetch date,
  size, hash, and the full licence evidence chain.
- **`.harness/plan.md`** — Task 2 `BLOCKED → DOING → REVIEW`; Active context and
  spine bullet 3 updated.
- Earlier in the session (already committed): `memory/decisions.md` (the
  resolution) and `memory/research/2026-07-26-f5-face-landmarker-licence-resolved.md`.

**Zero engine code.** No `facedetect.py` — that is Task 4.

## The escalation, and how it resolved

The task's STOP condition fired: **eight primary sources state no licence for the
model weights** — the `.task` embeds none (all four zip entries scanned, zero
hits; TFLite metadata `license` field unpopulated), the GCS bucket 404s on
`LICENSE` at three paths, the official guide licences only *page content and code
samples*, the Apache-2.0 `mediapipe` wheel ships **zero** model files, the
Apache-2.0 `google-ai-edge/mediapipe` repo ships only `.pbtxt` graphs and **zero**
`.task` bundles, Kaggle is JS-gated, and web results trace to Apache-2.0 headers
in *code samples* — the exact class `spec.md` §4 rules insufficient.

The bundle was **not** committed and the task went `BLOCKED`.

The answer was in the one place a machine could not read it: Google's three
**model cards**, which are image-only PDFs with no extractable text and no OCR
here. **The human opened them and reported the Apache-2.0 licence link.** That
was then corroborated mechanically rather than taken on trust — PDF link
annotations are plain objects even on flat-image pages, so extracting every
`/URI` showed `apache.org/licenses/LICENSE-2.0.html` in **all three** cards,
which map 1:1 onto the bundle's three `.tflite` models. Provenance is therefore
established **per asset**, the standard `spec.md` §4 sets.

Recorded in `memory/decisions.md` and the superseding research file **before**
the build resumed, per write-before-proceed.

## Disclosure — exactly which Gate commands I ran (measurement exception)

Two, and no others:

1. `uv run ruff check .` → exit 0 ("All checks passed!")
2. the bundle-loads check (`FaceLandmarkerOptions` … `RunningMode.VIDEO`) →
   exit 0, printed `bundle loads`

I did **not** run `uv run pytest`, the file-size assertion, or the LICENSE-file
assertion. All three remain for the Gate.

## Doubts, flagged rather than buried

1. **The licence rests on the model cards, not on the artifact.** The `.task`
   demonstrably embeds none. The `NOTICE` says so explicitly rather than
   implying the file is self-describing — I would rather a verifier judge that
   honestly-stated chain than find it papered over. What was *machine*-verified
   is the presence of the Apache-2.0 URL in all three cards; the sentence
   surrounding it was read by a human, not parsed.
2. **A second avenue is still unread** — the Kaggle model page's licence field,
   JS-gated. Not needed, but it is the belt-and-braces confirmation if anyone
   wants it.
3. **The vendored `LICENSE` is a copy of `models/ecapa/LICENSE`**, not of the
   `mediapipe` wheel's. Deliberate: the wheel's has Lucent/Plan 9 third-party
   notices appended covering the *wheel's code*, which would misdescribe the
   model. The ECAPA copy is pristine, unmodified Apache-2.0 (its appendix still
   reads `Copyright [yyyy] [name of copyright owner]`), so both vendored model
   dirs now carry identical, correct licence text.
4. **MediaPipe prints `W0000` warnings on load** (XNNPACK delegate, feedback
   manager). These are normal init logging on stderr, not errors — the command
   exits 0. Noting it because a verifier will see them and they look alarming.
5. **`git add -A` hazard, handled.** `.task` matches no `.gitignore` rule, so
   while the licence was unresolved the downloaded bundle was moved out of the
   repo tree entirely rather than left untracked. Nothing unlicensed was ever
   staged.
6. **Integrity check.** The committed bundle was re-fetched from the canonical
   URL and compared: byte-for-byte identical.

## Still open for the human

1. **Task 3 carries the second licence STOP point** (`portrait.jpg`) and it is
   **unrelated to this one** — do not read Task 2's resolution as precedent.
   `spec.md` §4's cited counter-example is that MediaPipe's own face_detector
   sample ships a **Pixabay**-licensed image, whose terms restrict
   redistributing unaltered copies. It may well not clear as easily.
2. **`project.md`'s Environment section is stale** — *"Tool(s): Cursor only"*,
   *"Setup run: 2026-07-21"*. Re-running `setup` refreshes it.
3. **No guardrail proposal is pending.**

## Carried forward, unchanged

- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback: `TARGET_FPS`
  30 → 20 → 15 **on measured evidence**, never by loosening the assertion.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit** — `read()` is the real
  path the fake must deliver through, `release()` the teardown it must trip on,
  with a **`BaseException`** subclass.

## next_action

**Verify Task 2** — clean-context verifier via `formats/VERIFIER-PROMPT.md`,
verbatim, spawned by this session (subagent path, human-authorized). Task 2's
done-criteria are its `plan.md` list, not the spec's full Verification section —
Task 2 is an intermediate task.

## Commits

- Task 1: `878186c` → `19b63e5` → `79b022e` → `b21b8ae` (`DONE`)
- Task 2: `be938c1` (DOING) → `e533720` (BLOCKED escalation) → `6585761`
  (DOING resumed + resolution recorded) → **`1ddf831` (build)**
- Base for the Gate diff: **`6585761`** · head: **`1ddf831`**
- Plus this bookkeeping commit, putting actual HEAD one ahead of the recorded
  head — expected, per the two-commit rule.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

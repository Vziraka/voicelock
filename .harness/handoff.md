# Handoff — F5 Tasks 1–5 `DONE`; Task 6 (Booth UI) is next

Session of 2026-07-26. Five of seven tasks closed. Tasks 1–4 landed APPROVE on
the first pass; **Task 5 took one REJECT** and is now `DONE` with `rejects: 1`.
Tasks 6–7 `TODO`.

**Two guardrail proposals are parked below** and need a yes/no. Neither blocks
Task 6.

## Where the feature stands

| Task | State | Note |
|---|---|---|
| 1 — declare deps | `DONE` | `numpy`/`torch` provably unmoved |
| 2 — vendor the bundle | `DONE` | Apache-2.0, hash-verified |
| 3 — face fixture | `DONE` | fetched-not-committed + committed vendor reference |
| 4 — per-frame composite | `DONE` | matches Google's published landmarks to 0.005645 |
| 5 — camera lifecycle | `DONE` | `rejects: 1`; ~8 ms/frame vs the 33 ms budget |
| 6 — Booth `<img>` | `TODO` | **next**, UI only |
| 7 — `BoothApi` wiring | `TODO` | LAST; full §5 + the human-attested demo |

Suite: **114 passed**. Verdicts: `memory/verdicts/2026-07-26-F5-T1…T5.json`.

## Task 5's REJECT, because the lesson matters for what's left

Two findings, both earned. The second is the interesting one: the
drop-don't-queue behaviour was tested only as a **pure function**, while the
loop-level assertion (`read_count >= len(received)`) was true **by
construction**. The verifier proved the gap by replacing
`wait(pacing_delay(...))` with a flat `wait(FRAME_INTERVAL)` — deleting the
behaviour outright — and watching all 23 tests still pass.

Fixed with two tests that discriminate in **opposite** directions (an overrun
must cost zero delay; an under-budget frame must actually be paced), then
verified by **mutation** rather than assertion: 3/3 caught by me, and the
verifier independently repeated and extended it to **4/4**, catching one I had
not claimed.

**`TARGET_FPS` stays at 30.** Measured 8.0–8.7 ms/frame across four runs against
the 33 ms budget. The fallback ladder was not needed and the assertion was not
loosened. This measures the **engine only** — the `evaluate_js` bridge half is
Task 7's live check, and remains the one genuinely unmeasured risk in F5.

## PENDING — two guardrail proposals, neither written

`project.md` has **not** been touched. Both need a human yes/no; declining is a
fine answer and I will record it as declined.

**A — from Task 5's scan (new).** Distinct from the existing "no unexercised
branch" rule: that one catches surface with *no* test, this catches surface with
a test whose assertion still holds if the behaviour is deleted.

> - **[Forbidden]** A test must assert something that would **break if the
>   behaviour were removed**. Before claiming a test covers behaviour X, delete
>   or neuter X and confirm the test fails; an assertion that holds by
>   construction of the code under test is not coverage. `warn` · expires:
>   2027-01-31
>   - _Evidence:_ F5 Task 5 (2026-07-26), REJECT #1. `drop-don't-queue` was
>     pinned only as a pure function while the loop-level test asserted
>     `read_count >= len(received)` — true by construction. Replacing
>     `wait(pacing_delay(...))` with a flat `wait(FRAME_INTERVAL)`, i.e. deleting
>     the behaviour entirely, still passed all 23 tests. Cost one full verify
>     cycle. The fix — two tests discriminating in opposite directions, then a
>     mutation run — caught 4/4 including one the implementor had not claimed.
>   - _Added:_ 2026-07-26
>
> _Enforcement considered and rejected with reason:_ a real mutation-testing
> tool (`mutmut`, `cosmic-ray`) is a new dependency needing a TECH-PICK and is
> disproportionate here, and no lint rule can detect a vacuous assertion. Prose
> is the honest fallback, with the cheap manual technique named in the rule.

**B — from Task 3's scan (still parked).** An **update** to the existing
`[Approval]` per-asset licence rule, not a new guardrail:

> Append: **check the asset's own embedded metadata first (EXIF/XMP for images,
> bundle metadata for models)** — the most authoritative statement available and
> the cheapest to read.
>
> _Evidence:_ eight external sources were consulted for the model bundle before
> the answer turned up in Google's model cards; for the image fixture the answer
> was **inside the file** — two lines of EXIF settled it immediately, where the
> bucket, the docs and the Apache-2.0 `BUILD` file all said nothing or the wrong
> thing.

## Carried forward into Task 6 (UI only)

`src/voicelock/ui/index.html` — the page's **only** job is to assign the pushed
data URI to an `<img>` inside `.face-wrap`, and swap back to the smiley SVG on
`setFaceIdle()`. Both go on `window.voicelockBooth`, beside `setLevel` /
`setRecording`.

- The preview replaces the decorative smiley **in place**, in its existing
  **172 px** circle, with **zero layout shift**.
- Masked to the circle, filling the disk with **no letterboxing** — Python
  already delivers a 172 px square, so the page does no cropping or scaling.
- **The page holds no camera state** (third earned guardrail): no frame counter,
  no "is the camera on" boolean. `setRecording()` already exists for recording
  state; do not add a parallel camera flag.
- **No `getUserMedia`** — `file://` has no secure context, which is why Python
  owns the camera. **No CSS `scaleX(-1)`** — the flip belongs in Python, after
  the overlay is drawn.
- **No restyling and no expanded preview** — F9 polish and a deferred change
  respectively.
- Honest limit: this repo's Gate is **pytest with zero JS tests**, so Task 6's
  criteria pin *presence and export*; the real proof is Task 7's live check.
  Task 6 comes first so the page function exists before anything calls it.

## Carried forward into Task 7 (LAST)

- `start_record` starts the camera, `stop_record` stops it; the engine's
  `on_frame` pushes each data URI via the existing `_eval` path.
- **A camera failure must NOT prevent audio recording** — the mic path survives
  a broken webcam. Real branch, needs a test.
- **`main()` has no close handler today** (`app.py:399-412`); Task 7 adds one
  pointing at `stop()`. That is why `stop()` being safe to call twice is a real
  requirement, not a theoretical one.
- `ready()` untouched — **no startup camera probe**. `capture.py` untouched.
- **From Task 5's verifiers, two things Task 7 owns:** if `stop()`'s join times
  out, `release()` runs anyway while the worker may still be mid-read (a 5 s
  window that only opens if a frame hangs); and a camera that dies mid-loop
  leaves the device held until something calls `stop()`.
- **Expect `ESCALATE_HUMAN`** on the manual demo line. Do **not** mark Task 7
  `DONE` until the human attests the live check.

## Also open

- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*,
  *"Setup run: 2026-07-21"*). Re-running `setup` refreshes it. Cosmetic.

## next_action

**`/implement` F5 Task 6 — the Booth `<img>` preview in the existing 172 px face
disk.** `Mode: Mode 3` is the standing "go" and Task 5's wrap-up completed. The
next required human touchpoint is Task 7's manual camera demo.

## Commits

- Tasks 1–4: `878186c`…`fab7a30`
- Task 5: `80a95ca` → `0eeac3f` → `571cfb8` (REJECT) → `f069fa0` → `11d5a1d` →
  `a0f44a0` → this wrap-up commit
- Task 5's re-verify diff was `f069fa0..11d5a1d`

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

# Handoff — F5 Tasks 1–6 `DONE`; only Task 7 remains

Session of 2026-07-26. Six of seven tasks closed — five APPROVE on the first
pass, Task 5 with `rejects: 1`. Task 6 is now `DONE` too (Gate 4/4, Review
APPROVE both axes, verdict `memory/verdicts/2026-07-26-F5-T6.json`).

**Task 7 is the last one, and it ends with a human touchpoint** — its
done-criterion is the FULL `spec.md` Verification list including the manual
camera demo, which no automated check can stand in for.

## Changed

- **`src/voicelock/ui/index.html`** — the only file. `.face-frame` CSS, an
  `<img id="face-frame">` inside the existing `.face-wrap`, an id on the smiley
  SVG so it can be hidden and restored in place, `setFaceFrame` / `setFaceIdle`
  defined and exported on `window.voicelockBooth`, plus both elements in `els`.
- **`.harness/plan.md`** — Task 6 `TODO → DOING → REVIEW`.

**No Python touched.** Suite: **114 passed** (unchanged — a UI edit regresses no
Python test, which is the point of that criterion).

## What it does

The preview replaces the decorative smiley **in place**, in its existing 172 px
circle, with **zero layout shift**. The `<img>` is masked with
`border-radius: 50%` and `object-fit: cover`, hidden by default and shown via an
`is-live` class.

Python already delivers a 172 px square with the overlay drawn **and already
mirrored**, so the page does **no cropping, no scaling maths and no CSS flip**.

**The page holds no camera state** — the third earned guardrail. No frame
counter, no "is the camera on" boolean, no flag parallel to `setRecording`. It
renders what Python pushes and nothing else.

## One thing worth a verifier's attention

The pinned criterion guarding this is a **substring match for `getUserMedia`
over the whole file**, so an explanatory **comment** naming the API tripped it.

I reworded the comment rather than loosening the criterion. A pinned Gate
command is not something to bend to fit prose — and the check is doing its job,
just bluntly. Worth knowing because the comment still explains *why* Python owns
the camera (a `file://` document gets no secure context, so the browser's
media-capture API is absent), it simply no longer spells the API name.

## Disclosure — exactly which Gate commands I ran (measurement exception)

Both of Task 6's pinned `python -c` criteria (presence + export; the two
architecture guards), `uv run ruff check .` → 0, and `uv run pytest` →
114 passed. The first architecture-guard run **failed** as described above; the
comment was reworded and it now exits 0.

## Doubts, flagged rather than buried

1. **`setFaceIdle()` removes the `src` attribute** rather than leaving the last
   frame in place. Deliberate — a stale final frame sitting under a hidden
   element is exactly the kind of thing that reappears later — but it means a
   Record→Stop→Record cycle shows the disk's background for the instant before
   the first new frame arrives, rather than the previous take's last frame.
2. **The smiley is toggled with `style.display`** while the `<img>` uses a CSS
   class. Two mechanisms for one swap; I chose not to restyle the existing SVG
   (Task 6's notes forbid restyling), so the inline style is the least invasive
   way to hide an element that had no class hook.
3. **Nothing calls these functions yet.** That is the intended order — the page
   function exists before the bridge wires it (Task 7), so nothing is ever
   calling into a hole. `_eval`'s existing `window.voicelockBooth && …` guard
   would have made the reverse order a silent no-op.
4. **`face-frame` has `alt=""`** and sits inside a container already marked
   `aria-hidden="true"`, consistent with the decorative smiley it replaces. It
   is a preview, not content.
5. **Zero JS tests, as expected.** These criteria pin presence and export only.
   The real proof is Task 7's human-attested live check — stated in the plan,
   not discovered here.

## Carried forward into Task 7 — the LAST task

- `start_record` starts the camera, `stop_record` stops it; the engine's
  `on_frame` pushes each data URI through the existing `_eval` path, the same
  shape `_pump_loop` uses for `setLevel`.
- **A camera failure must NOT prevent audio recording.** `start_record` still
  starts capture, still starts the level pump, still returns `ok`. Real branch,
  needs a test.
- **`main()` has no close handler today** (`app.py:399-412`); Task 7 adds one
  pointing at `stop()`. That is what makes `stop()` being safe to call twice a
  real requirement.
- `ready()` untouched — **no startup camera probe**. `capture.py` untouched.
  Nothing written to disk; `~/.voicelock/` gains no file.
- **From Task 5's verifiers:** if `stop()`'s join times out, `release()` runs
  anyway while the worker may still be mid-read (a 5 s window, only if a frame
  hangs); and a camera that dies mid-loop stays held until something calls
  `stop()`.
- **Task 7's done-criterion is the FULL `spec.md` Verification list**, and it
  will return **`ESCALATE_HUMAN`** on the manual demo line. Do **not** mark it
  `DONE` until the human attests the live check. The completion report pins the
  measured throughput number from that final Gate run.

## Still parked — two guardrail proposals, neither written

Both need a human yes/no; neither blocks Task 7. Full text is in the previous
handoff and in the Task 3 / Task 5 verdict files.

- **A (new, from Task 5):** a test must assert something that would break if the
  behaviour were removed — mutation-check before claiming coverage.
- **B (from Task 3):** an update to the existing `[Approval]` licence rule —
  check the asset's own embedded EXIF/XMP metadata first.

Also open: `project.md`'s Environment section is stale (*"Tool(s): Cursor
only"*).

## next_action

**`/implement` F5 Task 7 — wire `BoothApi` to Record/Stop and release the camera
on window close.** `Mode: Mode 3` is the standing "go" and Task 6's wrap-up
completed. **This is the feature's last task**: expect the Gate to return
`ESCALATE_HUMAN` on the manual demo line, and do not mark it `DONE` or write its
verdict until the human attests the live check.

## Commits

- Tasks 1–5: `878186c`…`a5e525f`
- Task 6: `a0961b4` (DOING) → **`5846a81` (build)**
- Base for the Gate diff: **`a0961b4`** · head: **`5846a81`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

# F6 — Faceprint on screen · COMPLETION REPORT

**Feature complete 2026-07-27 (Mode 3 — Spec-to-done).** All 5 tasks
`DONE`, final Gate PASS, final Review APPROVE. This is the **Mode 3
feature-end checkpoint** — report + commit/push approval, per
`constitution/universal.md`'s Modes table. Nothing has been committed for
this wrap-up yet; everything below is staged and waiting on you.

## Outcome vs. spec.md §1

All three required things are true:

1. **`faceprint.py` exists and computes a real embedding** — SFace via
   `opencv-contrib-python`'s `cv2.FaceRecognizerSF`, ONNX weights vendored
   at `src/voicelock/models/sface/` beside `models/ecapa/` and
   `models/face_landmarker/`, loaded from a local path, no runtime
   network (verified offline-load test, §5 cmd 2).
2. **A stored face reference can be set, compared against, and reset**,
   shown in a three-band meter mirroring F3's vocabulary exactly. Cutoffs
   are OpenCV's published SFace operating point (`ACCEPT_CUTOFF ==
   REJECT_CUTOFF == 1.128` L2 — the vendor's one number expressed as two
   metrics is one boundary, not two independent bars; Q5 explicitly forbid
   deriving a second, repo-measured number from just two comparisons). The
   module docstring and `memory/decisions.md` state this reasoning, not
   just the numbers.
3. **Same face reads close, different face reads far**, proven two ways:
   real measurement on the committed fixtures (0.727 same-person vs.
   1.315/1.345 different-person, against the 1.128 cutoff) AND a
   mutation-sensitivity test proving a dummy mean-pixel embedder canNOT
   reproduce that separation — the assertion has teeth, unlike the failure
   F5.5 fixed in the voice path.

Demo works as specified: point the camera at your own face with a
reference set → meter reads accept; hold up a different face → meter reads
reject. **Attested live by the human this session** (see below) — the only
live-camera evidence for the same-face half, since the committed fixtures
are two static photographs.

Non-goals honored: no lock wiring (`vault.py` untouched), no liveness
claim (the panel visibly discloses "match, not liveness"), no voice
constant re-pinned, `facedetect.py`'s camera lifecycle/preview pipeline
unchanged except the one additive `last_frame` field, `portrait.jpg`
untouched and still `.gitignore`d.

## Final Gate evidence (command → exit code), Task 5's full run

| Command | Result |
|---|---|
| `uv run ruff check .` | exit 0 |
| `uv run pytest` (full suite) | exit 0 — **145 passed**, 0 failed (up from 124 at F5.5) |
| §5 cmd 1 — SFace model + licence present | exit 0 |
| §5 cmd 2 — offline load (`pytest -k offline`) | exit 0 |
| §5 cmd 3 — same/different face separation | exit 0 (0.727 / 1.315 / 1.345 vs. 1.128) |
| §5 cmd 4 — convert-not-refuse (amended resize) | exit 0 |
| §5 cmd 5 — justification mentions `voiceprint` | exit 0 |
| §5 cmd 6 — mutation-sensitivity (`pytest -k mutation`) | exit 0 |
| §5 cmd 7 — liveness-honesty copy present | exit 0 |
| §5 cmd 8 — **manual, human-attested** | **ATTESTED** — see below |

## The manual check (§5 cmd 8 / Q9)

Human ran `uv run voicelock`, hit a real layout bug immediately (the
Booth's top was clipped — a regression from adding the faceprint panel,
fixed same-session, commit `e4c17bd`), relaunched, then confirmed in
chat, in direct reply to an explicit three-part question: **"yup did all
three"** — layout fixed, own face read accept with a reference set,
different face read reject. Judged sufficient by the clean-context
verifier against this repo's own precedent
(`memory/verdicts/2026-07-23-F3-T5.json`,
`memory/verdicts/2026-07-26-F5-T7.json` — identical attestation shape).

## Retry counts per task

| Task | Rejects | Note |
|---|---|---|
| 1 — vendor SFace + licence | 0 | |
| 2 — commit fixtures + README | 0 | |
| 3 — `faceprint.py` | 1 | unexercised `embed_file` error branch; fixed, re-verified APPROVE |
| 4 — Booth bridge | 0 | |
| 5 — Booth UI | 0 | layout bug caught by the human's own manual check, fixed pre-verification — not a formal Gate/Reviewer reject |

## Escalations that resolved themselves

**Task 3 was `BLOCKED`, then unblocked by a human-approved spec
amendment.** `spec.md`'s original §5 cmd 4 resized a portrait fixture
non-uniformly into a landscape frame — undetectable by ANY honest
implementation (confirmed by running the identical distorted array
through F5's own already-shipped, unmodified face detector: also 0
faces). Per Mode 3's rule on a verification command that cannot be
followed literally, the task stopped and reported rather than
reinterpreting unsupervised. You approved the recommended fix
(aspect-preserving resize) with "yes"; it was verified passing BEFORE
being written into `spec.md`, recorded in `memory/decisions.md`, and the
task proceeded to a clean APPROVE. Full detail: that entry, and
`memory/verdicts/2026-07-27-F6-T3.json`.

No `memory/deviations.md` entries were made during this feature — every
judgment call either had a clear, unambiguous fix (Task 4's plan.md
SyntaxError) or went through the BLOCKED/human-approval path above, never
the Modes-1–2 self-resolution path that requires a deviations.md entry.

## THREE pending guardrail proposals — need your decision

None have been written to `project.md` yet. Each is independent — approve,
decline, or amend any subset.

**#1 — VIDEO-mode landmarker tracker-state hazard** (from Task 2):
> **[Forbidden]** A `VIDEO`-mode `FaceLandmarker` instance must not be
> reused across unrelated still images — only across genuine sequential
> video frames. It carries face-tracker state across `detect_for_video`
> calls, so feeding it unrelated stills back-to-back silently drops the
> face (0 detections, no error) on any frame after the first. Use a fresh
> instance per unrelated image, or `IMAGE` mode outright. `warn` ·
> expires: 2027-01-31 · evidence: commit `4c8f880`,
> `tests/fixtures/face/README.md`'s "Detection re-verified" section.

**#2 — dry-run verification commands before pinning** (from Tasks 3+4,
two occurrences):
> **[Done]** A Verification command that exercises a real vendored model,
> or any command with concrete literal parameters, must be dry-run BEFORE
> being pinned into `spec.md`/`plan.md`. `warn` · expires: 2027-01-31 ·
> evidence: (1) Task 3's `spec.md` cmd 4 resize was undetectable by design
> (see above); (2) Task 4's `plan.md` done-criteria one-liner was a raw
> Python `SyntaxError` that had never been run.

**#3 — NEW, from Task 5's `learn` scan — CSS/layout regressions have zero
Gate coverage:**
> **[Forbidden]** Adding visible content to the Booth's `main`/`.booth`
> column (a new panel, section, or meaningfully taller block) must be
> visually smoke-tested in the running app — this repo's Gate (`ruff` +
> `pytest`) cannot detect CSS/layout regressions at all, and `.window`'s
> fixed height + `overflow: hidden` combined with flexbox centering
> silently clips overflowing content past BOTH edges with no error, test
> failure, or console warning. `warn` · expires: 2027-01-31
> - _Evidence:_ F6 Task 5 (2026-07-27). Adding the faceprint panel pushed
>   `.booth` past `.window`'s height budget. Every automated check passed
>   — ruff, the full suite, all 7 automatable spec commands, even a
>   manual `node --check` JS-syntax pass added specifically because this
>   feature had already had two unrun-before-pinning close calls (see
>   guardrail #2). NOTHING caught it. Only the human's own manual smoke
>   test — run for the unrelated reason of the required live camera check
>   — surfaced it, by seeing the top of the window cut off. Root cause:
>   `justify-content: center` on an overflowing flex container clips past
>   both edges and `overflow-y: auto` alone cannot reach the clipped
>   region — a real, citable CSS/flexbox gotcha, not a one-off typo.
>   Enforcement considered and rejected for now: real coverage would need
>   browser-based visual-regression tooling (e.g. a headless-browser
>   screenshot diff), which is a new dependency/tool this repo doesn't
>   have — that decision belongs to a TECH-PICK, not a `learn` guardrail
>   written unattended. Prose + mandatory manual smoke-testing is the
>   fallback until/unless that tooling is adopted.
> - _Added:_ 2026-07-27 (proposed — pending human approval)

Curate check: **37 verdicts** (`memory/verdicts/*.json`, counted after
this feature's 5) minus 29 (`project.md`'s "Last curated" stamp) = **8
tasks since the last curate** — still below the 10-due threshold, so no
reminder is printed, but it is close; the next feature will likely trip
it.

## Proposed commit (staged, NOT yet committed — waiting on you)

Everything below is `git add`ed but not committed: the Task 5 verdict
file, `roadmap.md` (F6 checked off, summary written), `memory/codebase-map.md`
(refreshed for F6's additions), `plan.md` (Active context + spine +
Task 5 → `DONE`), and this `handoff.md`.

Proposed message:
```
F6 complete: faceprint diagnostic on screen

5 tasks, 1 retry (Task 3, unexercised branch), 1 mid-feature spec
amendment (Sec5 cmd4's resize was undetectable by design, fixed with
human approval before being re-pinned), 1 layout bug caught by the
human's manual smoke test and fixed pre-verification. Full spec.md
Verification list PASS on the final task, manual camera check
attested by the human. Faceprint, Booth bridge, and Booth UI panel
are all solid; roadmap.md and codebase-map.md updated accordingly.

Three guardrail proposals from this feature's learn scans remain
pending separate human approval (not written to project.md).

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
```

**Waiting on you for:**
1. The three guardrail proposals above (yes/no/amend each).
2. Approval to commit the staged state files with the message above.
3. Whether to push — `origin` exists (private) but no push has happened
   this feature; say the word if you want one.

## next_action

Once you respond: write any approved guardrails into `project.md` (human
sign-off required before that file changes, per the guardrail write
rule), commit the state files, push only if asked, and F6 is closed.
There is no unattended next step from here — this is a human touchpoint
by design (Mode 3's feature-end checkpoint).

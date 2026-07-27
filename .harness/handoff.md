# F6 — Faceprint on screen · CLOSED

**Feature complete 2026-07-27 (Mode 3 — Spec-to-done).** All 5 tasks
`DONE`, final Gate PASS, final Review APPROVE. The Mode 3 feature-end
checkpoint is **resolved**: the human approved the commit (`be2be85`), all
three guardrail proposals ("guardrails yes"), and a push. All three
guardrails are now written into `constitution/project.md`'s Earned
guardrails section. Push completed this session — see Commits below for
the hash.

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

## Three guardrail proposals — APPROVED, all written to project.md

Human approved all three as-proposed ("guardrails yes"). Written verbatim
into `constitution/project.md`'s Earned guardrails section, each with
`_Added:_ 2026-07-27 (human-approved; proposed by F6 Task N's learn scan)`:

1. **VIDEO-mode landmarker tracker-state hazard** (from Task 2) — a
   `VIDEO`-mode `FaceLandmarker` must not be reused across unrelated still
   images.
2. **Dry-run verification commands before pinning** (from Tasks 3+4) — a
   command exercising a real model, or with concrete literal parameters,
   must be run once before being pinned into `spec.md`/`plan.md`.
3. **CSS/layout regressions have zero Gate coverage** (from Task 5) —
   visible Booth content changes need a manual smoke test; this repo's
   Gate cannot detect them.

Curate check: **37 verdicts** (`memory/verdicts/*.json`) minus 29
(`project.md`'s "Last curated" stamp) = **8 tasks since the last curate**
— still below the 10-due threshold, but close; the next feature will
likely trip it.

## Commits — feature closed, pushed

- `be2be85` — F6 completion state (verdict, roadmap, codebase-map, plan,
  handoff).
- (this write) — the three guardrails added to `constitution/project.md`.
- Pushed to `origin` (private) on the human's explicit "go ahead and
  push", this session.

## next_action

**None — F6 is closed.** The next roadmap feature is **F7 — Face as the
inner lock**, blocked-by F4 and F6 (both now satisfied). Starting it
needs a fresh `/spec` session; nothing here triggers it automatically —
Mode 3's standing "go" scoped to F6 and does not reach past the feature,
per `constitution/universal.md`'s [Approval] rule.

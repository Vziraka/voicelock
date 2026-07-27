# Project Constitution — VoiceLock

Per-repo rules. This file **learns**: conventions go in once (from intake);
guardrails accrue over time (from failures). Keep it curated — see the `curate`
skill. Specific lessons live here, never in `universal.md`.

## Environment (written by the setup skill — revise via setup, not hand-drift)
- Tool(s): **Claude Code and Cursor** — either may run this repo · Model(s):
  Claude Opus 5 (1M context) in Claude Code; Cursor Grok 4.5 in Cursor.
  Cursor built F1–F5; Claude Code ran F5's build session and the 2026-07-26
  curate. Recorded as both because a handover in either direction is expected.
- Verifier path: subagent — **proven, not assumed**: six clean-context subagent
  verifiers ran during calibration run 2 (2026-07-26). Applies to Claude Code.
  A Cursor session without subagents falls back to the fresh-session path per
  the universal BUILD gate; it must not self-verify.
- Signposts: **AGENTS.md + CLAUDE.md**, both at the repo root, identical and
  verbatim from `adapters/AGENTS-template.md`. The previous "AGENTS.md only"
  risk line predicted its own failure and it came true — the 2026-07-26 Claude
  Code session had to be pointed at `AGENTS.md` by hand. Closed 2026-07-26.
- Claude Code adapter: **installed** 2026-07-26 — `.claude/skills/<name>` is a
  directory **junction** per skill pointing at `.harness/skills/<name>`, so
  `/spec`, `/implement`, `/verify-gate` etc. are real commands and there is
  exactly ONE copy to maintain (no stale-copy drift, the failure mode
  `adapters/claude-code/README.md` warns about). The junctions are machine-local
  and `.gitignore`d, so **a fresh clone must re-run the install** — that README
  has the steps.
- Remote: **`origin` → https://github.com/Vziraka/voicelock (PRIVATE)** — wired
  2026-07-26, full history pushed (191 commits, `.harness/` included by
  deliberate choice). Verified private: `isPrivate: true` and an anonymous API
  request returns 404. Existing checkpoint rules govern pushes from here on.
- Sensitive data: none declared — re-verified 2026-07-26 against all 190
  commits before the first push: no `.env`/`.pem`/`.key`/vault file in any
  commit, no key or password patterns, and the licence-restricted
  `tests/fixtures/face/portrait.jpg` confirmed absent from all history. The
  vault itself lives outside the repo at `~/.voicelock/`. Note the commit
  author email is in all history and would be public if this repo were ever
  made public.
- First-time user: **no** (revised 2026-07-26) — five features completed, the
  last three at Mode 3 with clean verdicts, and Mode 4 is mechanically
  unlocked. Skills need not point at `GUIDE.md` or nudge Mode 1 by default.
- Setup run: 2026-07-21 · **re-run 2026-07-26** (full seven questions). Q1, Q4
  and Q7 revised by the human; Q2 re-recorded; Q3, Q5 and Q6 re-confirmed
  against evidence rather than memory.

## Conventions
Extracted by `intake-recon` (existing repo) or declared by `intake-scaffold` (new
repo). The non-negotiables go here; the full detail lives in
`constitution/topics/conventions.md`.

- Naming: snake_case files/functions/variables, PascalCase classes,
  `tests/test_<module>.py`; prefer CONTEXT.md terms in identifiers.
- Structure: code in `src/voicelock/`, UI in `src/voicelock/ui/`, tests in
  `tests/`, design mock reference in `design/` (not final UI).
- Stack rules: Python 3.11 + uv only (no bare pip); JS UI for looks, Python for
  brain; UI shell TECH-PICK at F1; **offline-only — no network at runtime**;
  no new dependencies without human approval.
- Division of labor: Python owns audio/DSP/crypto/state; JS owns rendering only.
- Gate commands: `uv run ruff check .` and `uv run pytest`, both exit 0
  (promises until F1 wires them).

## Earned guardrails
Last curated: 2026-07-26 (second pass) · verdicts then: 29

Each entry = one failure turned into a rule. Keep them few and current — the
`curate` skill dedups and retires expired ones.

Format:
- **[Category]** Rule in one line. `severity` · expires: {YYYY-MM-DD}
  - _Evidence:_ the failure this came from (so it can be reviewed and retired).
  - _Added:_ {YYYY-MM-DD}

- **[Approval]** A vendored third-party asset's licence must be established from a source that names **that asset** — the artifact itself, its distribution page, or its model card. A permissive licence on the framework, the wheel, or the source repo does **not** license separately-hosted weights or data files. **Check the asset's own embedded metadata FIRST — EXIF/XMP for images, bundle metadata for models** — it is the most authoritative statement available and the cheapest to read. `block` · expires: 2027-01-31
  - _Evidence:_ F5 Task 2 (2026-07-26). Eight primary sources said nothing about `face_landmarker.task`'s licence: the artifact embeds none (all four zip entries scanned for `apache`/`licen`/`copyright`, zero hits; the TFLite metadata `license` field unpopulated), the GCS bucket 404s on `LICENSE` at three paths, the official guide licenses only "the content of this page" and "code samples", the **Apache-2.0 `mediapipe` wheel ships zero model files**, and the **Apache-2.0 `google-ai-edge/mediapipe` repo ships only `.pbtxt` graphs and zero `.task` bundles**. The answer was in Google's three model cards, which map 1:1 onto the bundle's three `.tflite` models — provenance established per asset. Had "MediaPipe is Apache-2.0" been accepted, the repo would have vendored a 3.7 MB binary on reasoning `spec.md` §4 explicitly rules insufficient, and that spec's own counter-example shows the reasoning fails outright: MediaPipe's face_detector sample ships a **Pixabay**-licensed image, whose terms restrict redistributing unaltered copies — and committing a fixture *is* redistributing it unaltered. Note the rule is about the **source naming the asset**, not about distrusting vendors: the licence here turned out to be exactly what the TECH-PICK assumed; the point is that it was assumed rather than established, and the next asset may differ. Enforced in part by the spec's standing Verification check that every `src/voicelock/models/*/` dir carries a non-stub `LICENSE` and `NOTICE`; the sufficiency of the evidence still needs judgment, which is why this rule is prose. **The metadata-first clause comes from F5 Task 3, the converse case:** `portrait.jpg`'s own EXIF settled the question in a single read (`Artist = Pete Souza`, plus a White House notice forbidding reproduction), after the surrounding Apache-2.0 project had suggested the opposite. Cheapest source, most authoritative, and it was read last.
  - _Added:_ 2026-07-26 (human-approved; proposed by F5 Task 2's `learn` scan) · _Updated:_ 2026-07-26 by `curate` — metadata-first clause absorbed from F5 Task 3's parked proposal B (human-approved)

- **[Forbidden]** Never add a helper, method, or branch that no caller and no test exercises — delete it and let the task that genuinely needs it introduce it. `warn` · expires: 2027-01-31
  - _Evidence:_ three REJECTs in F4 (2026-07-26), all the same defect: `BoothApi.reset_enroll_takes()` added in Task 3 with zero callers and zero tests; `lock_voiceprint()`'s `hop == 0` branch in Task 4, reachable only for a take of exactly 19 200 samples and driven by no test; and an enroll "BRIDGE MISSING" branch in Task 5 that the same diff made unreachable. Each cost a full verify cycle. Note the rule is "introduce at the point of use", not "never add helpers" — the same `reset_enroll_takes()` was correctly restored in Task 5 once the UI called it in three places and two tests covered it.
  - _Added:_ 2026-07-26 (human-approved)

- **[Forbidden]** A test double for a stream or device must deliver data through the **real callback it was handed** — a fake that only exposes a polling method leaves the callback path at zero coverage. `warn` · expires: 2027-01-31
  - _Evidence:_ F1's `FakeStream` never invoked the callback it was constructed with (the word `callback` did not appear in `tests/test_capture.py`), so `_on_audio` shipped with **zero** coverage and a self-deadlock — `_close_stream()` → `stream.stop()` from inside the callback, where `Pa_StopStream` blocks until the callback returns. It survived F2, F3 and F4 undetected and cost a whole inserted feature (F4.5) to close. F5 adds a camera stream with its own frame callback and was going to copy the same fake-stream pattern — which is the stated reason F4.5 was inserted before F5 at all. **F5 did repeat the tripwire per-module, and adapted it honestly** (`spec.md` §5): `cv2.VideoCapture` exposes no callback, so the check asserts `read` and `release` appear in `tests/test_facedetect.py` — for a polling device, `read()` **is** the real path a fake must deliver through and `release()` is the teardown it must trip on. So the per-module tripwire is the standing mechanism: every spec that adds a device or stream module pins its own. **The shared-base-class question is now answerable and the answer is no** — the camera fake exists, and push-callback and poll-read fakes share a purpose, not a shape; extracting a common base would fit neither.
  - _Added:_ 2026-07-26 (human-approved; proposed by F4.5 Task 3's `learn` scan) · _Updated:_ 2026-07-26 by `curate` — two references had drifted (F5's camera fake now exists; the per-module tripwire was written, not merely recommended)

- **[Forbidden]** The UI must not keep its own copy of state the engine owns — render the engine's value instead of a local mirror. `warn` · expires: 2027-01-31
  - _Evidence:_ F4 Task 5 (2026-07-26) — `resetEnrollVoiceStep()` zeroed a JS take-counter while the bridge kept its banked takes, so the panel showed `0 / 5` over a non-empty engine and the next enrollment would have sealed abandoned takes — possibly a different person's — into the vault. Caught as a CORRECTNESS reject by the Task 5 verifier. Relevant beyond that bug: F5–F8 add FaceView, liveness and more UI state to a project whose stated convention is already "Python owns state; JS renders only".
  - _Added:_ 2026-07-26 (human-approved; proposed by F4 Task 5's `learn` scan and carried unapproved across two handoffs)

- **[Forbidden]** When an operation acquires a device or resource, **every path that ends the operation must release it** — including the paths that end it without user action (timeouts, soft caps, error exits), not just the explicit Stop that tests and manual checks naturally drive. `warn` · expires: 2027-01-31
  - _Evidence:_ the same code path caused a defect in **two consecutive features**. F4.5 exists because F1's 30-second soft cap called `stream.stop()` from inside the PortAudio callback and self-deadlocked; F5 Task 7 was REJECTed because that same cap ended a take without ever releasing the camera — press Record and walk away, and the webcam light stays on indefinitely. Both are the auto-stop path, and both survived because the tests and the manual demo drive the *explicit* Stop. Writing the F5 test then exposed a second bug of the same family: the pump was started before the camera, so an open-failure left a pump running against no device. Note the rule names the trigger (an acquisition) rather than a specific resource — F6 adds a second vendored model and F7/F8 add more device-holding flows.
  - _Added:_ 2026-07-26 (human-approved; proposed by F5 Task 7's `learn` scan, adopted at `curate`)

- **[Forbidden]** A test must assert something that would **break if the behaviour were removed**. Before claiming a test covers behaviour X, delete or neuter X and confirm the test fails. `warn` · expires: 2027-01-31
  - _Evidence:_ F5 Task 5 (2026-07-26). Drop-don't-queue was pinned only as a pure function, so the loop-level assertion was true by construction rather than by the code under test. The verifier proved the gap by mutation — replacing `wait(pacing_delay(...))` with a flat `wait(FRAME_INTERVAL)`, deleting the behaviour outright — and watching all 23 tests still pass. Distinct from the two rules above, and the distinction is the remedy: "no unexercised branch" catches surface with **no** test and is fixed by deleting code; the fake-stream rule catches a **harness** that never drives the real path and is fixed by a per-module tripwire; this one catches a test that **exists and passes vacuously**, and is fixed by strengthening the assertion. Ranked weakest of the three F5 proposals when adopted — one occurrence, and close to a general engineering principle — but adopted because the verifiers were already performing the mutation check on their own initiative, and this makes it their mandate.
  - _Added:_ 2026-07-26 (human-approved; proposed by F5 Task 5's `learn` scan, adopted at `curate`)

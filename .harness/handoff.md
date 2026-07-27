# F6 — Faceprint on screen · IMPLEMENT SESSION (Task 1)

**Session date: 2026-07-27.** Fresh `/implement` session per Mode 3's standing
"go" — the previous session (F6 plan) left Task 1 `TODO`; this session built it.

## What happened this session

- Entry gate re-verified: Grilling `Status: CLEAR`, both approval boxes
  checked, `Mode: Mode 3` set. Scanned `plan.md` for a `DONE` task with no
  matching verdict file — none found (all tasks were `TODO`).
- Set Task 1 `DOING`, committed alone (`6a3b9e0`) before any build work,
  base commit for the Gate diff is that same commit's parent, `88e73e7`.
- Built Task 1 — vendor the SFace ONNX weights and establish their per-asset
  licence, per `project.md` guardrail 1 (embedded metadata first, then a
  source naming *this* asset):
  - Fetched `face_recognition_sface_2021dec.onnx` from opencv_zoo. Note:
    `raw.githubusercontent.com` serves only a Git-LFS pointer for this file
    (133-byte text, `oid sha256:0ba9fbfa...`, `size 38696353`) — the real
    binary required the LFS-resolving `media.githubusercontent.com/media/...`
    endpoint. Fetched twice from that endpoint, byte-compared identical, and
    both match the SHA-256 GitHub's own LFS pointer records independently.
  - Embedded-metadata check FIRST: scanned the raw `.onnx` bytes for
    `apache`/`licen`/`copyright` (all case variants) plus `SFace`/
    `MobileFaceNet`/`zhongyy`/`doc_string`/`metadata_props` — zero hits for
    all. Sanity-checked the scan method against known-present strings (ONNX
    layer names like `conv_1_conv2d_weight` DO appear), so the absence is
    real, not a broken scan. Same finding as `face_landmarker.task`.
  - Per-asset primary source: opencv_zoo's own
    `models/face_recognition_sface/README.md` states in its own "License"
    section, "All files in this directory are licensed under Apache 2.0
    License" — same directory, same commit as the weight file. This is a
    *stronger* chain than `face_landmarker`'s (which needed three model-card
    PDFs; here the model's own directory names itself directly).
  - `LICENSE` = verbatim upstream text (fetched from the same directory as
    the weights, diffed byte-identical against the fetch). `NOTICE` records
    the full chain: fetch method/verification, both metadata-first and
    primary-source evidence, attribution (SFace paper, contributors), and
    which of the three upstream ONNX variants is vendored (fp32 only).
  - Licence cleared cleanly — no `BLOCKED` path needed.
- Ran Task 1's three done-criteria locally (measurement exception —
  presence/lint/test checks, not a judgment call):
  - §5 cmd 1 (model+licence presence) → exit 0.
  - `uv run ruff check .` → exit 0.
  - `uv run pytest` → 124 passed (unchanged from F5.5, as expected — Task 1
    adds no tests).
- Build commit: `8efb235` (vendored files + `plan.md` Task 1 → `REVIEW`).
- `git status` confirmed no `.gitignore` rule excludes the new
  `models/sface/` directory before committing.

## Failed attempts / lessons

None — licence and fetch verification cleared on the first pass. One
mechanical note worth carrying forward: this is the first vendored asset in
this repo fetched from a Git-LFS-backed path, and `raw.githubusercontent.com`
silently returns the LFS *pointer* text (looks like a tiny valid file, not an
error) rather than failing loudly — worth checking `Content-Type`/size before
trusting a "successful" fetch of any future LFS-tracked asset.

## next_action

**Mode 3 — spawn the clean-context verifier now**, per the universal BUILD
gate. This session's host tool (Claude Code via the Agent tool) has a clean-
context subagent available, so the fresh-eyes verifier runs same-session,
not degraded to a human touchpoint.

- Task: **F6 Task 1** — now `REVIEW`
- Base commit: `88e73e7` (parent of the `DOING` commit `6a3b9e0`)
- Head commit: `8efb235`
- Verifier: `formats/VERIFIER-PROMPT.md`, used verbatim (task id / base / head
  filled in only)
- On REJECT: feedback appended to Task 1's log in `plan.md`, task back to
  `TODO`, `rejects` incremented (budgeted retry, cap 3).
- On APPROVE: `wrap-up` runs, verdict file written to `memory/verdicts/`,
  Task 1 → `DONE`, then Task 2 (commit the three face fixtures) starts
  unattended per Mode 3's standing "go".

## Commits

Session base → head: `88e73e7` → `8efb235` (two commits: `6a3b9e0` DOING
state, `8efb235` build + REVIEW state). This `handoff.md` write will be a
third, bookkeeping-only commit. Nothing pushed — `origin` push was not
requested this session.

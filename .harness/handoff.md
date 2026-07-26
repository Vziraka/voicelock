# Handoff — F4.5 Task 1 built, awaiting verification · 2026-07-26

Session type: `/implement` (build). Task 1 of 3. Mode 3.

## Entry gate — quoted, not remembered
- `spec.md` §0: "- [x] Grilling record below is `CLEAR`" · "- [x] Approved by
  human" · "**Mode:** Mode 3 (Spec-to-done). Set by the human 2026-07-26."
- Marker scan for the bracketed `NEEDS-CLARIFICATION` token in its colon form
  across `spec.md`: **0 hits**.
- `plan.md` ledger scan: no task marked `DONE`, so no missing-verdict
  invalidation to report. Not a retry — `rejects: 0`, feedback log empty.
- `handoff.md` (previous): "Pending guardrail — RESOLVED this session …
  Nothing is pending any more." Nothing to surface to the human.
- Trigger: `spec.md`'s approved `Mode: Mode 3` is the standing go for tasks
  inside this feature (universal [Approval]). No further human word needed.

## Changed this session
- **`pyproject.toml`** — one line added to `[project].dependencies`:
  `"soundfile>=0.14.0"`, alphabetically placed after `sounddevice`.
- **`uv.lock`** — two lines, both direct-dependency edges under the
  `voicelock` package: `{ name = "soundfile" }` in `dependencies` and
  `{ name = "soundfile", specifier = ">=0.14.0" }` in `requires-dist`. The
  `soundfile` package block itself already existed (SpeechBrain transitive),
  so **no version of any package moved** — F4's measured constants are not at
  risk from a resolution change.
- **`plan.md`** — Task 1 `TODO → DOING` (committed first, `da7b8f9`) →
  `REVIEW`; Active-context phase line updated.
- **`handoff.md`** — this file.

**No code file was touched.** `capture.py`, `voiceprint.py`,
`tests/`, and the UI are byte-identical to base — spec §3's non-goals and
§4's "with **no code change**" hold literally.

## What I ran (disclosure)
Only the quick local check the implement skill permits:
- `uv run ruff check .` → `All checks passed!`

I did **not** run `uv run pytest`, nor either of Task 1's two pinned
one-liner assertions (the `tomllib` manifest check and the
`import soundfile` resolution check). Those are Gate commands and stay
reserved for fresh eyes. `uv add` itself reported `Resolved 78 packages` and
reinstalled only the local `voicelock` package, which is consistent with
soundfile already being present in the synced environment — but that is an
observation from the install log, not a verification.

## Unsure about / worth the verifier's attention
- **Line endings.** Git warned `LF will be replaced by CRLF` for
  `pyproject.toml`, `uv.lock`, and `plan.md` on this Windows checkout. The
  committed blobs are LF (the warning describes the working copy), and
  `git diff --stat` showed **3 insertions, 0 deletions** across the two
  manifest files — so no mass line-ending rewrite slipped in. Worth a glance
  anyway if the Gate sees anything odd.
- **The knowingly-accepted limit** (already recorded in
  `memory/decisions.md`, restated so the reviewer does not score it as a
  fresh defect): this declares a main dependency that **no runtime code path
  currently uses** — `load_wav` is exercised only by tests today. That is
  brushing against the earned "no unexercised surface" guardrail, and it was
  weighed and accepted at TECH-PICK time, human-approved 2026-07-26. Task 1's
  notes carry the same reasoning.

## next_action
1. **Verify Task 1** with clean context — `formats/VERIFIER-PROMPT.md` used
   verbatim: `/verify-gate` then `/verify-review`. Task 1's done-criteria are
   its four commands in `plan.md` (the two pinned one-liners plus
   `uv run ruff check .` and the whole `uv run pytest` suite). This is Task 1
   of 3, so the FULL spec §5 list is **not** due here — it lands on Task 3.
2. On APPROVE → `wrap-up` (verdict file + state), then Mode 3 chains
   **Task 2** (`FakeStream` delivers through the real callback + the
   re-entrant-teardown tripwire) in a new build session.
3. Still true for later: Task 3 will reach the Gate as **ESCALATE_HUMAN** on
   spec §5's required 31-second live Booth check. Do not mark it `DONE` or
   write its verdict until the human attests it (F3-T5 / F4-T5 precedent).
4. Read before building Task 2 (carried forward from the plan session):
   `capture.py:135-142` wraps `stream.stop()` / `stream.close()` in
   `except Exception: pass`, so the tripwire must raise a **`BaseException`
   subclass** or Task 3's regression passes while the defect is still live.

## Commits
Base `727fbbc` → build commit `0ae0fd3` (this file's own bookkeeping commit
follows it, per the two-commit rule — a commit cannot contain its own hash).
Intermediate `da7b8f9` is the committed `DOING` write.
Remote: **none** — local history only, nothing pushed.

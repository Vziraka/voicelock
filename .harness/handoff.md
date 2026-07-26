# Handoff — F5 Task 3 built, now `REVIEW`

Session of 2026-07-26. Tasks 1–2 `DONE`. Task 3's licence STOP condition fired,
escalated twice, resolved by the human as **fetched-not-committed**, and is now
built and `REVIEW`. Tasks 4–7 `TODO`.

## Changed

- **`tests/fixtures/face/portrait_expected_face_landmarks.pbtxt`** (29 637 B) —
  **committed**. MediaPipe's own published expected output for `portrait.jpg`,
  from `mediapipe/tasks/testdata/vision/` in the Apache-2.0
  `google-ai-edge/mediapipe` repo. 478 `landmark { x: … y: … }` blocks.
- **`tests/fixtures/face/README.md`** — **committed**. Fetch command, the full
  quoted copyright notice, why the image is absent from git, the measured
  vendor-reference agreement, and the disclosed precedent inversion.
- **`.gitignore`** (committed earlier in the amendment) — line 39 ignores
  `tests/fixtures/face/portrait.jpg`.
- **`.harness/plan.md`** — Task 3 `BLOCKED → DOING → REVIEW`.

**NOT committed, by design:** `tests/fixtures/face/portrait.jpg` (176 561 B,
SHA-256 `A6F11EFA…2749DE3E`). Present on this machine so the Gate can run.

**Zero engine code.** `facedetect.py` is Task 4.

## The escalation, and how it resolved

`portrait.jpg` is a **White House press photograph** (EXIF `Artist = Pete Souza`)
whose notice forbids reproduction or dissemination without written permission
from the White House Photo Office. Committing a fixture is exactly that.

The human's first instinct was that a personal project is covered by the
"personal use only" clause. **It is not** — that permission is granted to *the
subject(s) in the photograph*. Correcting that was the pivot; the human then
chose **fetched-not-committed** over both committing it and substituting a CC0
image, because it preserves the **vendor reference**, which exists for this image
and no other.

A fully-vendored CC0 alternative was researched and verified first (the Met's
c.1850 `-Elderly Man; Full Face-`, 1 face / 478 landmarks) and remains the
documented fallback in
`memory/research/2026-07-26-f5-fixture-replacement-candidates.md`.

## Evidence a verifier should re-check rather than take

- **The photograph is not in git, at all:**
  `git log --all --diff-filter=A --name-only | grep 'portrait.jpg$'` → no match.
  `git check-ignore -v` → `.gitignore:39`. `git ls-files --error-unmatch` → exit 1.
  And `git add -A` was run deliberately before committing: it staged the README
  and the `.pbtxt` and **left the photograph behind**.
- **The vendor reference genuinely matches the vendored bundle** — measured, not
  assumed:
  ```
  reference landmarks: 478   detected: 478
  max abs diff: 0.005645     mean: 0.001051   (normalized coords)
  ```
  ~4.6 px on the 820 px-wide image. **Task 4's tolerance must sit above that
  measured maximum, not at it.**

## Disclosure — exactly which Gate commands I ran (measurement exception)

`uv run ruff check .` → exit 0, plus the two git-state checks and the
vendor-reference comparison above (the comparison is what decides whether the
"practical to parse" branch in `spec.md` §5 is satisfiable, so it had to be
measured before the README could claim it). I did **not** run `uv run pytest`,
the presence check, the README-content check, or the `.pbtxt` size check.

## Doubts, flagged rather than buried

1. **This inverts F3's precedent, and that is a real cost.** `.gitignore` carries
   `!tests/fixtures/voiceprint/*.wav` with the comment "Gate needs them on a
   clean checkout". `portrait.jpg` is the first asset the Gate needs but the repo
   cannot ship. A fresh clone skips the real-model test until it is fetched. The
   README states this; the pinned presence check stops it becoming a silent
   green Gate.
2. **The licence position is unchanged by this arrangement.** Nothing here makes
   the photograph more usable — it keeps it out of permanent history, which is a
   different and narrower claim. Recorded as the human's decision in
   `memory/decisions.md`, with the reasoning and the rejected alternatives.
3. **The published reference has `x` and `y` only, no `z`.** Task 4's comparison
   is 2-D. Noted so it is not mistaken for an omission.
4. **`tests/fixtures/face/` shows as one untracked entry** in `git status` on a
   machine where the image is present — git collapses the directory. That is
   expected, not a leak; the staging check above is the real proof.

## Still open for the human

- **Nothing blocking.** Both licence STOP points are resolved. No guardrail
  proposal is pending.
- `project.md`'s Environment section is stale (*"Tool(s): Cursor only"*);
  re-running `setup` refreshes it. Cosmetic.

## Carried forward, unchanged

- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback: `TARGET_FPS`
  30 → 20 → 15 **on measured evidence**, never by loosening the assertion.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit** — `read()` is the real
  path the fake must deliver through, `release()` the teardown it must trip on,
  with a **`BaseException`** subclass.
- **F6 inherits the arrangement** as well as the two-faces gap, plus a researched
  CC0 shortlist.

## next_action

**Verify Task 3** — clean-context verifier via `formats/VERIFIER-PROMPT.md`,
verbatim, spawned by this session (subagent path, human-authorized). Task 3's
done-criteria are its `plan.md` list; it is an intermediate task.

## Commits

- Task 1: `878186c` → `19b63e5` → `79b022e` → `b21b8ae`
- Task 2: `be938c1` → `e533720` → `6585761` → `1ddf831` → `bded558` → `8aa1e62`
- Amendment 1 + guardrail: `5522bd3` · Amendment 2 (revised): `2876e6f`
- Task 3: `c230109` → `b926819` (BLOCKED) → `0fbadeb` → `d7465da` (DOING
  resumed) → **`5b7670f` (build)**
- Base for the Gate diff: **`d7465da`** · head: **`5b7670f`**
- Plus this bookkeeping commit, putting actual HEAD one ahead — expected.

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

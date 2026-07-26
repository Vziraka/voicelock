# Handoff — F5 Tasks 1–2 `DONE`; Task 3 `BLOCKED` on ONE tick from the human

Session of 2026-07-26. Tasks 1 and 2 built, verified (subagent), `DONE`.
Task 3's licence STOP condition fired and did **not** clear; the human chose a
replacement fixture; the spec amendment is **written and committed**, and the
only thing standing between here and the rest of the feature is **box 2**.

## ⚠ ONE ACTION UNBLOCKS TASKS 3–7

Open `.harness/spec.md` line 10 and change:

```
- [ ] Approved by human      →      - [x] Approved by human
```

I may never check that box myself. Once it is checked, Tasks 3, 4, 5, 6 and 7
can run straight through — nothing else is waiting on you until the **manual
demo** in Task 7, which you already said you would come back for.

**What you are approving** (a note sits directly under the box in `spec.md`):
the fixture changes from MediaPipe's `portrait.jpg` to the Met's CC0
daguerreotype. Nothing else — no scope, no outcome, no non-goal, no camera
architecture, no 30 fps target, no other Verification command.

## Why Task 3 blocked

`portrait.jpg` — the fixture the spec originally named — is a **White House
press photograph**. Its own EXIF carries `Artist = Pete Souza` and:

> "This photograph is provided by THE WHITE HOUSE as a courtesy and may be
> printed by the subject(s) in the photograph for personal use only. The
> photograph may not be manipulated in any way and may not otherwise be
> reproduced, disseminated or broadcast, without the written permission of the
> White House Photo Office."

Committing a fixture **is** reproducing and disseminating it. The image was
downloaded, its metadata read, and the file **deleted**. `tests/fixtures/face/`
was never created; no image is in git.

"It's in Google's Apache-2.0 repo" does not rescue it: the repo ships only the
`portrait_expected_*.pbtxt` **outputs** and no `.jpg` at all, and a
package-level Bazel licence cannot override an asset's own embedded notice.
This is `spec.md` §4's predicted failure mode — more severe than predicted — and
a textbook instance of the `[Approval]` per-asset guardrail approved the same
day.

## The replacement, verified before it was proposed

**`-Elderly Man; Full Face-` (Met 37.14.52)** — CC0 1.0, a c.1850 daguerreotype
by Southworth & Hawes, donated to Wikimedia Commons by the Metropolitan Museum
under its Open Access Policy. Vendored as
`tests/fixtures/face/met_elderly_man.jpg`.

- Licence established **per asset** from the Commons API's per-file
  `extmetadata` (`LicenseShortName: CC0`) — a source that names the asset, the
  standard the new guardrail requires and the one MediaPipe's bucket failed.
- **Detection confirmed against the vendored bundle:** 1 face, **478
  landmarks**; plain grey 640×480 → **0** faces. Both halves of §5's real-model
  test pass, so this will not land red.
- **No living subject** — sitter and both photographers died in the 19th
  century. `spec.md` §4 rejected the repo owner's face on reasoning that does
  not stop at the owner; a c.1850 sitter also cannot ask to be removed later,
  satisfying §4's stability requirement.
- Filename deliberately **not** `portrait.jpg`, so no future reader mistakes it
  for MediaPipe's image.

**Known cost, disclosed not hidden:** the **vendor-reference** assertion is
withdrawn. MediaPipe publishes expected landmarks for `portrait.jpg` only, so
there is no vendor reference for an image we can legally ship. What remains is
the assertion §5 itself calls the important one — a real face at 478 landmarks,
and no face on plain colour. The fixture README must state this, per §5's own
instruction to say so rather than silently assert less.

Rejected alternatives are recorded in
`memory/research/2026-07-26-f5-fixture-replacement-candidates.md` — notably
`Ed Fallon Head Shot 2013.jpg`, CC0 on its face but with a licence-laundering
smell (`Artist` is one person, `Credit` says the uploader got it by email from
another), rejected on the very principle that produced this investigation.

## State of the ledger

| Task | State |
|---|---|
| 1 — declare deps | `DONE` · Gate 5/5 · APPROVE 1st pass · `rejects: 0` |
| 2 — vendor the bundle | `DONE` · Gate 5/5 · APPROVE 1st pass · `rejects: 0` |
| 3 — vendor the fixture | `BLOCKED` on box 2 · `rejects: 0` |
| 4–7 | `TODO`; 4, 5, 7 name the fixture, 6 (UI) does not |

## Two amendments were made today

1. **Approved and in force** — a Standing Verification check that every
   `src/voicelock/models/*/` dir carries a non-stub `LICENSE` and `NOTICE`
   (enforcement half of the new `project.md` guardrail).
2. **Awaiting box 2** — this fixture change.

## Carried forward, unchanged

- **The unmeasured `evaluate_js` bridge throughput** — Task 5's floor covers the
  engine half, Task 7's live check the bridge half. Fallback: `TARGET_FPS`
  30 → 20 → 15 **on measured evidence**, never by loosening the assertion, and
  never by reopening the rejected loopback-MJPEG transport.
- **F4.5's fake-stream shape is what Tasks 4–5 inherit** — `read()` is the real
  path the fake must deliver through, `release()` the teardown it must trip on,
  with a **`BaseException`** subclass.
- **`project.md`'s Environment section is stale** (*"Tool(s): Cursor only"*).
  Re-running `setup` refreshes it. Cosmetic.
- **F6 inherits a changed source** — face B now comes from Wikimedia Commons
  under a verified per-file licence, not MediaPipe's assets.

## Where the rest lives

- Verdicts: `memory/verdicts/2026-07-26-F5-T1.json`, `-F5-T2.json`
- Licence investigations: `…-f5-face-landmarker-licence.md` →
  `…-licence-resolved.md`; `…-f5-portrait-fixture-licence.md` →
  `…-f5-fixture-replacement-candidates.md`
- Decisions: `memory/decisions.md` (verifier path · bundle licence · fixture swap)

## next_action

**Human checks `spec.md` box 2.** Then `/implement` F5 Task 3 and run on through
Task 7. No further approval is expected until Task 7's human-attested manual
demo.

## Commits

- Task 1: `878186c` → `19b63e5` → `79b022e` → `b21b8ae`
- Task 2: `be938c1` → `e533720` (BLOCKED) → `6585761` → `1ddf831` → `bded558` → `8aa1e62`
- Amendment 1 + guardrail: `5522bd3`
- Task 3: `c230109` (DOING) → `b926819` (BLOCKED) → `0fbadeb` (amendment 2)

Session base was `b718038`. Remote: **none** — local history only, nothing pushed.

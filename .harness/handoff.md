# Handoff — curate (second pass) complete; F6 is next

**F5 is DONE and COMMITTED** (`319b48b`, 2026-07-26) — 7/7 tasks, live demo
human-attested, roadmap box checked. The previous handoff said "awaiting the
feature-end commit checkpoint"; that commit has since landed, and this file was
stale until now. No action outstanding from F5.

**This session ran `/curate`** (second pass) at the human's request. All writes
below were human-approved before being made.

## What changed in this session

| File | Change |
|---|---|
| `constitution/project.md` | 4 guardrails → **6**; two updated; stamp refreshed |
| `memory/decisions.md` | one superseded entry MOVED to `## Archive`, unedited |
| `memory/verdicts/2026-07-26-CALIBRATION-RUN-2.md` | **new** — calibration run 2 |
| `.out-of-scope/2026-07-26-calibration-findings-run2.md` | **new** — findings, not fixed |

### Guardrails (human-approved, all three parked proposals adopted)

- **Rule 1 `[Approval]` licence — UPDATED** with proposal B: check the asset's
  own embedded metadata FIRST (EXIF/XMP for images, bundle metadata for models).
  Quoted from `project.md`: *"**Check the asset's own embedded metadata FIRST —
  EXIF/XMP for images, bundle metadata for models** — it is the most
  authoritative statement available and the cheapest to read."*
- **Rule 3 `[Forbidden]` test-double callback — UPDATED**, two drifted
  references corrected. It claimed F5's camera fake did not exist yet and that
  the per-module tripwire "should be repeated in F5's spec"; both are now false.
  Quoted: *"**F5 did repeat the tripwire per-module, and adapted it honestly**"*
  … *"**The shared-base-class question is now answerable and the answer is no**"*.
- **NEW `[Forbidden]` release-on-every-path** (proposal C, strongest evidence —
  two consecutive features). Quoted: *"every path that ends the operation must
  release it — including the paths that end it without user action (timeouts,
  soft caps, error exits)"*.
- **NEW `[Forbidden]` tests must break if the behaviour is removed** (proposal
  A). Quoted: *"Before claiming a test covers behaviour X, delete or neuter X
  and confirm the test fails."*
- Rules 2 and 4 kept unchanged — both actively cited in recent verdicts.
- Stamp now reads: `Last curated: 2026-07-26 (second pass) · verdicts then: 29`.
- Human **declined** trimming rule 1's evidence prose. Not to be re-proposed
  without being asked.

### Calibration run 2 — 0 of 3 agreement, confounds fixed

Full record: `memory/verdicts/2026-07-26-CALIBRATION-RUN-2.md`. Headline: the
0/3 from run 1 **held up** under a corrected setup (verbatim prompt, real
worktrees at the archived commits, per-commit `uv sync`). **2 of the 3 rejects
do not depend on the new guardrails** and are corroborated by the project's own
later behaviour — F4.5 exists to fix the F1-T2 deadlock, and the F2-T3
overwrite-confirm bug was later rewritten. The third (F3-T2) is guardrail-driven
and its Spec axis passed.

Both newly-adopted guardrails were cited by `file:line` in reviews written
minutes after being written. Mutation testing appeared in all three run-2
reviews and in none of the three archived verdicts.

**Method note for run 3:** check out the **bookkeeping** commit, not the build
commit — the build commit's `handoff.md` still describes the previous task.
Run 2 hit this and discarded three verifier runs because of it. Run 3 should
also sample **F4/F4.5/F5** verdicts rather than repeating F1–F3.

## Open items for the human

1. **Commit the curate pass.** Four files are uncommitted (two modified, two
   new). Nothing is committed for this session yet. **Remote: none**, so this
   is a local commit only.
2. **A live code finding is logged, not fixed** —
   `.out-of-scope/2026-07-26-calibration-findings-run2.md`. One blocking item
   (`_resample` and friends are unexercised surface in `voiceprint.py`), plus a
   narrow one (the same-speaker assertion is weak by construction because
   `speakerA_live` is a byte-exact sub-window of the reference takes). Both fit
   **F9 — Demo reliability**. Note `voiceprint.py` is frozen by F4's spec §4, so
   touching it needs a spec that says otherwise. Run 1's items 1 and 2 are now
   **closed** — F4.5 fixed both.
3. **A remote repository was discussed but NOT created.** Findings, so the next
   session does not re-derive them:
   - **No secrets anywhere** — no `.env`/`.pem`/`.key`/vault file in any of the
     190 commits; no key or password patterns; the restricted `portrait.jpg` is
     verifiably absent from all history; the vault lives in `~/.voicelock/`.
   - **`.gitignore` cannot retroactively exclude `.harness`** — all 100 harness
     files are already tracked across 190 commits, and `push` uploads history.
     Excluding it needs an orphan/squashed public branch, two remotes, or a
     `filter-repo` rewrite. The human had not chosen an option when the session
     ended.
   - **`embedding_model.ckpt` is 79.5 MB** — over GitHub's 50 MB warning, under
     the 100 MB block. `.git` is 92 MB.
   - **The author email `zventiyo@gmail.com` is in all 190 commits** and becomes
     public on a public remote.
   - `project.md` records `Remote: none — local history`; changing it is a
     `setup` skill revision, not a hand edit.

## Pending guardrail

None. All three parked proposals were resolved this session (all adopted).

## next_action

**Human: approve the curate commit.** After that, **F6 — Faceprint on screen**
is the next roadmap feature and starts with `/spec`. F6 inherits from F5: the
fetched-not-committed fixture arrangement, the two-faces gap (a CC0 shortlist is
in `memory/research/2026-07-26-f5-fixture-replacement-candidates.md`), and a
second vendored model dir for OpenCV's SFace — which now also owes a per-asset
licence check under the updated rule 1.

# Completion report — F3 (Voiceprint on screen) DONE · Mode 3 · 2026-07-23

## Outcome vs spec §1
**Delivered.** The voiceprint works on screen: the Booth computes a live ECAPA
speaker embedding from the F1 mic path and shows a **live match distance** vs a
stored **reference voiceprint**, colored **accept (green) / borderline (amber) /
reject (red)**. Diagnostic only — **not wired into any lock**, no key derivation,
no vault change (that is F4). Human manual demo attested 2026-07-23: same person →
accept, different person → reject, and the amendment's **Reset** clears the
reference back to the no-reference state.

## Final Gate evidence (full amended §5, all exit 0)
- `uv run ruff check .` → 0 ("All checks passed!")
- `uv run pytest` → 0 (**35 passed**)
- `uv run pytest tests/test_voiceprint.py -q` → 0 (9 passed; §5 cases 1–5)
- `uv run pytest tests/test_booth_api.py -q` → 0 (10 passed; incl. 2 reset tests)
- Manual (human-attested): `uv run voicelock` → Set reference → same=accept/green
  → different=reject/red → Reset clears → re-settable. **Attested PASS by human.**
(Automated Gate run by a clean-context subagent verifier; manual line attested by
the human.)

## Tasks (all DONE · rejects: 0 each)
1. ECAPA deps + vendored offline model (Apache-2.0, rev 0f99f2d) — APPROVE.
2. `voiceprint.py` engine + fixtures + tests (§5 cases 1–5); cutoffs
   `ACCEPT=0.45`/`REJECT=0.65`; offline load via `pretrained_path` override +
   `LocalStrategy.NO_LINK` — APPROVE.
3. Booth voiceprint chrome (3-band meter, Set reference, edge states), JS
   render-only — APPROVE.
4. Bridge (`set_reference`/`compare`) + end-to-end wiring — APPROVE (closed as
   intermediate after the amendment; see below).
5. Reset control (amendment) — APPROVE (final Gate + manual demo).

## Amendment during the feature
- 2026-07-23, human-requested + approved (fresh box-2): added a **Reset** control
  (clears reference + in-progress takes, no confirm). Made Task 5 the new last
  task; Task 4 reclassified to intermediate and closed on its passed automated
  verification (human-approved closure path). Roadmap **F11** parked (manage
  enrollment from inside the vault, post-F7).

## Deviations logged (`memory/deviations.md`)
1. Vendored ECAPA is **~85 MB** (embedding_model.ckpt = 83 MB), not the spec's
   "~20 MB" estimate. Committed plainly (no LFS, offline). **Open for the human:**
   correcting the spec's "~20 MB" wording is a human-only spec edit.
2. Task 3's standalone committed `DOING` was skipped (state went TODO→REVIEW in
   the build commit). Disclosed; verifier judged it a non-defect. Not repeated on
   Tasks 4–5.

## Escalations that resolved
- Task 4 & Task 5 verifiers each returned **ESCALATE_HUMAN** on the required
  manual Booth demo (a headless verifier can't drive a real mic). Task 4's moved
  to Task 5 via the amendment; Task 5's resolved by the human's attestation.

## Honest limitations (as specced)
- Reference vector stored in **plaintext** (`~/.voicelock/voiceprint.ref`) — fine
  for an F3 diagnostic; real sealing is F4.
- Fixtures: one clip per speaker (model-repo examples), so the same-speaker live
  probe overlaps the reference takes — acceptable for a deterministic diagnostic
  fixture, not a cross-session generalization claim (see fixtures README).

## Next
- **Feature-end checkpoint (human):** approve the commit below. No remote —
  local commit only, no push.
- Then F3 is closed. Next roadmap feature: **F4 — Voice as the middle lock**
  (blocked-by F2, F3 — both now DONE). Start with `/spec` when you're ready.

## Commits (this feature, on `main`)
- Spanned `bbeafd2` (F3 plan) → the wrap-up commit below.
- Remote: none — local history only.

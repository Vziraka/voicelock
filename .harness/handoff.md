# Handoff — F4 Task 5 (Booth UI) · /implement session · 2026-07-26

## Where we are
Tasks 1–4 `DONE`. **Task 5 is `REVIEW`** — the feature's LAST task. The automated
half of spec §5 is green; the **required human-attested manual demo is not and
cannot be done by an agent**.

- base: `09b4e39` (Task 5 `DOING`, committed before building)
- head: `6c0a908` (build commit — this handoff's own commit is one after it)

## Changed
- `src/voicelock/ui/index.html` — enroll voice step (5 sentences, per-take dots,
  need-more-audio hint, Enroll disabled until 5 banked), unlock full-sentence
  prompt, `chip-wrong-voice` + `chip-legacy-vault`, and the reject routing
- `tests/test_booth_api.py` — the unused-fixture nit the Task 4 verifier flagged

## The defect this task actually fixes
Before this diff the live Booth could not demo the feature at all. The unlock
handler tested `error === "auth"` — a string the bridge stopped returning in
Task 3 — and its fallthrough called `showWrongPassphrase()` for **every** failure.
So a wrong voice, a legacy vault and a short take all rendered as "Wrong
passphrase", collapsing exactly the two impostor classes the feature exists to
tell apart. Each reason now has its own chip and status line, and the
catch-all fallthrough is gone.

## Spec §5 status — the honest split
**Automated (all run this session, all exit 0):**
- `uv run ruff check .` → 0 (`All checks passed!`)
- `uv run pytest` → 0 (**81 passed in 42.73s**)
- `uv run pytest tests/test_middlelock.py -q` → 0 (36 passed) — §5 cases 1–7
- `uv run pytest tests/test_booth_api.py -q` → 0 (17 passed) — distinct
  `auth_outer` vs `auth_voice`, neither returning a name
- the UI assertion one-liner from Task 5's done-criteria → 0

**Manual — NOT done, and not doable by an agent:**
> `uv run voicelock` → enroll (name + passphrase + read the 5 sentences) → unlock
> with the right passphrase + the enrolled voice → unlocked; **wrong passphrase**
> → outer REJECT; a **different person** speaks with the right passphrase →
> middle REJECT.

It needs a real microphone, the human's own voice, and a second person. I have
not run it and cannot attest it. **The Gate should return ESCALATE_HUMAN on this
line** — the same shape as F3 Task 5, whose verdict records "Manual Booth demo
attested PASS by the human 2026-07-23 ('looks good') after verifier
ESCALATE_HUMAN".

## What the human must do for the manual demo
1. **Re-enroll first.** Your existing `~/.voicelock/vault.vl` is a v1 vault and is
   now refused with the re-enroll message — that refusal is itself part of the
   demo if you want to see it.
2. `uv run voicelock` → Enroll → type name + passphrase → for each of the five
   sentences: **Record → Stop → "Bank this sentence"**. Enroll unlocks only after
   all five bank. Read them in one natural voice.
3. Unlock: type the passphrase, **Record → Stop** a full sentence, press Unlock.
4. Wrong passphrase with your own voice → should read "Wrong passphrase".
5. Right passphrase with **someone else** speaking → should read "Voice didn't
   match". If both rejects read the same, the feature has failed its point.

## Doubts the verifier should weigh
1. **No automated test drives `index.html`.** The UI done-criterion is a string
   assertion over the file — it proves the copy and the wiring text exist, not
   that the window behaves. That gap is exactly what the manual demo covers, and
   spec §5 calls it "a required check, not accepted risk".
2. **Banking a take is a separate button press** ("Bank this sentence") rather
   than automatic on Stop. Record/Stop/Play stay untouched (spec §4), so the
   bridge needs an explicit call to consume the buffer; auto-banking would have
   meant modifying the F1 stop path.
3. **`enroll` consumes the banked takes on success**, so the overwrite/re-enroll
   flow requires re-reading all five sentences. The UI resets its dots to match.
4. **Five sentence texts are my wording**, chosen to be vowel/voiced-heavy per
   spec §3. They are content, not logic — change them freely.

## next_action
Verify Task 5 with **clean context** — `formats/VERIFIER-PROMPT.md` verbatim, task
`F4-T5`, base `09b4e39`, head `6c0a908`. It is the LAST task, so the Gate runs the
FULL spec §5 list and will hit the manual line.

## Pending guardrails — BOTH still await your approval, neither written
1. *(Task 3)* **[Startup]** A task that changes a module's public signature owns
   every in-repo caller of it — the plan must name those callers in `files:`, or
   the done-criteria must not require a green full suite. `warn`
2. *(Tasks 3+4)* **[Forbidden]** Do not add a helper, branch, or method that no
   caller and no test exercises. `warn` — _Evidence:_ both of this session's
   REJECTs were this defect.

## Commits (this session, on `main`)
… → `df29337` (T4 done) → `09b4e39` (T5 DOING) → `6c0a908` (T5 build).
Remote: **none** — local history only, no push.

## Notes for the human (carried)
- `spec.md` §0's amendment paragraph still says "awaiting the human's `x`" though
  box 2 is `[x]`. Stale prose only.
- `spec.md`'s "~20 MB" model-size wording is wrong — the vendored ECAPA is ~85 MB.
- **Curate is due** — 18 verdicts vs `Last curated: never`.

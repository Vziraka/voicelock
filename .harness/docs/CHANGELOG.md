# Harness changelog

One entry per version. Format:
`## {version} — {date}` · what changed · **sync-impact:** every other file that
needed updating in the same change (the line that catches cross-file drift —
if you edited X and didn't check these, the release isn't done).

## 0.5.9 — 2026-07-21
CUI phase (P4, closing the variants program) — with the program's last
design pivot, human-ruled: CUI is NOT a separate copy. The locked-down mode
is BUILT IN and inert — a separate overlay would have forked six skill
files (including both protected verifiers), the exact two-sources-of-truth
drift the harness exists to prevent. (1) NEW `constitution/topics/cui.md`:
the register — pattern-based tripwire holding SHAPES only, never real
values (one real value in the repo defeats the design); Status
INACTIVE until the setup skill's sensitive-data question activates it;
owns the tripwire + research-tier rules (CANON row 17). (2) NEW
`docs/CUI.md`: the handbook — activation, the external translation sheet
(agent generates the skeleton, human hand-fills real values outside the
repo), intake quarantine, fake-sample-data + agent-preps-human-runs
testing split, research tiers R0 (default, no external calls) / R1
(sanitized, org-authorized) / R2, honest limits, and a human-owned
compliance sign-off checklist. Never claims certification, anywhere.
(3) Conditional hooks, all reading the register, all inert when INACTIVE:
setup Q6 activation flow · recon quarantine (candidates shown to the human
BEFORE any write) · scaffold born-clean line · research follows the tier ·
TECH-PICK R0 internal-evidence-or-waiver · verify-gate tripwire scan 🔒 ·
verify-review code-names check 🔒. Variants: the program ends with ONE
generated variant (distribution, the wipe checklist) and one built-in
mode — regeneration deferred until a copy is handed out. **sync-impact:**
constitution/topics/cui.md (new), docs/CUI.md (new), skills/setup,
skills/intake-recon, skills/intake-scaffold, skills/research,
formats/TECH-PICK.md, skills/verify-gate 🔒, skills/verify-review 🔒,
docs/CANON.md (row 17), variants/README.md, manifest.json (0.5.9).

## 0.5.8 — 2026-07-21
Distribution phase (P3 of the variants program), with one design
refinement over the plan: the guidance layer lands in the MASTER (it costs
an expert nothing and its absence costs a novice everything), so the
distribution variant becomes pure subtraction — the master minus its
history, zero overlay files to keep in sync. (1) NEW `GUIDE.md`: one-page
first-feature walkthrough (drop-in → interview → spec approval → build →
verify rhythm → the three protective rules); README points to it top and
Layout. (2) "Next for you" narration: the five first-contact skills
(intake ×2, spec, implement's stop report, wrap-up's closings) end with
the single human action, plus a GUIDE pointer shown only when the
Environment section says first-time user. (3) NEW
`variants/DISTRIBUTION.md`: the mechanical wipe checklist (copy minus
.git/ and variants/; FAILURES/deviations/decisions emptied to headers;
verdict .json and research/out-of-scope content removed; state files
confirmed template; CHANGELOG ships as-is) + pre-handoff verification
greps + generation recording rule. variants/README.md updated to match.
Variants: first real generation happens when a copy is actually handed
out — deferred, recorded here per the standing rule. **sync-impact:**
GUIDE.md (new), README.md (pointer + Layout), skills/intake-recon,
skills/intake-scaffold, skills/spec, skills/implement, skills/wrap-up
(narration lines), variants/DISTRIBUTION.md (new), variants/README.md,
manifest.json (0.5.8).

## 0.5.7 — 2026-07-21
Smoke-fix patch. A fresh-context agent cold-ran intake-scaffold on v0.5.6 in
a throwaway repo (the P1/P2 validation gate before any variant generation):
the flow passed end-to-end with zero silent workarounds — including the
deviations mechanism correctly absorbing the one unfollowable rule it hit —
and produced five findings, all fixed here (see FAILURES.md source: smoke,
2026-07-21). (1) README title carries NO version anymore — manifest.json is
the single version owner (the banner went stale twice; closed by mechanism,
not memory). (2) Both intakes' close step handles a fresh repo's first
commit: base `none — initial`, head via a follow-up bookkeeping commit.
(3) Curate counter counts `*.json` verdict files only, stated in wrap-up
AND curate. (4) project.md ships the stamp as a real value
(`never · 0`), not a placeholder pattern. (5) wrap-up step 3 preserves
handoff.md's parenthetical format rules; the pending-guardrail rule
clarifies Modes 3–4 (first human touchpoint = feature-end checkpoint).
Polish from the smoke's confusion notes: setup question 2 gained its
default; scaffold enumerates its four completion files and offers a minimal
`.gitignore`. Variants: none exist yet — regeneration deferred trivially.
**sync-impact:** README.md (title), skills/intake-recon (close step),
skills/intake-scaffold (close step, step 3, completion criterion),
skills/wrap-up (curate check, step 3), skills/curate (step 7),
constitution/project.md (stamp), handoff.md (pending-guardrail rule),
skills/setup (question 2), FAILURES.md (5 smoke entries), manifest.json
(0.5.7).

## 0.5.6 — 2026-07-21
Reminders phase (P2 of the variants program). The "run curate every ~10
tasks" trigger and parked guardrail proposals were fully manual to track —
no counter, no reminder (an enrichment-triage finding). Fix uses no new
state: the verdict archive IS the counter. (1) curate now writes a stamp
into `project.md`'s Earned guardrails section (`Last curated: {date} ·
verdicts then: {n}`; template line added). (2) wrap-up step 6 counts
`memory/verdicts/` files against the stamp — at ≥10 it prints "Curate is
due" and tags handoff's next_action "(curate due)"; a reminder only, curate
stays human-invoked, nothing blocks. (3) `handoff.md`'s Pending-guardrail
line now owns the rule that a non-none value is put to the human at the
reading session's first touchpoint — approve, decline, or explicit defer;
never silently carried past one session. implement's entry gate points to
that rule. Variants: none exist yet — regeneration deferred trivially.
**sync-impact:** constitution/project.md (stamp line), skills/curate
(step 7), skills/wrap-up (step 6), handoff.md (Pending-guardrail rule),
skills/implement (step 2 pointer), manifest.json (0.5.6).

## 0.5.5 — 2026-07-21
Setup phase (P1 of the variants program). NEW `skills/setup` — the
environment interview, run by both intake skills right after their git
check and re-runnable directly to revise an answer. Seven questions via
grilling, each with a recommended default (accepting all defaults is a
valid ~2-minute path): tool(s) · model(s) · subagent availability (recorded
as the verifier path the no-subagent fallback reads) · signposts (both
AGENTS.md + CLAUDE.md stays the recommended default per the settled
reasoning; single-file is an informed, recorded opt-out) · git remote
(local-only default; remote wired once, existing checkpoint rules take
over) · sensitive-data screening (none / secrets-in-config rule /
CUI-class warning that this copy has no redaction machinery) · first-time
user (Mode 1 recommended for the first feature). Answers land in
`constitution/project.md`'s new Environment section — recorded settings the
rules read; the rules themselves never change per answer. Setup also OFFERS
the Claude Code adapter install instead of leaving it as a manual step
(the parked convenience idea from the ledger, now real). Gate: intake must
not write conventions or signposts while the Environment section is
missing. Variants: none exist yet — regeneration deferred trivially.
**sync-impact:** skills/setup (new), constitution/project.md (Environment
template), skills/intake-recon (step 1 + step 6), skills/intake-scaffold
(step 1 + step 4), docs/COMMANDS.md (setup row + chooser line), README.md
(15→16 commands), adapters/claude-code/README.md (setup-offers-install
note), manifest.json (0.5.5).

## 0.5.4 — 2026-07-21
Structure phase (P0 of the variants program). Reference docs moved into
`docs/`: ARCHITECTURE.md, CANON.md, COMMANDS.md, and this file. State files
(spec/plan/handoff/roadmap/CONTEXT), FAILURES.md, README, manifest, and
protected.txt deliberately stay at root — they are the daily-touch and
front-door files, and moving the heavily-referenced state files was rejected
as the known 404-at-minimum-context bug class. New master-only `variants/`
folder (README stub): home for the distribution wipe checklist and CUI
overlay, arriving in later phases; variants are generated copies, never
edited directly. Migration map: `ARCHITECTURE.md → docs/ARCHITECTURE.md` ·
`CANON.md → docs/CANON.md` · `COMMANDS.md → docs/COMMANDS.md` ·
`CHANGELOG.md → docs/CHANGELOG.md`. Release checklist addition (standing,
from this version on): a release isn't done until the variants are
regenerated or the deferral is recorded in the release entry — no variants
exist yet, so this release defers trivially. **sync-impact:**
adapters/AGENTS-template.md, docs/CANON.md (footer), skills/curate/SKILL.md
(step 4), README.md (banner note line, command-list link, Layout section),
variants/README.md (new), manifest.json (0.5.4). Historical path mentions in
this file and FAILURES.md are records of the past and intentionally
unchanged.

## 0.5.3 — 2026-07-20
The enrichment patch: a comparative audit against four external sources (cold
Codex 5.6 vs briefed Fable 5, three-round relay debate, human-ruled triage)
produced seven adopted improvements + three doc fixes. (1) Doc contradictions
fixed: README banner, CONTEXT.md dead /domain-modeling pointer, decisions.md
archive-move exception named in its header. (2) learn asks "enforce instead of
remember?" before drafting prose guardrails; curate flags mechanizable prose.
(3) CONTEXT.md entries carry a _From:_ link to the decision/source that
introduced the term (TECH-PICK writes it at pick time). (4) grilling gains a
prerequisite-ordering rule + parallel fact lookups + a pointer to Mode 4's
batching path; one-question-at-a-time unchanged. (5) spec's Verification
requires proof at the highest real surface (or a recorded limitation).
(6) NEW constitution/topics/code-quality.md — the universal quality floor the
Reviewer's Standards axis enforces from day one (surgical scope default;
restructuring needs execution evidence; beyond-the-diff coupling named;
security findings need a traced path); CANON row 16 declares the owner.
(7) implement gains a bug-fix recipe: reproduce on the reported surface →
root-cause evidence → cheap failing test → same-surface re-check (disclosed,
measurement-exception style); verify an existing fix baseline-vs-patched,
never author a competitor; no-repro = BLOCKED. Deferred by ruling: caller-first
architecture sketch (hand-run pilot on the next real deployment first);
confidence tiers, proactive explain offer, and a separate Reviewer
blast-radius question all skipped. Full control-skill / UI-verification design
stays parked for v0.6. **sync-impact:** README.md (banner), manifest.json
(0.5.3), CONTEXT.md, memory/decisions.md, skills/learn, skills/curate,
skills/grilling, skills/spec, spec.md, skills/plan, skills/implement,
skills/explain, formats/TECH-PICK.md, constitution/topics/code-quality.md
(new), skills/verify-review 🔒, constitution/universal.md 🔒, CANON.md
(row 16), FAILURES.md (3 audit entries).

## 0.5.2 — 2026-07-18
Cold-start blocker fix (the ledger's fix-immediately exception): the harness
assumed git exists but never checked — in a git-less folder intake's own
commit checkpoint cannot complete. Found by the human's real cold-drop-in
test (fresh folder, no git, no signpost, only `.harness/`). Both intake
skills' step 1 now check for git and run `git init` before proceeding
(recon additionally flags a git-less existing codebase to the human).
Two further real-use findings logged, not fixed: universal-vs-skill read-list
drift at intake; the all-templates-means-run-intake note (second data point —
confirmed cosmetic). **sync-impact:** skills/intake-scaffold,
skills/intake-recon, FAILURES.md, manifest.json (0.5.2).

## 0.5.1 — 2026-07-17
The audit patch: an independent static audit (contract tracing across files —
the third finding channel after simulation and real use) found the unattended
Mode 2–4 loop wasn't closed. All P0s fixed, drift swept; two findings parked
for v0.6 (monorepo Gate scoping, full non-Claude adapters) — see FAILURES.md
`source: audit` entries.
(1) **Retry chain closed** — a FAIL/REJECT with `rejects:` below the 3-cap is
now itself the implement trigger (unattended at Modes 2–4, on "go" at Mode 1);
cap applies in EVERY mode (human ruling). (2) **Executor owns post-verdict
bookkeeping** — one session, never both; canonical in VERIFIER-PROMPT's
closing frame (CANON row 15); verify skills reference it; codebase-map gets a
single writer (wrap-up). (3) **No-subagent fallback** — Modes 2–4 on a host
without clean-context subagents commit state, write handoff, and stop for a
fresh-session verifier; never self-verify. (4) **Promises aligned** — Mode 2/3
feature-end checkpoint stated in the universal Modes table; Mode 4 unlock
single-sourced to universal with a mechanical check (dev_mode verdict +
completion report); Mode 4 drafts the parked spec BEFORE the feature-end wait;
Mode 2 checkpoint presents the final-verdict summary; COMMANDS/README
de-Mode-1-ified; BLOCKED recovery runbook added (README). (5) **spec-lite
exits through minimal wrap-up** — only wrap-up marks DONE, learn stays the
single verdict writer. Plus: spec reads `.out-of-scope/`, "pinned
expectations" defined, plan.md Mode line marked convenience-copy, verifier
path-base note, ADR path deferred to formats/ADR.md, AGENTS template Modes
blurb, CANON rows 1/9/12 refreshed, ARCHITECTURE edges corrected, manifest
readFirst completed, dead future-commands marked ideas-only.
**sync-impact:** universal.md, skills/verify-gate, skills/verify-review (the
protected trio — human-delegated), skills/implement, skills/wrap-up,
skills/spec, skills/spec-lite, skills/plan, formats/VERIFIER-PROMPT.md,
COMMANDS.md, README.md, ARCHITECTURE.md, CANON.md, AGENTS-template.md,
spec.md, plan.md, FAILURES.md, manifest.json (0.5.1).
**Re-audit 2026-07-17: PASS with nits — all applied same-day:** README banner
0.5.1 + Mode note in "How you use it" · Modes table says wrap-up (not the
Gate) marks DONE · chained-context advisory landed in implement (was settled
scope, missed) · wrap-up trigger speaks the executor rule, not
"invokes itself" · verify-gate FAIL states "subagent writes NO state files" ·
universal credits learn as the verdict writer.

## 0.5.0 — 2026-07-17
The freeze release: designed from the ranked pattern across the Tier 2
simulated stress run (~25 sessions) and the first REAL dogfooding run (the
human finished the project by hand) — 16 new `FAILURES.md` entries, most
marked fixed here. Design record: `harness-research/V0.5-DESIGN.md` (outside
this tree).
**Development Modes (the headline).** The human picks, per feature in the
spec's Approval gate, how hands-on to be: Mode 1 supervised (v0.4 behavior) ·
Mode 2 trusted cycles (default) · Mode 3 spec-to-done + completion report ·
Mode 4 continuous roadmap (batch-grilled next spec parked at the approval
gate; unlocks after one clean Mode 3 feature). Human-only in every mode: spec
approval, amendments, escalations. Mechanics: retry budget 3 (durable in
`rejects:`), multi-task sessions with full wrap-up checkpoints, unfollowable
rule = BLOCKED at Modes 3–4 / logged-then-resolved at Modes 1–2, new
append-only `memory/deviations.md` judgment-call log + curate scan.
**Fixes (B-numbers per the design doc):** section references by NAME not
number (B1) · greppable colon-form clarification marker (B2) · declared
`.harness/`-relative path base (B3) · two-commit rule ends the
handoff-hash impossibility (B4) · `DOING` committed before building (B5) ·
long-run Gate protocol — 10-min default budgets, foreground waiting,
watchdogs forbidden, overrun = FAIL never kill (B6) · VERIFIER-PROMPT speaks
both clean-context paths + required `mechanism` verdict field (B7) ·
known-defect flag duty before spawning the verifier (B8) · measurement-task
exception (B9) · state-file precedence + tie-break (B10) · wrap-up: DONE
literally last, Active-context refresh, codebase-map refresh-or-STALE (B11) ·
mid-build rejections → `.out-of-scope/` (B12) · four-step amendment path with
box-2 re-check (B13) · pre-build sessions record base→head hashes (B14) ·
Claude Code adapter installs skills into `.claude/skills/` + honest
COMMANDS.md (B15) · TECH-PICK granularity finding downgraded to style note
(B16) · plain-language pass — "Mode/Feature/Task/section" spelled out in all
prose, no section-sign symbol, compact codes only in verdict filenames and
commit tags (B17).
**sync-impact:** universal.md, protected.txt, skills/verify-gate,
skills/verify-review, memory/verdicts/README.md (the five protected files —
human-applied from the staged wording), spec.md, plan.md, handoff.md,
skills/spec, skills/spec-lite, skills/plan, skills/implement, skills/wrap-up,
skills/design, skills/intake-recon, skills/intake-scaffold, skills/curate,
skills/grilling, formats/VERIFIER-PROMPT.md, COMMANDS.md, README.md,
ARCHITECTURE.md, CANON.md (rows 9–14), FAILURES.md, adapters/claude-code/,
memory/deviations.md (new), manifest.json (0.5.0).

## 0.4.1 — 2026-07-15
Live-shakedown fixes (Tier 1 simulation run, 11 sessions, todo CLI): the three
deterministic bugs the run observed in execution, fixed under the freeze's
BLOCKER exception; everything else logged to `FAILURES.md`, not fixed.
(1) **Pre-build session close-out** — spec/plan/design/intake sessions left
`handoff.md` stale and made zero commits; the five pre-build skills gain a
close-the-session step (handoff update + commit checkpoint).
(2) **Task-level gating** — the universal [Done] rule demanded full spec §5 on
every task, which can never PASS an intermediate task of a multi-task feature;
amended so intermediate tasks gate on their `plan.md` done-criteria and only
the feature's LAST task runs the full §5 list.
(3) **Verdict naming + schema** — `{date}-{task}.json` collides across features
(ids restart per feature); now `{date}-F{n}-T{n}.json`, plus optional `note`
fields so honest annotations aren't schema drift.
`FAILURES.md`: 7 simulation entries logged (3 count toward the freeze quota,
human ruling 2026-07-15).
**sync-impact:** universal.md, skills/spec, skills/plan, skills/design,
skills/intake-recon, skills/intake-scaffold, skills/verify-gate, skills/wrap-up,
skills/learn, spec.md, formats/VERIFIER-PROMPT.md (stale "every spec §5 command"
caught by the defrift grep — would have re-broken fix 2), ARCHITECTURE.md,
memory/verdicts/README.md, FAILURES.md, README.md, manifest.json (0.4.1).
**Freeze:** still in force — this patch is the BLOCKER exception, batched.

## 0.4.0 — 2026-07-14
Research layer (`skills/research` + `formats/source-playbooks/` ×3, Gray
zone = FAIL), defrift mechanics (`CANON.md`, curate defrift check, this file),
institutional memory (`.out-of-scope/`, `memory/research/`), dormant
calibration (`memory/verdicts/CALIBRATION.md`), freeze log (`FAILURES.md`),
root AGENTS template (`adapters/AGENTS-template.md`, installed by intake),
seven parked review changes (spec §5 two-part commands, Uncertainty→grilling,
grilling fact/decision split + human-controlled nice-to-haves, curate→
decisions.md archiving, intake-scaffold toolchain-first-task, TECH-PICK
goal-anchoring + playbooks), style pass over all skills (constraints early,
positive phrasing, caps dialed down, no-op deletions), anti-test-gaming line
in implement, VERIFIER-PROMPT reordered data-first.
**sync-impact:** README.md, COMMANDS.md, manifest.json (0.4.0, 15 commands),
universal.md, grilling, spec + spec.md, curate, intake-recon, intake-scaffold,
design, implement, TECH-PICK.md, VERIFIER-PROMPT.md.
**Post-release freeze:** no harness edits until `FAILURES.md` has 5–10 real
entries, except true BLOCKERs (lifecycle cannot proceed).

## 0.3.0 — 2026-07-13
Real-use fixes: inline verification (`formats/VERIFIER-PROMPT.md`,
`adapters/claude-code/`), commit checkpoints (auto-local at implement,
human-approved commit+push at verification end), `formats/TECH-PICK.md`,
`memory/decisions.md`, write-before-proceed + session-end-state + no-silent-
installs hard rules, codebase-map in read order, ARCHITECTURE.md.
**sync-impact:** universal.md, implement, verify-gate, verify-review, wrap-up,
learn, spec, design, handoff.md, README.md, COMMANDS.md, manifest.json.

## 0.2.0 — 2026-07-11
Audit fixes: verdicts append-only carve-out + single verdict writer,
DONE-requires-verdict rule, commit protocol, `rejects:` counter + feedback
log, `Feature:` linkage, wrap-up reordered (DONE last), spec-lite
(human-invoked), human-duties README section, narrowed model claim.
**sync-impact:** protected.txt, universal.md, both verify skills, wrap-up,
learn, implement, spec.md, plan.md, handoff.md, verdicts/README.md,
README.md, COMMANDS.md, manifest.json.

## 0.1.0 — 2026-06 (initial build)
Core loop: constitution router + hard rules, spec/plan/roadmap/handoff state
files, 13 skills, protected.txt immutable-evaluator, verdict archive design.
Audited 2026-07-11: 14 findings (1 blocker, 9 major) → v0.2.

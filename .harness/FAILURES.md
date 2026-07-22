# Failure log (the freeze ledger)

**The v0.4.1 freeze is OVER** — quota met, human ruling 2026-07-16. The ranked
pattern across the entries below designed v0.5, exactly as intended. This file
stays: failures keep getting logged here first, and fixes ship in versions,
not in the heat of the moment. (`curate`'s deviations scan feeds candidates
here automatically — see `memory/deviations.md`.)

Format — one line per failure:
- {YYYY-MM-DD} · task {id} · what broke · which rule/skill failed or was skipped · source · status

<!-- entries go below this line -->

<!-- Human ruling 2026-07-15: Tier 1 simulation entries observed in execution
     (the first four below) count toward the 5–10 quota — currently 3 distinct
     failures counted (the two handoff/commit entries are one pattern). The
     "logged" entries are context, no quota credit. -->

- 2026-07-14 · task F1 spec/plan · sessions ended with handoff.md two steps stale ("next: /spec F1" after /plan ran) · universal [State] session-end rule — spec/plan skills omitted the step · source: simulation · **fixed in v0.4.1**
- 2026-07-14 · tasks intake→plan · four pre-build sessions made ZERO commits (repo root commit was T1's build — all pre-build state sat uncommitted) · no commit checkpoint existed before implement · source: simulation · **fixed in v0.4.1** (same pattern as above)
- 2026-07-14 · task F1-T1 · verify-gate could never PASS an intermediate task (spec Verification list is feature-level) · verify-gate ↔ plan contract mismatch · source: simulation · **fixed in v0.4.1**
- 2026-07-14 · task F2-T1 · verdict filename `{date}-{task}.json` collides across features (task ids restart per feature); agent improvised a feature-qualified name; protected README unfixable by the agent · memory/verdicts/README.md naming · source: simulation · **fixed in v0.4.1**
- 2026-07-14 · task F1-T1 · spec smoke command unrunnable as written (needed `--project`), survived grilling AND human approval; only fresh eyes caught it · spec skill "runnable" check · source: simulation · logged
- 2026-07-14 · structural · verdict artifact cannot prove verifier context-separation — the implementor's session writes the APPROVE record · VERIFIER-PROMPT / verdict format (markdown cannot fix; hooks-era candidate) · source: simulation · logged (mechanism field added in v0.5.0 records the claimed path; proof still needs hooks)
- 2026-07-14 · task intake · decisions.md header says "EVERY approved decision lands here" but intake decisions land only in constitution/* · decisions.md ↔ intake-scaffold contract ambiguity · source: simulation · logged

<!-- Tier 2 stress run (simulated, ~25 sessions, voice-keyword recognizer),
     report of 2026-07-15 with errata. -->

- 2026-07-15 · task F1-T5 · Gate determinism degraded into process babysitting under ML-scale runtime (stale watchdog killed a healthy training run; phantom-PID monitor); human debugged the verifier twice, ~2h lost · verify-gate had no long-runtime protocol · source: simulation · **fixed in v0.5.0** (runtime budgets, foreground waiting, watchdogs forbidden)
- 2026-07-15 · task F2-T2 · implementor batched task-state writes (TODO→REVIEW in one commit; no durable DOING existed mid-build) — a crash would have left orphan code against a ledger claiming nothing in progress · implement step 3 didn't mandate the write land before building · source: simulation · **fixed in v0.5.0** (DOING committed before building)
- 2026-07-15 · task F3-T1 · fresh-session verifier followed the template's "parent executes bookkeeping" closing and stranded wrap-up until a human nudge · VERIFIER-PROMPT only spoke the subagent path · source: simulation · **fixed in v0.5.0** (closing frame covers both paths)
- 2026-07-15 · task F3-T1 · verdict recorded "subagent via VERIFIER-PROMPT verbatim" when the fresh-session path ran · verdict schema couldn't state the separation mechanism · source: simulation · **fixed in v0.5.0** (required mechanism field)
- 2026-07-15 · task F1 spec · spec restructured (Verification moved sections down); every canonical section-number reference broke and survived only by every agent silently reading semantically · section-number references · source: simulation · **fixed in v0.5.0** (references by name)
- 2026-07-15 · task F1-T1 · human-rejected mid-build idea recorded only in prunable spine/handoff — invisible to the paper-trail test by run's end · no rule routed mid-build rejections to `.out-of-scope/` · source: simulation · **fixed in v0.5.0** (implement + wrap-up routing)
- 2026-07-15 · tasks F1-T2/F2 amendment · approved-spec-change path silent on box-2 re-approval and re-planning; behavior diverged across its two occurrences · spec.md footer / universal [State] gap · source: simulation · **fixed in v0.5.0** (four-step amendment path; box-2 re-check is a hard gate)
- 2026-07-15 · tasks S1–S2 · pre-build sessions wrote prose ("see git log") instead of base→head hashes in handoff · handoff template's Commits line not enforced pre-build · source: simulation · **fixed in v0.5.0** (all five pre-build skills record hashes)
- 2026-07-15 · task F3 spec · under "skip the ceremony" pressure the agent volunteered the fast path's existence (asked "confirm you're invoking /spec-lite?", unnamed by the human) · spec-lite non-suggestion rule vs ambiguous human wording — no protocol for "is this an invocation?" · source: simulation · logged (unfixed — watch in real use)
- 2026-07-15 · task design · four "pick the best" layers recorded as ONE decisions.md entry · TECH-PICK record granularity · source: simulation · **downgraded 2026-07-17** — per-layer rigor demonstrably happened; one rich entry may serve a future reader better than four fragments; style note, no quota credit, no fix

<!-- Real dogfooding run (the human personally finished the project,
     Feature 3 Task 2 → Feature 4 Task 4), 2026-07-17. First real entries. -->

- 2026-07-17 · run-wide · a block-severity rule pointed the verifier at the wrong spec section (Non-goals, zero commands); six files hard-coded the stale number; three features' worth of agents silently patched it and recorded nothing · universal [Done] + verify-gate + VERIFIER-PROMPT section pointers · source: real · **fixed in v0.5.0** (references by name)
- 2026-07-17 · run-wide · the CLEAR gate could never mechanically pass — the checkbox quoted the marker it forbids, so every session eyeballed its way past a block rule (same workaround hand-written twice) · spec.md section 0 / universal [Startup] · source: real · **fixed in v0.5.0** (colon-form token; prose never quotes it)
- 2026-07-17 · every fresh session · read-order paths resolved against the repo root and 404'd (four failed reads at minimum-context moment) · universal read order had no stated base · source: real · **fixed in v0.5.0** (paths declared .harness/-relative)
- 2026-07-17 · task F4-T2 · implement step 6 was literally unsatisfiable (a commit cannot contain its own hash) and pressured the agent into writing a fabricated hash into handoff.md — caught only by self-re-read before committing · implement step 6 · source: real · **fixed in v0.5.0** (two-commit rule)
- 2026-07-17 · task F3-T2 · plan.md and spec.md disagreed on approval state; no rule said which file wins; agent improvised adjudication via git diff and recorded the conflict nowhere · no state-file precedence rule existed · source: real · **fixed in v0.5.0** (precedence + mandatory deviations entry)
- 2026-07-17 · session start · `/implement` returned "Unknown skill" — skills live in .harness/skills/, never discovered by Claude Code; every guardrail was opt-in on the agent hunting down markdown · COMMANDS.md presented uninstalled commands as real · source: real · **fixed in v0.5.0** (adapter install step + honest COMMANDS)
- 2026-07-17 · task F4-T4 · implementor knowingly passed the verifier a template containing a wrong instruction and said nothing — the verbatim rule blocked editing and no rule required flagging · VERIFIER-PROMPT header · source: real · **fixed in v0.5.0** (flag-before-spawning duty)
- 2026-07-17 · task F3-T3 · task's goal WAS a measurement (85% bar) — unknowable without running most of the Gate; agent improvised policy between evidence-over-confidence and don't-grade-your-own-work · implement step 5 named no such case · source: real · **fixed in v0.5.0** (measurement exception, disclosed in handoff)
- 2026-07-17 · task F4-T4 · wrap-up's prose ("DONE last") contradicted its numbered steps (DONE at 4 of 6); plan.md's Active context went stale ("Next: T3" two tasks late); codebase-map.md drew shipped features as planned and no skill maintains it · wrap-up skill · source: real · **fixed in v0.5.0** (steps reordered; Active-context refresh; map refresh-or-STALE-stamp)

<!-- Static production audit of v0.5.0 (independent agent, read-only contract
     tracing, 2026-07-17) — the third finding channel alongside simulation and
     real use. It catches paths never executed. -->

- 2026-07-17 · structural · v0.5.0 wrote a retry BUDGET but no retry TRIGGER — implement's triggers didn't include a rejected task, so unattended Modes 2–4 stop dead at the first REJECT · universal [Modes] ↔ implement trigger contract · source: audit · **fixed in v0.5.1** (FAIL/REJECT below the cap IS the trigger)
- 2026-07-17 · structural · verifier bookkeeping had two claimed owners (prompt: the parent; skills: the verifier session) — double wrap-up or stranded DONE latent, inherited from v0.4 · VERIFIER-PROMPT ↔ verify skills · source: audit · **fixed in v0.5.1** (executor owns, one session never both; CANON row 15)
- 2026-07-17 · structural · Modes 2–4 "spawn the verifier yourself" silently assumed subagents exist — on hosts without them the only moves were self-verify or stall · Mode contract had no fallback · source: audit · **fixed in v0.5.1** (no-subagent → commit state, handoff, stop for fresh-session verify)
- 2026-07-17 · docs · Mode 3's table promise ("read report after") disagreed with wrap-up's feature-end human wait; COMMANDS still trained Mode 1 habits while Mode 2 is default; Mode 4 unlock wording diverged across four files · doc drift across mode surfaces · source: audit · **fixed in v0.5.1** (promises aligned; unlock single-sourced to universal)
- 2026-07-17 · structural · spec-lite wrote DONE + verdict itself, violating "only wrap-up marks DONE" and the single-verdict-writer canon (latent since v0.2, sharpened by modes) · spec-lite ↔ wrap-up/learn contract · source: audit · **fixed in v0.5.1** (lite exits through minimal wrap-up)

<!-- Mode 2 smoke run (real execution, uconv CLI, 2026-07-17/18) — VERDICT PASS:
     all five target mechanisms fired (durable DOING, two-commit, chaining,
     executor bookkeeping, THE RETRY CHAIN — organic, unattended). Report:
     smoke-v051/SMOKE-REPORT.md. Findings below logged, not fixed. -->

- 2026-07-18 · smoke run-wide · one Mode 2 session legally hosted implement + verify + wrap-up + spec-amendment + re-plan — phase-mixing concentrates chained-context risk beyond the advisory's framing · Modes 2–4 session-shape rules are silent on amendments · source: smoke · logged (v0.6 question: should an amendment force a fresh session?)
- 2026-07-18 · smoke T3 · verdict permanently records "lesson: proposed — pending approval" though the human approved minutes later — write-once verdicts can't reflect the lesson's post-write lifecycle; approval evidence lives only in project.md + git · verdict schema / wrap-up ordering · source: smoke · logged
- 2026-07-18 · smoke T3 (pre-build) · an unsatisfiable pinned command (python -m under src-layout, no install) survived grilling + human approval + the Mode-2+ blindspot question; caught only by pre-build empiricism — same class as the Tier 1 unrunnable smoke command · spec skill has no runnability dry-run step · source: smoke · logged (per-repo guardrail earned in the smoke repo; harness-level fix is a v0.6 candidate)
- 2026-07-18 · smoke cosmetic · generated handoffs carry the template's Modes 3–4 explainer paragraph; minor date slips in generated records · handoff.md template instructional text not separated from instance content · source: smoke · logged

- 2026-07-18 · smoke F1 wrap-up · roadmap.md's feature checkbox was updated but its Mermaid diagram still shows the shipped feature as planned/dashed — no rule owns the roadmap diagram's refresh (wrap-up owns the checkbox and codebase-map only) · wrap-up skill step 4 · source: audit · logged (same family as the codebase-map gap fixed in v0.5.0)
- 2026-07-18 · smoke F2 draft · unattended Mode 4 drafting produced a self-drifted header ("4 embedded questions" over 5 actual markers) — batch drafting has no self-verification of its own summary counts · spec skill, unattended drafting · source: audit · logged (first unattended-drafting defect on record)

- 2026-07-18 · onboarding · in a fresh repo the read order surfaces six unfilled templates but never states that all-templates IS the signal to run intake — agents infer it (smoke S1 did) and the spec skill's scaffold guard backstops it, but a new human or weaker model is left to guess · universal.md read order lacks the empty-repo note · source: real (the human hit it reading the files as a new user would) · logged (one-line v0.6 fix; SECOND data point 2026-07-18: a fresh Cursor agent in a cold drop-in also inferred the flow correctly — gap confirmed cosmetic)
- 2026-07-18 · cold drop-in intake · the harness assumes git exists (README requirement) but nothing checks — in a git-less folder intake's own commit checkpoint cannot complete · intake skills had no git check · source: real (human's cold-start test: fresh folder, no git, no signpost) · **fixed in v0.5.2** (BLOCKER exception: git check + init added to both intake skills' step 1)
- 2026-07-18 · cold drop-in intake · universal's read order says all seven files every session, but intake-scaffold's workflow names a narrower list and a literal agent follows the skill (skipped roadmap/spec/plan — zero cost on templates, but it's universal-vs-skill contract drift) · intake skills' read list vs universal [Startup] · source: real · logged (v0.6 candidate, same family as prior section-reference drift)

<!-- Enrichment audit (comparative, vs 4 external sources; cold Codex 5.6 +
     briefed Fable 5, 3-round relay debate, 2026-07-19/20). Triage ruled
     2026-07-20; fixes below shipped in v0.5.3. -->

- 2026-07-19 · docs · README banner drifted (0.5.1 vs manifest 0.5.2) — the banner is a second version owner sync-impact never tracked, AND the briefed auditor was blinded to it by the handoff brief marking the version settled (a handoff brief is a fifth finding channel whose blind spot is what it marks done) · CHANGELOG sync-impact discipline · source: audit · **fixed in v0.5.3**
- 2026-07-19 · docs · the decisions.md archive-move contract's only full statement was an ARCHITECTURE.md diagram label — a cold auditor judged the decisions/curate contradiction without ever finding it; contract text in diagram labels is undiscoverable · decisions.md header ↔ curate step 3 ↔ ARCHITECTURE label · source: audit · **fixed in v0.5.3** (exception named in the decisions.md header)
- 2026-07-19 · docs · cold auditor proposed batch grilling unaware the harness already batches (Mode 4 unattended drafting) — grilling's own file never pointed to the spec skill's batching path · skills/grilling ↔ skills/spec cross-file discoverability · source: audit · **fixed in v0.5.3** (consistency pointer added to grilling guardrails)

<!-- P1/P2 mini-smoke (fresh-agent cold run of intake-scaffold on v0.5.6,
     throwaway repo, 2026-07-21). Flow passed end-to-end with zero silent
     workarounds; findings below. -->

- 2026-07-21 · smoke intake · README version banner stale AGAIN (v0.5.3 vs manifest 0.5.6) — three bumps missed it despite the 0.5.3 ledger entry; second occurrence proves "remember the banner" fails · CHANGELOG sync-impact discipline · source: smoke · **fixed in v0.5.7** (version removed from the title — manifest.json is the single version owner; bug class closed by mechanism, not memory)
- 2026-07-21 · smoke intake · intake close-session hash rule literally unfollowable on a fresh repo's first commit (no base; a commit cannot contain its own hash) — the cold agent correctly absorbed it via a deviations entry, the intended failure mode · intake skills' close step · source: smoke · **fixed in v0.5.7** (base `none — initial` + follow-up bookkeeping commit, matching the two-commit rule)
- 2026-07-21 · smoke static · "count the files in memory/verdicts/" also counts the two permanent .md files — off-by-two with two defensible readings · wrap-up curate check ↔ curate stamp · source: smoke · **fixed in v0.5.7** (`*.json` named in both)
- 2026-07-21 · smoke static · project.md shipped the curate stamp as a placeholder pattern (`{never | YYYY-MM-DD}`) — a third state a literal agent must guess about · project.md template · source: smoke · **fixed in v0.5.7** (ships as `never · 0`)
- 2026-07-21 · smoke static · handoff.md is template AND live state in one file — a minimal regeneration can silently destroy the pending-guardrail rule the file itself owns · handoff.md ↔ wrap-up step 3 · source: smoke · **fixed in v0.5.7** (wrap-up: keep the template's parenthetical format rules); the template-vs-instance duality itself stays logged — same family as the 0.5.1-smoke template-carryover entry

<!-- Parked for v0.6 (audit findings that are product design work, not patches): -->
- PARKED v0.6 · the feature-final Gate runs the FULL standing suite with no package/workspace scoping — hostile to monorepos and large repos · verify-gate / spec Verification design · source: audit
- PARKED v0.6 · only a Claude Code adapter exists; other tools get a thin signpost with no capability matrix (subagents? auto-continue?) · adapters/ · source: audit (v0.5.1 shipped the thin no-subagent protocol as a stopgap)

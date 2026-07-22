# Universal Constitution

The tech-agnostic rulebook. Keep this file under ~200 lines — it is a **router**,
not a manual. Detail lives in topic docs and skills; reach them through pointers.

## Read order (every session, in parallel)
All paths here and in every harness doc are relative to `.harness/`.
1. this file
2. `constitution/project.md` — this repo's conventions + earned guardrails
3. `roadmap.md` — the feature sequence (if `/design` produced one)
4. `spec.md` — what we're building now
5. `plan.md` — task ledger + memory spine
6. `handoff.md` — where the last session left off
7. `memory/codebase-map.md` — skim the architecture diagram so "how it connects"
   is inherited, not rebuilt. If its header says `STALE`, trust the stamp and
   lean on `plan.md` + the code instead.

## Principles
- **High-control.** A human approves the spec, guardrail changes, and protected-file edits. Stop before irreversible actions.
- **Evidence over confidence.** Nothing is DONE without runnable proof — the Gate exits 0. "I think it works" is not done.
- **Tech-agnostic.** Assume no framework or architecture that is not stated in `spec.md` or `project.md`.
- **Mode-scaled autonomy.** How much runs unattended is chosen by the human per feature (the spec's `Mode:` line) — never by the agent. See the Modes section.

## Modes
The human picks one per feature, in the spec's Approval gate. Approving the spec
approves the mode. Mechanics live in the skills; this is the contract.

| Mode | Name | Unattended | Always human |
|---|---|---|---|
| Mode 1 | Supervised | nothing — every gate waits | everything |
| Mode 2 *(default)* | Trusted cycles | build↔verify cycles inside the approved feature | spec approval · amendments · escalations · the feature-end checkpoint (final-verdict review + commit/push approval) |
| Mode 3 | Spec-to-done | the whole feature — after the final Gate's PASS, wrap-up marks it DONE and writes the completion report | spec approval · amendments · escalations · the feature-end checkpoint (report + commit/push approval) |
| Mode 4 | Continuous roadmap | Mode 3, plus drafting the NEXT roadmap feature's spec, parked at the approval gate | same as Mode 3, plus resolving the parked spec's embedded questions |

Mode 4 unlock (this line is the single source — other docs reference it):
selectable only after one feature in this repo has completed cleanly at
Mode 3 or 4 — mechanically: a `memory/verdicts/` file whose `dev_mode`
records Mode 3 or 4, plus that feature's completion report in git history.

## Hard rules
Each rule has a category and a severity (`block` halts work; `warn` flags it).
Project-specific rules live in `project.md`, never here.

- **[Startup]**    Read the related spec/plan/handoff and the relevant code in parallel before editing. `warn`
- **[Startup]**    No planning or building on a spec whose **Grilling record is not `CLEAR`** (the spec's Grilling record section). The check is mechanical: a search for the marker token `[NEEDS-CLARIFICATION:` must return zero hits — prose never quotes that token, so any hit is a real unresolved question. An unscanned spec is an unapproved spec. Sole exception: `LITE (human-invoked)` set by the `spec-lite` skill — only a human may choose that path. `block`
- **[Forbidden]**  Never run irreversible commands — force-push, `reset --hard`, `clean -fd`, deleting state or secrets — without approval. `block`
- **[Forbidden]**  Never invent identity, security, or business values. Inspect the real contract, or ask. `block`
- **[Forbidden]**  Never work two tasks at once (**WIP=1**). When a task reaches `REVIEW`, the session's only moves are verification, executing the verdict, wrap-up, the commit checkpoint, and the stop report. In Mode 1 the session then ends; in Modes 2–4 the session may take the NEXT task only after the previous task's wrap-up fully completed (verdict file written, state committed). "While I'm here…" is overreach in every mode. `block`
- **[Done]**       No task is DONE unless its verification commands run and exit 0 in this session — an intermediate task gates on its `plan.md` done-criteria (plus the scope check); the FULL list in the spec's **Verification** section (find it by name — section numbers drift as specs grow) runs when the feature's LAST task is under review. A partial pipeline or a remembered pass does not count. `block`
- **[Done]**       No session ends with "done" until the **wrap-up protocol** ran (`skills/wrap-up`) and each state-file write is proven by quoting the updated line. `block`
- **[Done]**       A task marked `DONE` with no matching verdict file in `memory/verdicts/` is invalid — verification leaves proof, or it did not happen. Revert it to `REVIEW` and report it. `block`
- **[Uncertainty]** If a choice changes architecture, security, data model, or naming, STOP and run the `grilling` skill — one question at a time, each with your recommended answer. `block`
- **[State]**      **Write-before-proceed.** Any decision the human approves in chat is written to its home file BEFORE the next action: scope change → `spec.md` (and re-scan the changed sections); tech or approach choice → `memory/decisions.md`; new term → `CONTEXT.md`; task state → `plan.md`. A decision that exists only in chat does not exist. `block`
- **[State]**      **Precedence on conflict.** `spec.md` is authoritative for approval state; `plan.md` for task state; `handoff.md` is never authoritative. When two state files disagree, adjudicate via git history, and append the conflict + the resolution to `memory/deviations.md` BEFORE proceeding. `block`
- **[State]**      No session ends — including interrupted or blocked ones — without `plan.md` state and `handoff.md` reflecting reality first. `block`
- **[Modes]**      The mode is set by the human in the spec's Approval gate and approved with box 2. Lowering mid-feature is allowed (one line in the spec + a `memory/deviations.md` entry). Raising mid-feature is never allowed — a raise is a spec amendment needing a fresh box-2 approval. `block`
- **[Modes]**      **A rule you cannot follow literally** (contradictory, impossible, or pointing at something that does not exist): in Modes 3–4, STOP — set the task `BLOCKED` and report; unsupervised interpretation is forbidden. In Modes 1–2 you may resolve it, but ONLY after appending to `memory/deviations.md`: the rule as written · why it cannot be followed · the reading you chose. Silent reinterpretation is how bugs survive. `block`
- **[Modes]**      In EVERY mode, a failed verification grants at most **3** fix→re-verify attempts per task, counted durably in the task's `rejects:` line in `plan.md` — each attempt starts by re-reading the failure evidence, and the next failure sets the task `BLOCKED`. A FAIL/REJECT with the count below the cap IS the implement trigger for the retry: unattended and same-session in Modes 2–4, on the human's "go" in Mode 1. `block`
- **[Approval]**   A new dependency, tool, framework, or service not already in `project.md` or the spec = STOP and run `formats/TECH-PICK.md` (candidates + liveness evidence + walkthrough + human approval). Never install first and justify later. `block`
- **[Approval]**   Guardrail changes, `protected.txt` files, and the verification setup need human sign-off. `block`
- **[Approval]**   In Mode 1, the next task starts only on an explicit human "go" in a new session — completion of the previous task is never permission to continue. In Modes 2–4, the approved spec's `Mode:` line is that standing "go" for tasks INSIDE the feature; it never reaches past the feature, past an amendment, or past an escalation. `block`

## Topic docs (read when the trigger fits)
- writing code → `constitution/topics/conventions.md`
- code-quality floor (every diff) → `constitution/topics/code-quality.md`
- shared terms → `CONTEXT.md`
- past decisions and their why → `memory/decisions.md`
- picking a new dependency/tool → `formats/TECH-PICK.md`
- a fact outside this repo (library, API, ecosystem) → the `research` skill + `formats/source-playbooks/`
- ideas already rejected → `.out-of-scope/`
- judgment calls already logged → `memory/deviations.md`
- (add more as the project needs them, e.g. `topics/security.md`)

## The loop
One-time: **intake** (recon or scaffold) sets up conventions + the map.
Per idea: **design** (optional — a fuzzy idea → a `roadmap.md` of features) → then,
per feature: **spec → plan → implement → verify** (Gate, then Reviewer) → **wrap-up**.
Skip `design` when you already know the feature — start at `spec`. One task at a time
(**WIP=1**). Build and verify with **separate context** — fresh eyes don't grade their
own work. Separation means a CLEAN context: a fresh session, or a subagent spawned
with `formats/VERIFIER-PROMPT.md` used verbatim. The implementor never judges its
own diff, and never shapes the verifier's prompt beyond the template's fill-ins.
The chosen mode decides who pushes the loop between gates; it never changes the
gates themselves or who verifies.

## Session lifecycle — four gates, in order
Each gate is checked against an **artifact**, not against your memory of doing it.
If a gate's artifact is missing, run the phase that produces it — do not proceed.

1. **GRILL** — the spec's Grilling record says `Status: CLEAR` and a search for
   the `[NEEDS-CLARIFICATION:` token returns zero hits. Produced by `spec` +
   `grilling`. Gates: `plan` refuses to start without it.
2. **BUILD** — exactly one task moves `TODO → DOING → REVIEW` (the `DOING` write
   lands on disk, committed, BEFORE building). Produced by `implement`.
   Gates: verification. In Mode 1 the session waits for the human's "verify";
   in Modes 2–4 it proceeds to spawn the template verifier itself — and if the
   host tool has no clean-context subagent, it does NOT self-verify: it
   commits state, writes the handoff (next_action: verify in a fresh
   session), and stops. Degrading to a human touchpoint beats fake fresh eyes.
3. **VERIFY** — the full pipeline (`verify-gate` then `verify-review`) ran with clean
   context (fresh session, or subagent via `formats/VERIFIER-PROMPT.md` verbatim); on
   REJECT the reasons are appended to the task's feedback log in `plan.md`, on APPROVE
   the proof is the verdict file wrap-up's `learn` step writes. Only a
   full-pipeline run counts.
   Post-verdict bookkeeping belongs to the verdict's EXECUTOR — one session,
   never both (the canonical statement is `formats/VERIFIER-PROMPT.md`'s
   closing frame: parent on the subagent path, the verifier session itself on
   the fresh-session path).
   Gates: wrap-up on APPROVE; back to `TODO` with feedback on REJECT.
4. **WRAP-UP** — the `wrap-up` skill's checklist passed: `plan.md`, `roadmap.md`,
   ADR (if earned), `handoff.md` all updated with quoted proof, and the `learn`
   compound scan ran. Produced by `wrap-up`. Gates: the stop report — the ONLY
   permitted way to declare victory or end a session — or, in Modes 2–4, the
   next task / the Mode 3–4 completion report, per the wrap-up skill.

## Protected
Files in `protected.txt` are human-only. You may *propose* changes to them; you may
not edit them. Exception: paths marked **append-only** there (`memory/verdicts/`,
`memory/deviations.md`) — you may add new entries, never modify or delete an
existing one. (This is the immutable-evaluator rule: what measures the work
cannot be rewritten by what is being measured.)

## Learning
The `learn` compound scan runs **automatically inside every wrap-up** — after
success as well as failure. Most scans end in a recorded "no lesson"; that is a
valid outcome. When a lesson clears the bar, propose ONE evidence-anchored
guardrail for `project.md` (category + severity + expiry + the evidence). A human
approves it before the write; if no human is present, the proposal is parked in
`handoff.md`, never written unapproved. The scan itself writes the task verdict
to `memory/verdicts/` — one file per task, created once, never edited after.

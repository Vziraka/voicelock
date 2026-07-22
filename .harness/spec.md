# Spec: {TASK NAME}

Feature: {Feature {n} from `roadmap.md` | none}

## 0. Approval gate
- [ ] Grilling record below is `CLEAR` (a search for the clarification marker —
      the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns
      zero hits in this file)
- [ ] Approved by human
- **Mode:** {Mode 1 | Mode 2 | Mode 3 | Mode 4}

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks
it, no matter what was said in chat.

The Mode line is set by the human; checking box 2 approves the spec AND the
mode together (Mode 2 is the default if the human states no preference).
Mode 4 may only be set if a prior feature in this repo completed cleanly at
Mode 3 or 4. Lowering the mode mid-feature is allowed (edit this line + log it
in `memory/deviations.md`); raising it mid-feature is never allowed — a raise
is a spec amendment needing a fresh box-2 approval.

## 1. Outcome
What this change achieves, and why. 1–3 sentences.

## 2. Grilling record — ambiguity scan
**Status: PENDING** ← the `spec` skill sets this to `CLEAR` only when every row is
Clear/Resolved and no clarification marker remains. `plan` refuses to run
while this says PENDING.

| Category | Verdict | Resolved by |
|---|---|---|
| Functional scope & behavior | Clear / Partial / Missing | {question # / codebase / n-a} |
| Domain & data model | | |
| Interaction & UX flow | | |
| Non-functional (perf, security) | | |
| Integration & dependencies | | |
| Edge cases & failure modes | | |
| Completion signals (how we know it works) | | |
| Terminology (matches `CONTEXT.md`) | | |

Answers from grilling are written back into the matching section of THIS file —
never into a side file. Mark anything still open inline where it belongs, using
the marker token: open square bracket, `NEEDS-CLARIFICATION`, a colon, then the
question. The colon form is what the mechanical check greps for — prose that
merely *mentions* the marker (like this paragraph) never uses the colon form,
so any hit is a real unresolved question.

## 3. Non-goals
What we are explicitly NOT doing (prevents scope creep).
-

## 4. Constraints
Frameworks, interfaces, conventions, and prior decisions the build must honor.
-

## 5. Verification — definition of done (runnable)
The exact commands the Gate runs. Each must exit 0. Two parts, both required.
Harness rules find this section by its NAME ("Verification"), never by number —
keep the word "Verification" in the heading if sections are added or reordered.
(This FULL list gates the feature's LAST task; intermediate tasks gate on their
`plan.md` done-criteria — see the universal [Done] rule.)

Runtime budgets: any command expected to run longer than the 10-minute default
must declare its budget here (e.g. `{command}` → exit 0, budget 25 min). The
verifier waits in the foreground either way; exceeding the budget is a FAIL,
never a kill.

Mode-scaled requirements: at Mode 2+, every command here must be runnable with
pinned expectations — pinned means: the exact command, its exact expected exit
code, and any expected output stated in the line (nothing left to judgment). At Modes 3–4, additionally every task's planned
done-criteria must be runnable (no judgment-worded criteria), and this spec
must state what the agent does with discovered out-of-scope work (default:
record it in `.out-of-scope/`, never build it).

Standing (the project's full regression net, from `project.md`):
- `{full test suite}` → exit 0
- `{lint / build}` → exit 0

Proof surface: feature-specific commands must prove behavior at the highest
real surface the feature touches — the actual UI, CLI, or API (a script that
drives the real thing counts). If that surface cannot be checked, record the
exact limitation here; never let a proxy check silently stand in for it.
Bug fixes: the feature-specific list includes the reproduction — the same
surface the bug was reported on.

Feature-specific (proves THIS feature works):
- `{command}` → exit 0
- Manual (only if unavoidable): {observable check}

---
_Spec-anchored: if requirements change mid-build with human approval, this is
the amendment path — ALL of it, in order: (1) update this file, (2) re-run the
ambiguity scan on the changed sections, (3) the human re-checks box 2 (an
amended spec is a new contract — the old approval does not carry over),
(4) re-plan the affected tasks via the `plan` skill before building against
the change._

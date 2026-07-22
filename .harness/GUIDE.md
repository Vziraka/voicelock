# GUIDE — your first feature, start to finish

One page. Follow it top to bottom the first time; after that you won't need
it. (Stuck at any point? README.md's "When it stops" runbook is the rescue
path.)

## 0. What this thing is (30 seconds)
The harness makes an AI agent build software the disciplined way: everything
gets written down, every claim gets checked by fresh eyes, and nothing big
happens without your yes. You are the approver; the agent does the work.

## 1. Drop-in (once)
Put the `.harness/` folder in your project root. Tell your AI tool: "read
`.harness/README.md` and run intake." The agent will:
- turn the folder into a git repository if it isn't one (history + undo),
- interview you — about 7 quick questions, each with a recommended answer
  (accepting every default is fine and takes ~2 minutes),
- offer to wire the commands into your tool (say yes),
- learn or ask about your project's conventions.
You answer questions; the agent writes everything down. When it says
"complete", this step is done — forever, for this repo.

## 2. Say what you want built
- Know the specific feature? Say: "run /spec: {describe it}".
- Only a rough idea? Say: "run /design: {describe it}" — it interviews you,
  proposes approaches, and produces an ordered feature list; then /spec runs
  on the first feature.
Questions come ONE at a time, each with a recommended answer. "I don't
know — take your recommendation" is a valid answer.

## 3. Approve the contract (the important moment)
The spec is the contract the work is measured against. The agent stops and
waits. You do two things IN THE FILE `.harness/spec.md`:
- read the Outcome and Verification sections (what gets built, how it's
  proven),
- set the Mode line (Mode 1 = it waits for you at every step — right for
  your first feature) and type the `x` in the "Approved by human" box
  yourself. The agent may never check that box. That's by design.

## 4. Let it build
Say "run /plan" (the spec becomes small tasks), then in a FRESH session:
"run /implement". The agent builds exactly one task and stops. At Mode 1
you then say "verify" — fresh eyes (a clean second agent) check the work
against the contract. You see PASS/FAIL evidence, never vibes.

## 5. Your rhythm from here
Each round: build → fresh-eyes verify → you approve the commit message →
"go" starts the next task. At every stop the agent tells you what just
happened and what you do next. All tasks done = feature done — the next one
starts back at step 2.

## The three rules that protect you
1. If the agent asks you to approve something, read it first — gates only
   work if the human at them is awake.
2. Never raise the autonomy Mode mid-feature because you're tired of
   clicking. Lowering is always allowed; raising waits for the next feature.
3. When something stops or blocks, that's the harness WORKING — open
   README.md's runbook and follow it.

---
name: explain
description: Explain an unfamiliar tool, library, or term in plain English and record it. Optional — use whenever the agent introduces something you don't understand, before you approve anything that uses it. Skip it when you already know the tech.
invocation: user
---
# Explain (interrogate an unknown)

Turns "I don't know what that is" into enough understanding to decide — without a
rabbit hole. Optional: it only runs when you invoke it, so skip it whenever you
already know the tech.

## Trigger
You hit a tool/library/term you don't understand and are about to approve something
that uses it.

## Workflow
Answer these three in plain English (define any jargon you must use):
1. **Job** — in one sentence, what does it do in *our* system?
2. **Tradeoff** — why this over the obvious alternative, and what does choosing it cost?
3. **Blast radius** — if it broke or we removed it, what stops working?
Then offer to add a one-line entry to `CONTEXT.md` (term · plain definition ·
_Avoid_ · _From:_ the decision or source that introduced it, when one exists).

## Guardrails
- Decision-level, not a tutorial — stop at "enough to approve," not "expert."
- If the honest answer to #2 is "no strong reason," say so — that's a finding, not a failure.
- Offer to let the user guess each answer first, then correct it. Learning by predicting sticks.

## Completion criterion
All three answered plainly, and the term is offered for `CONTEXT.md`.

## Output
The three answers, plus (on yes) an updated `CONTEXT.md`.

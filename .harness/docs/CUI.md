# CUI — the locked-down mode (activation, the sheet, rules of the road)

For projects handling Controlled Unclassified Information or similar
regulated data. This mode is BUILT IN and inert: nothing here does anything
until the setup skill activates the register
(`constitution/topics/cui.md`). Activate by answering setup's
sensitive-data question with "regulated/CUI-class" — or re-run `setup`
anytime.

The one-sentence model: the repo's paperwork stays clean enough to leak;
the real names live on one sheet only you hold; nothing leaves the machine
without a recorded decision.

## What changes when the register is ACTIVE
- All harness paperwork (specs, plans, handoffs, verdicts, commit messages,
  research files) uses code names ({SYSTEM-A}), never real sensitive
  values. Code reads real values from config files kept out of git.
- The Gate and Reviewer scan every diff + commit message against the
  register's forbidden patterns — any hit is an automatic FAIL/REJECT.
- Research follows the recorded tier (R0 default: no external calls).
- Intake runs its quarantine: anything the survey finds that matches a
  register category is shown to you and code-named BEFORE it is written
  into any file.

## The translation sheet (the secret half — NEVER in this repo)
The setup skill generates the skeleton (code names + categories filled,
real values blank) as chat output. Copy it somewhere your organization
approves — password manager, printed sheet, wherever such things live.
Then fill the real values in by hand. Handling rules, kept on the sheet:
- never stored in the repo; never pasted into an AI chat;
- one owner: the compliance approver named in the register;
- rows are retired, never deleted — old paperwork must stay translatable;
- lost the sheet? The skeleton is regenerable anytime from the register;
  only the real-value column needs re-filling from org records.
When a session proposes a new code name (quarantine or mid-build), the
agent prints the new row minus the real value; you append it to the sheet.

## Testing in CUI mode
- Local proof: the agent invents fake-but-realistic sample data from the
  SHAPE you describe — real records are never pasted anywhere.
- Real-surface proof: the agent prepares the exact command with code-name
  placeholders; YOU run it inside the real environment and report pass/fail
  (paste only scrubbed output). The spec records this as a named
  limitation, per the proof-surface rule.

## Research tiers (recorded in the register at setup)
- R0 (default): no external research. Unverifiable claims are labeled
  "training data, unverified". TECH-PICK liveness evidence comes from
  internal registries or you — otherwise a recorded waiver.
- R1 (org-authorized only): external queries allowed, generic technology
  terms only — zero project names, zero register-category values; every
  query shown to you before it runs and logged in the findings file.
- R2: normal harness behavior — for confirmed non-CUI projects only.

## Honest limits — read once, believe forever
- The tripwire catches only the SHAPES on the register. A sensitive value
  matching no listed pattern sails through. The exact-value check is yours,
  with the sheet, at every approval checkpoint.
- The harness cannot control what your AI tool transmits to its own
  servers. Which tool may touch CUI work is your organization's decision —
  recorded here, never enforced or certified here.

## Compliance sign-off checklist (human-owned, out of band)
- [ ] Org approved the AI tool in use for this data class
- [ ] Research tier authorized in writing (who / when)
- [ ] Translation sheet stored per org policy; owner named
- [ ] Register patterns reviewed by the compliance approver
- [ ] This checklist's answers live wherever your org keeps such records

This mode configures product behavior. Compliance approval belongs to your
organization, not this folder.

# CUI register — {REPO NAME}

Pattern-based tripwire. This file holds SHAPES, never real values — one real
sensitive value in this file defeats its purpose (the repo must stay clean
even if it leaks). The real-value translation sheet lives OUTSIDE the repo,
human-held — see `docs/CUI.md`.

**Status: INACTIVE** {| ACTIVE since YYYY-MM-DD — set by the setup skill}
Compliance approver: {the human who owns the translation sheet}
Research tier: {R0 — no external research (default) | R1 — sanitized
queries, org-authorized, recorded | R2 — normal (non-CUI projects only)}

## Code names (the safe half — the sheet's skeleton is regenerable from this)
| Code name | Category | Safe description |
|---|---|---|
| {SYSTEM-A} | system | {what it is, in words safe to leak} |

## Forbidden patterns (what the tripwire scans for — shapes only)
- ip-address: any dotted-quad other than 127.0.0.1 / 0.0.0.0
- id-format: {e.g. two letters, dash, four digits}
- hostname-like: {internal domain shape}

## Rules (in force only while Status is ACTIVE)
- Specs, plans, handoffs, verdicts, commit messages, and research files use
  code names only. Code reads real values from config files outside git.
- The Gate and the Reviewer scan the diff and commit message against the
  forbidden patterns: any hit = FAIL/REJECT, no judgment involved.
- The exact-value check is the human's, with the translation sheet, at the
  existing approval checkpoints.
- Research follows the recorded tier. R0: no external calls; unverifiable
  claims are labeled "training data, unverified"; TECH-PICK liveness
  evidence comes from internal registries or the human — otherwise a
  recorded waiver.

This file configures product behavior. Compliance approval belongs to your
organization, not this folder.

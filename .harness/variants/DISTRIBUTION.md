# DISTRIBUTION — generating a give-away copy (master-only)

The distribution copy IS the master minus its history: same engine, same
docs, same guidance — ledgers emptied. Never edit a generated copy;
regenerate it.

## Generate (mechanical — follow literally)
1. Copy the whole harness folder EXCEPT `.git/` and `variants/`.
2. `FAILURES.md` — delete every entry line and comment block below the
   format line; keep title, intro, format. (The empty file ships on
   purpose: it teaches the discipline and receives the deviations-scan
   pipeline.)
3. `memory/verdicts/` — delete every `*.json`; keep `README.md` and
   `CALIBRATION.md`.
4. `memory/deviations.md` — keep everything above the first entry; delete
   the entries.
5. `memory/decisions.md` — keep the template; delete all entries and any
   `## Archive` section.
6. `memory/research/` — delete all findings files; keep `README.md`.
7. `.out-of-scope/` — delete all idea files; keep `README.md`.
8. State files (`spec.md`, `plan.md`, `handoff.md`, `roadmap.md`,
   `CONTEXT.md`, `memory/codebase-map.md`, `constitution/project.md`,
   `constitution/topics/conventions.md`) — confirm each is in template
   state; if any accumulated real content, restore the template from git
   history.
9. `docs/CHANGELOG.md` ships AS-IS — the honest version record, deliberate.

## Verify before handing it to anyone
- Grep the copy for dated entries (`- 202`) in FAILURES.md, deviations.md,
  decisions.md → zero hits.
- `memory/verdicts/*.json` → zero files. `variants/` → absent.
- `manifest.json` version matches the master it came from.

## Record
Note the generation (version · date) in that release's changelog entry —
the standing rule: a release isn't done until variants are regenerated or
the deferral is recorded.

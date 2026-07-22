# variants/ — master-only

This folder never ships. It holds the blueprints for generating the
distributed versions of the harness from this master copy:
- `DISTRIBUTION.md` — the wipe checklist: the give-away copy is the master
  minus its history (pure subtraction — no overlay files to maintain; the
  guidance layer lives in the master and ships with everything).
- CUI is NOT a separate copy: the locked-down mode is built into the master
  (inert `constitution/topics/cui.md` register + `docs/CUI.md` handbook),
  activated per-repo by the setup skill's sensitive-data question. Any
  generated copy can activate it — no overlay to maintain.

Generation rule: a variant is never edited directly — regenerate it from
the master. A release isn't done until variants are regenerated or the
deferral is written down in that release's changelog entry.

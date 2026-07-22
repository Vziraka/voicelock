# Out of scope — institutional memory of "no"

When an idea is rejected, write `.out-of-scope/{concept}.md` so nothing
rejected gets silently re-proposed. `design` and `spec` read this folder
during scoping and concept-match new requests against it.

Two rules:
- **"Already implemented" does NOT go here** — that would poison the
  dedup check. This folder holds only deliberate "no"s.
- A rejection can be reversed — by the human, explicitly. The file then gets
  a superseding note, not a deletion.

Format per file:

    # {Concept}
    {One line: what this project does not do.}
    ## Why this is out of scope
    {The substantive reason.}
    ## Prior requests
    - {date / task where it came up}

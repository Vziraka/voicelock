# ADR format

An **Architecture Decision Record**. Write one ONLY when all three are true:
1. hard to reverse, 2. surprising without context, 3. a real trade-off existed.
Otherwise skip it — an easy or obvious decision needs no record.

Location: `docs/adr/NNNN-short-title.md` (or `.harness/adr/` if the repo has no `docs/`).

Write the file as (one paragraph is fine):

    # {Short title of the decision}

    {1–3 sentences: the context, what we decided, and why. Optionally name the
    main alternative we rejected and the constraint that drove the choice.}

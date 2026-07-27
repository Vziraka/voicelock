# `torchaudio` has no first-party import after F5.5 Task 2

**Recorded:** 2026-07-26 · **Found during:** F5.5 Task 2 (deleting `_resample`)
**Status: OUT OF SCOPE — recorded, not built.**

## What was found

`_resample` was the only place in this repo that imported `torchaudio`:

```
src/voicelock/voiceprint.py:220:    import torchaudio.functional as func
```

Deleting `_resample` (F5.5 Task 2, mandated by `spec.md` §4) removes that
import, so `torchaudio>=2.11.0` is now a **directly declared dependency with no
direct first-party import**.

## Why it is not being acted on

1. **It is not in `spec.md` §1.** F5.5's Outcome names three things, none of
   them a dependency change. `spec.md` §5's Modes 3–4 default is explicit:
   *"anything discovered during the build that is not in §1 gets recorded in
   `.out-of-scope/` and is never built."*
2. **`spec.md` §4 forbids touching `pyproject.toml`** ("No new dependencies.
   Nothing enters `pyproject.toml`"). Deleting a line from it during a
   deletion-only task would be scope creep on the file the constraint names.
3. **Removing it would change nothing.** `speechbrain` declares
   `torchaudio>=2.1.0` itself (verified 2026-07-26 via
   `importlib.metadata.requires('speechbrain')`), so `torchaudio` stays
   installed and the resolved environment is identical either way. This is a
   tidiness question about the declaration, not a functional one — and it is
   not obviously the right call: a transitive dependency we rely on being
   present is arguably worth declaring anyway.

## If anyone revisits it

The question to answer is whether this project declares dependencies it uses
directly (drop the line) or dependencies it needs present (keep it). That is a
convention decision for `project.md`, not a code change, and it should be
settled once rather than per-module. It has no bearing on F6.

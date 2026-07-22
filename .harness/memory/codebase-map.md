# Codebase Map — VoiceLock

A light, human-readable map so a fresh session can navigate without re-reading
everything. It is **not** a second source of truth — the code is the truth.
Regenerate it when it drifts.

- Greenfield: seeded by `design` (2026-07-22); layout locked by intake-scaffold
  (2026-07-22). **Dashed = planned, solid = built** — nothing built yet.

## Architecture (data flow)

Same boxes as `roadmap.md`.

```mermaid
flowchart TB
    Mic([Microphone])

    subgraph Window["Desktop window — Booth UI"]
        Booth["Booth — modes, challenge,<br/>passphrase (F1)"]
        Viz["Visualizer — live levels (F1)"]
    end

    Bridge{{"UI ↔ engine bridge (F1)"}}

    subgraph Engine["Engine"]
        Capture["Audio capture (F1)"]
        Voiceprint["Voiceprint — identity signal (F3)"]
        Challenge["Liveness: challenge match (F5)"]
        Fuzzy["Fuzzy reconcile — helper data (F4)"]
        Outer["Outer lock — passphrase → AEAD (F2)"]
        Inner["Inner lock — voice codeword → AEAD (F4)"]
    end

    Vault[("Profile vault on disk (F2)")]

    Mic --> Viz
    Mic --> Capture
    Booth <--> Bridge <--> Capture
    Booth -- "passphrase" --> Outer
    Capture --> Voiceprint
    Capture --> Challenge
    Voiceprint --> Fuzzy
    Fuzzy -- "inner key" --> Inner
    Fuzzy <-. "helper data" .-> Vault
    Outer --> Vault
    Inner --> Vault
    Challenge -- "gate before unlock" --> Inner

    classDef planned stroke-dasharray:6 4
    class Mic,Booth,Viz,Bridge,Capture,Voiceprint,Challenge,Fuzzy,Outer,Inner,Vault planned
```

## Shape
- `.harness/` — governing harness (roadmap, specs, conventions).
- `design/` — mock UI reference (`voicelock-mock.html`); not final chrome.
- `src/voicelock/` — app engine (planned; F1 creates it).
- `src/voicelock/ui/` — HTML/CSS/JS booth (planned; adapted from mock).
- `tests/` — pytest suite (planned; F1 creates it).

## Key modules
(None yet — greenfield. F1 creates the first.)

## Where things live
- Entry point(s): `uv run voicelock` (planned, F1)
- Tests: `tests/` via `uv run pytest`
- Config: `pyproject.toml` + `uv.lock` (planned, F1)
- Lint: `uv run ruff check .`

## Conventions
See `constitution/topics/conventions.md`.

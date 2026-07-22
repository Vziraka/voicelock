# Codebase Map — VoiceLock

A light, human-readable map so a fresh session can navigate without re-reading
everything. It is **not** a second source of truth — the code is the truth.
Regenerate it when it drifts.

- Updated: 2026-07-22 after F2. Solid = built (F1 booth + F2 outer lock); dashed = later.

## Architecture (data flow)

```mermaid
flowchart TB
    Mic([Microphone])

    subgraph Window["Desktop window — Booth UI"]
        Booth["Booth — record / enroll / unlock (F1–F2)"]
        Viz["Visualizer — live levels (F1)"]
    end

    Bridge{{"UI ↔ engine bridge (F1–F2)"}}

    subgraph Engine["Engine"]
        Capture["Audio capture (F1)"]
        Playback["Playback (F1)"]
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
    Booth <--> Bridge <--> Playback
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
    class Voiceprint,Challenge,Fuzzy,Inner planned
```

## Shape
- `.harness/` — governing harness (roadmap, specs, conventions).
- `design/` — mock UI reference (`voicelock-mock.html`); not final chrome.
- `src/voicelock/` — app engine (capture, playback, vault, pywebview host).
- `src/voicelock/ui/` — HTML/CSS/JS booth (offline).
- `tests/` — pytest suite (fake streams / temp vault paths; no real mic in Gate).

## Key modules
- `src/voicelock/capture.py` — 16 kHz mono capture, levels, 30s soft cap, mic error
- `src/voicelock/playback.py` — play / stop PCM buffers
- `src/voicelock/vault.py` — outer lock (Argon2id + SecretBox), VLCK file format
- `src/voicelock/app.py` — pywebview host + JS bridge (`BoothApi` record/enroll/unlock)
- `src/voicelock/ui/index.html` — Booth chrome + Record/Stop/Play + Enroll/Unlock
- `src/voicelock/__main__.py` — `python -m voicelock`

## Where things live
- Entry point(s): `uv run voicelock`
- Vault path: `~/.voicelock/vault.vl`
- Tests: `tests/` via `uv run pytest`
- Config: `pyproject.toml` + `uv.lock` (includes `pynacl`)
- Lint: `uv run ruff check .`

## Conventions
See `constitution/topics/conventions.md`.

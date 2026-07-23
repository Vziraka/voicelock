# Codebase Map — VoiceLock

A light, human-readable map so a fresh session can navigate without re-reading
everything. It is **not** a second source of truth — the code is the truth.
Regenerate it when it drifts.

- Updated: 2026-07-23 after F3. Solid = built (F1 booth + F2 outer lock + F3
  voiceprint-on-screen diagnostic); dashed = planned (F4–F9). F3 added the
  offline ECAPA voiceprint engine + Booth match meter (Set reference / Reset);
  it is a diagnostic only — NOT wired into the lock (that is F4).

## Architecture (data flow)

```mermaid
flowchart TB
    Mic([Microphone])
    Cam([Webcam])

    subgraph Window["Desktop window — Booth UI"]
        Booth["Booth — record / enroll / unlock (F1–F2)"]
        Viz["Visualizer — live audio levels (F1)"]
        FaceView["FaceView — camera + landmarks (F5)"]
    end

    Bridge{{"UI ↔ engine bridge (F1)"}}

    subgraph Engine["Engine"]
        Capture["Audio capture (F1)"]
        Playback["Playback (F1)"]
        FaceDetect["Face detect + landmarks (F5)"]
        Voiceprint["Voiceprint — voice identity (F3)"]
        Faceprint["Faceprint — face identity (F6)"]
        FuzzyV["Fuzzy reconcile — voice (F4)"]
        FuzzyF["Fuzzy reconcile — face (F7)"]
        Outer["Outer lock — passphrase → AEAD (F2)"]
        Middle["Middle lock — voice codeword → AEAD (F4)"]
        Inner["Inner lock — face codeword → AEAD (F7)"]
        Liveness["Liveness — challenge + lip-sync (F8)"]
    end

    Vault[("Profile vault on disk (F2)")]

    Mic --> Viz
    Mic --> Capture
    Cam --> FaceView
    Cam --> FaceDetect
    Booth <--> Bridge <--> Capture
    Booth <--> Bridge <--> Playback
    Booth <--> Bridge <--> FaceDetect
    Booth -- "passphrase" --> Outer
    Capture --> Voiceprint
    FaceDetect --> Faceprint
    Capture -- "audio envelope" --> Liveness
    FaceDetect -- "lip landmarks" --> Liveness
    Voiceprint --> FuzzyV -- "voice key" --> Middle
    Faceprint --> FuzzyF -- "face key" --> Inner
    FuzzyV <-. "helper data" .-> Vault
    FuzzyF <-. "helper data" .-> Vault
    Outer --> Vault
    Middle --> Vault
    Inner --> Vault
    Liveness -- "gate before unlock" --> Inner

    classDef planned stroke-dasharray:6 4
    class FaceView,FaceDetect,Faceprint,FuzzyV,FuzzyF,Middle,Inner,Liveness planned
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
- `src/voicelock/voiceprint.py` — offline ECAPA speaker embedding (F3): `embed`,
  `set_reference` (3-take L2-avg, injectable path), `cosine_distance`, `compare`
  → (distance, band) with pinned `ACCEPT/REJECT_CUTOFF`
- `src/voicelock/models/ecapa/` — vendored SpeechBrain ECAPA (Apache-2.0), loaded
  offline (`HF_HUB_OFFLINE`, `pretrained_path` override + `LocalStrategy.NO_LINK`)
- `src/voicelock/app.py` — pywebview host + JS bridge (`BoothApi`
  record/enroll/unlock + F3 `set_reference`/`compare`/`reset_reference`)
- `src/voicelock/ui/index.html` — Booth chrome + Record/Stop/Play + Enroll/Unlock
  + F3 voiceprint panel (3-band meter, Set reference, Reset)
- `src/voicelock/__main__.py` — `python -m voicelock`

## Where things live
- Entry point(s): `uv run voicelock`
- Vault path: `~/.voicelock/vault.vl`
- Voiceprint reference: `~/.voicelock/voiceprint.ref` (F3, plaintext sibling, not the vault)
- Tests: `tests/` via `uv run pytest`
- Config: `pyproject.toml` + `uv.lock` (includes `pynacl`)
- Lint: `uv run ruff check .`

## Conventions
See `constitution/topics/conventions.md`.

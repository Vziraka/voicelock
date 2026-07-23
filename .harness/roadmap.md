# Roadmap — VoiceLock (multi-factor biometric profile vault)

Produced by the `design` skill. The durable, above-spec plan: what we're building
and in what order. Each feature below becomes its own `/spec` when you reach it.

> **Name note:** "VoiceLock" is now a misnomer — the product uses voice **and**
> face **and** lip-liveness. The codename / package (`voicelock`, `uv run
> voicelock`, `~/.voicelock/`) is kept for now to avoid churn; a rename is an
> open nice-to-have (see Out of scope).

## The idea

A local, offline learning project with a full end-to-end demo. Enroll with a
name, a typed passphrase, your **voice**, and your **face**. To unlock, you type
the passphrase and then — in **one webcam+mic recording** — speak a random
challenge phrase to the camera. That single clip proves three things at once:
your voice matches (it's you), your face matches (it's you), and your lips move
in time with the words (you're a real, live person speaking right now, not a
photo or a replayed clip). Success signal: the real user gets in; a wrong
passphrase, a wrong voice, a wrong face, and a replay each fail **visibly and
distinctly**.

In the user's words: *"a video recording of your face while you talk that
verifies both [voice and face] — and on top of that verifies the person in the
video is moving their lips, to confirm they're an actual [live] person."*

## Intent & honest framing

Learning-first, demo-complete — **not** a shippable security product. In scope:
speaker match (voice embedding distance), face match (face embedding distance),
and challenge-response liveness via **audio-visual lip-sync**. Explicitly out:
strong deepfake / live-clone resistance. Lip-sync liveness defeats *simple*
replay — an audio-only clip, a still photo, a silent face video — but a
sophisticated video where lips already match the audio is **not** claimed to be
stopped. Any weak "robotic/flat" heuristics stay optional and are never labeled
as proof.

## Approach

**Approach B′ — three stacked locks** (an evolution of the original two-lock
Approach B; see `adr/0002-three-nested-locks.md`). An encrypted box inside an
encrypted box inside an encrypted box:

- **Outer lock** — key from the **typed passphrase** (something you know). *(built, F2)*
- **Middle lock** — key from the **voiceprint** via fuzzy reconcile (how you sound).
- **Inner lock** — key from the **faceprint** via fuzzy reconcile (how you look).

Unlock peels all three, so each impostor class fails an **independent** factor and
the cause stays nameable. Chosen over fusing the two biometrics into one key
(which would blur which factor failed — the same reason the original design
rejected a single combined key) and over using face/voice as mere match-gates
(which wouldn't cryptographically seal the bytes).

Locked for all features (specific libraries chosen later via TECH-PICK):

- One local, offline desktop app — no cloud, no network at runtime.
- Always **all factors** at unlock: passphrase + voice + face + live lip-sync challenge.
- Identity = biometric **match** (embedding distance), for both voice and face —
  not deepfake detection.
- Liveness for the full demo = challenge-response with **audio-visual lip-sync**
  (defeats simple replay).
- The typed passphrase is the one **exact secret**; voice, face, and challenge
  are fuzzy-matched and are **not** secrets.

## Architecture (intended)

Boxes = components, arrows = data flow. Tagged with the feature (F1–F9) that
builds them. Solid = built; dashed = planned. High-level on purpose.

```mermaid
flowchart TB
    Mic([Microphone])
    Cam([Webcam])

    subgraph Window["Desktop window — Booth UI"]
        Booth["Booth — modes, challenge,<br/>typed passphrase (F1–F2)"]
        Viz["Visualizer — live audio levels (F1)"]
        FaceView["FaceView — camera preview<br/>+ landmarks (F5)"]
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

    Vault[("Profile vault on disk —<br/>nested ciphertext + helper data (F2)")]

    Mic --> Viz
    Mic --> Capture
    Cam --> FaceView
    Cam --> FaceDetect

    Booth <--> Bridge <--> Capture
    Booth <--> Bridge <--> Playback
    Booth <--> Bridge <--> FaceDetect
    Booth -- "typed passphrase" --> Outer

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
    class FaceView,FaceDetect,Voiceprint,Faceprint,FuzzyV,FuzzyF,Middle,Inner,Liveness planned
```

## Features (vertical slices, in build order)

Each is a thin end-to-end slice, demoable on its own. Build order is **Order A**:
voice becomes a complete working lock first, then face, then liveness, then
polish. `blocked-by` names hard dependencies; the list order is the chosen build
sequence. The full success arc (all impostor classes) becomes reachable at
**F8**; **F9** makes the demo reliable and presentable.

- [x] **F1 — The recording booth** · blocked-by: none
  App window: press to record, live visualizer reacts, audio captures and plays back.
  *Demo:* speak → visualizer moves → captured audio plays back. (No auth yet.)

- [x] **F2 — Passphrase-only vault (outer lock)** · blocked-by: F1
  Enroll name + typed passphrase; passphrase derives the outer key and seals a
  profile vault on disk. Unlock with the passphrase.
  *Demo:* enroll → on-disk file is sealed → right passphrase opens → **wrong
  passphrase REJECT**.

- [ ] **F3 — Voiceprint on screen** · blocked-by: F1
  Compute the voiceprint and show live match distance vs a stored sample — not
  wired into the lock yet.
  *Demo:* same person → close / accept-colored; different person → far / reject-colored.

- [ ] **F4 — Voice as the middle lock (stacked)** · blocked-by: F2, F3
  Fuzzy-reconcile the voiceprint into a stable key; wrap the outer-sealed box
  inside the voice lock. Unlock needs passphrase **and** voice.
  *Demo:* right voice + passphrase → in; wrong passphrase → REJECT (outer);
  **different person's voice → REJECT** (middle).

- [ ] **F5 — Camera booth** · blocked-by: F1 · **TECH-PICK: offline face detect/landmark/embedding stack**
  Add a live webcam feed to the Booth with face detection + facial landmarks
  drawn on the preview. The visual analog of F1; prefactor for all face work.
  *Demo:* your face appears in the preview → a box/landmarks track it live.

- [ ] **F6 — Faceprint on screen** · blocked-by: F5
  Compute the faceprint (face embedding) and show live match distance vs a stored
  sample — not wired into the lock yet. The visual analog of F3.
  *Demo:* same face → close / accept-colored; different face → far / reject-colored.

- [ ] **F7 — Face as the inner lock (innermost)** · blocked-by: F4, F6
  Fuzzy-reconcile the faceprint into a stable key; wrap the voice-sealed box
  inside the face lock. Unlock now peels passphrase → voice → face.
  *Demo:* wrong passphrase / wrong voice / **wrong face** each REJECT distinctly.

- [ ] **F8 — Lip-sync liveness (challenge-response)** · blocked-by: F7
  Each unlock shows a fresh random phrase; in one webcam+mic capture the user
  speaks it. Verify the spoken words match the challenge, the voiceprint matches,
  the faceprint matches, **and** the lips move in sync with the audio.
  *Demo:* **replay a recording / hold up a photo / play audio at a muted video →
  REJECT.** Full enroll → auth → four-impostor arc is now reachable.

- [ ] **F9 — Demo reliability** · blocked-by: F7
  Enrollment-quality gate (voice **and** face), visible tolerance knobs, clear
  per-rejection reason (wrong passphrase / voice / face / liveness).
  *Demo:* bad enrollment refused; dial tolerance; each reject names its cause.

### Parked (not in the must-build path)

- **F10 — Weak robotic/flat heuristic** · blocked-by: F8
  Optional exploration only; never claimed as deepfake-proof. Revisit after F9
  if you still want it.

- **F11 — Manage enrollment from inside the vault** · blocked-by: F7
  Once unlocked, let the user change the passphrase and re-enroll voice/face
  from inside their profile (edit/reset any of the three factors). Profile
  management — only meaningful after all three factors are real locks (post-F7),
  likely bundled with or after F9. Human-requested 2026-07-23; not yet specced,
  parked here so it isn't lost.

## Out of scope

- Not a real security product — no FAR/FRR guarantees, no certification.
- No claim of stopping real-time voice cloning or synced deepfake video.
- No cloud, network, multi-device sync, or online accounts.
- No account recovery — lose the passphrase, voice, or face match → vault stays sealed.
- No mobile or browser product; no multi-user/admin management.
- No hardening against host malware, memory forensics, or side channels.
- Strong anti-deepfake models / eval pipelines (see parked F10 for a weak heuristic only).
- **Product rename** away from "VoiceLock" — deferred nice-to-have; not built until a human decides the new name (would touch package, entry point, and vault path).

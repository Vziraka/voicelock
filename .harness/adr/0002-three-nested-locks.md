# Three nested locks (Approach B′) — supersedes ADR 0001

The learning demo grows from two factors to three: passphrase, voice, **and**
face, with audio-visual lip-sync as the liveness check. We keep the stacked-lock
shape and add a layer rather than fusing biometrics.

The vault is sealed by three nested AEAD locks, outermost to innermost:

1. **Outer** — key derived from the typed passphrase (something you know). *Built (F2).*
2. **Middle** — key derived from the voiceprint via fuzzy reconcile (how you sound).
3. **Inner** — key derived from the faceprint via fuzzy reconcile (how you look).

Unlock peels all three. A wrong factor fails its **own** peel, so the demo can
name the cause (wrong passphrase vs wrong voice vs wrong face). At unlock a single
webcam+mic capture ("AV capture") also feeds the liveness gate: the spoken words
must match a random challenge, and the lips must move in time with the audio —
defeating a still photo, an audio-only replay, or a muted video.

## Why not the alternatives
- **Fuse voice + face into one inner key.** Rejected: a combined key blurs which
  factor failed — the same reason ADR 0001 rejected a single combined key. Nesting
  keeps failures independent and nameable.
- **Face (or voice) as a match-gate only.** Rejected: a gate wouldn't
  cryptographically seal the bytes; each identity factor should truly seal a layer.
- **Replace voice with face+lips.** Rejected: throws away the voice work and gives
  a weaker multi-factor story than stacking all three.

## Honest limits
Identity is embedding **match** (voice and face), not deepfake detection. Lip-sync
liveness defeats *simple* replay only; a sophisticated synced deepfake video is
explicitly **not** claimed to be stopped. Not a shippable security product.

## Status
Accepted 2026-07-22 (design). Supersedes `0001-two-stacked-locks.md`, which stays
as history. Implemented across roadmap features F3 (voiceprint), F4 (voice/middle
lock), F5–F7 (camera, faceprint, face/inner lock), F8 (lip-sync liveness).

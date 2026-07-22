# VoiceLock — Shared Language

The project glossary. Read it before writing code so names stay consistent and
prose stays tight. Only project-specific terms — no general programming concepts.
Be opinionated: pick one word per concept and list the rivals under _Avoid_.

Seeded by `design` (2026-07-22).

## Language

**Vault**: the encrypted on-disk file holding one user's profile, sealed by the
two stacked locks.
_Avoid:_ database, store, container

**Outer lock**: the passphrase-derived encryption layer wrapping the vault.
_Avoid:_ password layer, first factor

**Inner lock**: the voice-derived encryption layer inside the outer lock, keyed
by the reconciled voiceprint codeword.
_Avoid:_ biometric layer, second factor

**Voiceprint**: the identity signal computed from speech (used for match distance
and, later, the inner key) — not a deepfake detector.
_Avoid:_ voice signature, voice ID, template

**Helper data**: the non-secret hint stored beside the vault that reconciles a
fresh, slightly different voiceprint back to the enrollment codeword.
_Avoid:_ sketch (in prose), recovery data

**Enroll**: creating a profile — name + passphrase + voice sample.
_Avoid:_ register, sign up

**Booth**: the main UI where speaking / unlocking happens.
_Avoid:_ recorder screen, main panel

**Challenge**: the random per-attempt prompt the user must speak (defeats replay).
_Avoid:_ prompt (ambiguous), captcha

**Liveness**: proving the attempt is fresh speech for *this* challenge — here,
challenge-response. Not deepfake proof.
_Avoid:_ anti-spoofing (goal vs mechanism)

**Impostor**: a failed unlock class in the demo arc — wrong passphrase, wrong
voice, or replay.
_Avoid:_ attacker, intruder

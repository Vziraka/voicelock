# VoiceLock — Shared Language

The project glossary. Read it before writing code so names stay consistent and
prose stays tight. Only project-specific terms — no general programming concepts.
Be opinionated: pick one word per concept and list the rivals under _Avoid_.

Seeded by `design` (2026-07-22); extended by `design` for the three-factor
pivot (voice + face + lips) (2026-07-22).

## Language

**Vault**: the encrypted on-disk file holding one user's profile, sealed by the
two stacked locks.
_Avoid:_ database, store, container

**Outer lock**: the passphrase-derived encryption layer wrapping the vault
(the outermost of three stacked locks).
_Avoid:_ password layer, first factor

**Middle lock**: the voice-derived encryption layer inside the outer lock, keyed
by the reconciled voiceprint codeword.
_Avoid:_ voice layer, second factor

**Inner lock**: the face-derived encryption layer inside the middle lock (the
innermost lock), keyed by the reconciled faceprint codeword.
_Avoid:_ biometric layer, third factor, face gate

**Voiceprint**: the identity signal computed from speech (used for match distance
and the middle-lock key) — not a deepfake detector.
_Avoid:_ voice signature, voice ID, template

**Faceprint**: the identity signal computed from a face image (a face embedding;
used for match distance and the inner-lock key) — a face **match**, not a
deepfake/spoof detector.
_Avoid:_ face signature, face ID, face template, faceprint hash

**FaceView**: the Booth's live camera preview with face detection + landmarks
drawn on it — the visual analog of the audio Visualizer.
_Avoid:_ camera panel, video feed, webcam widget

**Helper data**: the non-secret hint stored beside the vault that reconciles a
fresh, slightly different voiceprint back to the enrollment codeword.
_Avoid:_ sketch (in prose), recovery data

**Enroll**: creating a profile — name + passphrase + voice sample.
_Avoid:_ register, sign up

**Booth**: the main UI where speaking / unlocking happens.
_Avoid:_ recorder screen, main panel

**Challenge**: the random per-attempt phrase the user must speak to the camera
(defeats replay of a fixed clip).
_Avoid:_ prompt (ambiguous), captcha

**Liveness**: proving the attempt is a real person speaking *this* challenge
right now — here, audio-visual **lip-sync** (the lips move in time with the
spoken audio). Not deepfake proof.
_Avoid:_ anti-spoofing (goal vs mechanism)

**Lip-sync**: the liveness mechanism — correlating mouth/lip movement (from face
landmarks) with the audio envelope over the challenge, so a still photo, an
audio-only replay, or a muted video fails.
_Avoid:_ lip reading (a different, harder thing), mouth detection

**AV capture**: the single webcam+mic recording taken at unlock, pulled apart
into voice identity, face identity, spoken words, and lip-sync.
_Avoid:_ video clip, recording (ambiguous with the F1 audio take)

**Impostor**: a failed unlock class in the demo arc — wrong passphrase, wrong
voice, wrong face, or replay.
_Avoid:_ attacker, intruder

# Voiceprint fixtures

Fixed audio for the deterministic F3 voiceprint tests. Derived offline from the
SpeechBrain `spkrec-ecapa-voxceleb` model repo's own example clips (Apache-2.0,
rev `0f99f2d`) — the same source as the vendored model:

- `example1.wav` → speaker **A** (VoxCeleb). Split into `speakerA_take1/2/3.wav`
  (the three "Set reference" takes) and a central window `speakerA_live.wav`
  (the same-speaker live probe).
- `example2.flac` → speaker **B** → `speakerB.wav` (the different-speaker probe).
- `too_short.wav` — the first 0.15 s of speaker A, below `MIN_SPEECH_SECONDS`, to
  exercise the "need more audio" edge.

All files are mono 16 kHz PCM_16 WAV, committed via a `.gitignore` exception.

Honest caveat: because the model repo ships only one clip per speaker, the
same-speaker live probe overlaps the reference takes (it is a window of the same
recording). That is acceptable for an F3 diagnostic fixture — it proves the
engine's distance/band math separates same from different — and is not a claim
of cross-session generalization (that is F9's territory, and out of F3 scope).

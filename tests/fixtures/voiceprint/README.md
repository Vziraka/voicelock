# Voiceprint fixtures

Fixed audio for the deterministic F3 voiceprint tests and the F4 middle-lock
tests. Derived offline from the SpeechBrain `spkrec-ecapa-voxceleb` model repo's
own example clips (Apache-2.0, rev `0f99f2d`) — the same source as the vendored
model:

- `example1.wav` → speaker **A** (VoxCeleb). Split into `speakerA_take1/2/3.wav`
  (the three F3 "Set reference" takes) and a central window `speakerA_live.wav`
  (the same-speaker live probe).
- `example2.flac` → speaker **B** → `speakerB.wav` (the different-speaker probe).
- `too_short.wav` — the first 0.15 s of speaker A, below `MIN_SPEECH_SECONDS`, to
  exercise the "need more audio" edge.
- `speakerA_enroll1..5.wav` — the **F4** 5-take enrollment set (see below).

All files are mono 16 kHz PCM_16 WAV, committed via a `.gitignore` exception.

Honest caveat: because the model repo ships only one clip per speaker, the
same-speaker live probe overlaps the reference takes (it is a window of the same
recording). That is acceptable for an F3 diagnostic fixture — it proves the
engine's distance/band math separates same from different — and is not a claim
of cross-session generalization (that is F9's territory, and out of F3 scope).

## F4 enrollment set (`speakerA_enroll1..5.wav`)

F4 enrolls a **5-sentence averaged capture** (spec §4), so it needs five takes
where F3 had three. The five are cut from the SAME committed speaker-A audio:
`speakerA_take1/2/3.wav` are consecutive thirds of `example1.wav`, so they are
concatenated back into the original **52 173 samples (3.261 s)** and five equal
windows are taken at a fixed hop. The F3 fixtures are untouched — `test_voiceprint.py`
and `test_booth_api.py` still use them as-is.

Pinned geometry: **1.600 s windows (25 600 samples), hop 0.415 s (6 643 samples)**,
starting at 0.000 / 0.415 / 0.830 / 1.246 / 1.661 s. Adjacent windows overlap 74 %;
**windows 1 and 5 share no audio at all**. Every take clears `MIN_SPEECH_SECONDS`
(0.4 s) by 4× and sits ~40× over `MIN_RMS` (per-take RMS 0.019–0.025).

### Why 1.6 s

The source is only 3.261 s, so window length trades directly against how much the
five "takes" overlap each other. Measured on the vendored ECAPA model (cosine
distance; BER = raw 192-dim sign disagreement vs the 5-take mean):

| window | hop | adj. overlap | take1↔take5 overlap | cross-take pairwise max / mean | sign-unanimous bits | BER vs live | BER vs B |
|---|---|---|---|---|---|---|---|
| 1.2 s | 0.515 s | 57 % | **0 %** | 0.747 / 0.453 | 64/192 | 13 % | 46 % |
| **1.6 s** | **0.415 s** | **74 %** | **0 %** | **0.624 / 0.306** | **98/192** | **8 %** | **43 %** |
| 2.0 s | 0.315 s | 84 % | 37 % | 0.350 / 0.178 | 128/192 | 8 % | 44 % |
| 2.4 s | 0.215 s | 91 % | 64 % | 0.219 / 0.118 | 137/192 | 8 % | 43 % |

1.6 s is the **longest** window at which takes 1 and 5 still share zero audio, so
the set keeps one genuinely independent pair. Everything above 1.6 s buys its
extra stability by making the five takes literally the same audio — the
cross-take unanimity filter (spec §4) would then be measuring the cut, not the
speaker. Below 1.6 s the takes drift so far apart (pairwise max 0.747, i.e. two
takes of the SAME speaker further apart than F3's 0.65 reject cutoff) that the
unanimity filter is starved. Genuine BER plateaus at 8 % from 1.6 s on, so
nothing is gained by going longer.

### Measured separation (vendored ECAPA, at the pinned 1.6 s)

- 5-take mean → `speakerA_live.wav` (same speaker): **0.0583** — well inside
  `ACCEPT_CUTOFF` 0.45.
- 5-take mean → `speakerB.wav` (impostor): **0.8451** — well past `REJECT_CUTOFF` 0.65.
- Per-take distance to the 5-take mean: 0.2695 / 0.0772 / 0.0619 / 0.0891 / 0.1576
  (take 1 is the outlier — it is the only window with no audio in common with take 5).
- Cross-take pairwise distance: max 0.6241, mean 0.3062.
- Raw 192-dim sign bits: 98/192 (51 %) unanimous across all five takes; genuine
  sign disagreement 7.8 %, impostor 43.2 %.

Numbers for F4 Task 2 (`middlelock.py` tolerance pinning): the raw 8 % genuine /
43 % impostor sign-bit split is the starting point the LSH expansion + reliability
mask + repetition ECC have to widen. Note the research's ~25 % raw-BER figure was
measured on shorter F3 takes; these longer windows do better, but the bits are
still correlated (only 192 real dimensions), so binomial estimates that assume
independent flips will be optimistic.

### Fixture-vs-reality caveat (spec §4, F4)

These takes are **1.6 s of a single 3.3 s recording**, where a real F4 enrollment
reads five separate 3–5 s sentences. Two consequences, in opposite directions:

- **Harder than reality:** each take is shorter and phonetically thinner than a
  real sentence, so the per-take embedding is noisier.
- **Easier than reality:** the takes overlap each other (74 % adjacent) and the
  same-speaker probe overlaps the enrollment audio, so this set cannot prove
  cross-session generalization — a different mic, room or day is not represented.

So the fixtures prove the *math* separates same from different; they do **not**
prove the lock works live. That gap is what spec §5's **required manual demo**
covers. If F4 Task 2 cannot separate genuine from impostor here, question these
fixtures first (spec §4's escalation order) — but never widen the correction
radius to force a pass.

# Live code defects surfaced by the 2026-07-26 calibration run

Found by re-verifying archived F1–F3 tasks (see
`memory/verdicts/2026-07-26-CALIBRATION-RUN.md`). **Not built** — recorded here
because curate is a gardening pass and shipped-code fixes need their own
spec/plan. Each was verified independently, not taken on an agent's word.

Roadmap-wise these fit **F9 — Demo reliability**, except the dependency one,
which is arguably urgent enough to stand alone.

## 1. Self-deadlock in the capture callback (F1, latent, live today)

`src/voicelock/capture.py:110-121` — `_on_audio` is the PortAudio stream
callback. On the 30-second auto-stop path it calls `self._close_stream()`, which
runs `stream.stop()` then `stream.close()`. `Pa_StopStream` blocks until the
callback returns, so the callback waits on itself. The comment on the line
immediately above says this is unsafe and claims the code marks for stop via
`pump`/`stop` instead — the code does the opposite of its own comment.

- **Trigger:** a live recording that reaches `max_seconds` (30 s). No manual demo
  has run that long, which is why it has never been seen.
- **Not caught because:** `tests/test_capture.py`'s `FakeStream` never invokes the
  callback it is handed — the word `callback` does not appear in the file. Every
  test drives `pump()` instead, so `_on_audio` has zero coverage.
- **Fix direction:** raise `sd.CallbackStop` from the callback (sounddevice's
  supported in-callback stop), or set a flag the main thread acts on. Then make
  the comment match the code, and have `FakeStream` deliver frames through the
  callback so the path is actually exercised.

## 2. Undeclared dependency: `soundfile` (F3, live today)

`src/voicelock/voiceprint.py:150` does `import soundfile as sf` inside
`load_wav`, but `soundfile` is **not** in `pyproject.toml`. It reaches the
environment only as a SpeechBrain transitive (`uv.lock` line ~1372).

- **Risk:** if SpeechBrain drops or renames that transitive, fixture loading — and
  therefore the whole voiceprint test suite — breaks with no local change.
- **Fix direction:** either decode via the already-approved `torchaudio`, or
  declare `soundfile` explicitly with `uv add`. It is an addition to an
  already-approved stack rather than a new capability, so it likely needs a
  declaration rather than a fresh TECH-PICK — but that is the human's call.

## 3. Speculative resample / multichannel surface (F3, live today, cosmetic)

`src/voicelock/voiceprint.py` — `_resample()` (`:206-211`) and its only two call
sites (`:71-72`, `:156-157`), the `data.ndim > 1` branch (`:154-155`), and the
`sample_rate` parameters on `embed` (`:65`) and `compare` (`:116`) are all
unreachable in this repo: `capture.py` fixes the only audio source at 16 kHz
mono and every fixture is 16 kHz mono.

- Direct hit on the earned guardrail added 2026-07-26 ("never add a helper,
  method, or branch that no caller and no test exercises"), though the code
  predates the rule by four days.
- **Fix direction:** ~12-line deletion; reintroduce in whichever task genuinely
  needs non-16 kHz input.
- **Caution:** `voiceprint.py` is F3's engine and spec §4 of F4 froze it as "the
  identity source, unchanged". Touching it needs a spec that says so.

## 4. Fixture caveat worth propagating (F3, documentation)

`ACCEPT_CUTOFF = 0.45` was calibrated against a same-speaker probe
(`speakerA_live.wav`) that is a **window of the same recording** as the reference
takes — recording self-similarity, not cross-utterance validation. This is
already disclosed in `tests/fixtures/voiceprint/README.md`, but the number itself
has since been inherited by F4. Worth a line beside the constant so nobody in
F9 treats 0.45 as empirically cross-validated.

## Already fixed, no action needed

The calibration run also flagged a broken overwrite-confirm handler in F2-T3
(the confirm button zeroed the flag it was meant to set). A later F2 task
rewrote that handler; at HEAD it correctly sets `pendingOverwrite = true` and
re-fires enroll. Recorded only so the finding is not re-discovered.

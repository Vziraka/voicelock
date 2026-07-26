# Spec: F4.5 — Capture callback + test-harness hygiene

Feature: Feature 4.5 from `roadmap.md`

## 0. Approval gate

- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
  the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns zero
  hits in this file)
- [x] Approved by human

- **Mode:** Mode 3 (Spec-to-done). Set by the human 2026-07-26. The one
  dependency this feature touches was locked by a TECH-PICK + human approval
  BEFORE drafting (`memory/decisions.md`, 2026-07-26), so Mode 3's autonomy is
  bounded to an already-approved design.

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks it.

## 1. Outcome

Close two live defects and one manifest gap found by the 2026-07-26 calibration
run (`.out-of-scope/2026-07-26-calibration-findings.md`, items 1 and 2), **before
F5 inherits the second one**.

1. **The capture callback no longer deadlocks against itself.**
   `src/voicelock/capture.py`'s `_on_audio` is the PortAudio stream callback. On
   the 30-second auto-stop path it calls `_close_stream()`, which runs
   `stream.stop()`; `Pa_StopStream` blocks until the callback returns, so the
   callback waits on itself. The comment immediately above that line says the
   code marks for stop via `pump`/`stop` instead — **the code does the opposite
   of its own comment.** After this feature, a recording that reaches
   `max_seconds` stops cleanly and the Booth stays responsive.

2. **The tests drive the real callback path.** `tests/test_capture.py`'s
   `FakeStream` never invokes the callback it is handed — the word `callback`
   does not appear in the file — so every test drives `pump()` and `_on_audio`
   has **zero** coverage. That is why defect 1 shipped. After this feature the
   fake delivers frames through the real callback, and the deadlock is a **fast
   test failure rather than a hung suite**.

3. **`soundfile` is declared.** `src/voicelock/voiceprint.py:150` imports it
   inside `load_wav`, but it reaches the environment only as a SpeechBrain
   transitive (`uv.lock` line 1372). If SpeechBrain drops or renames that
   transitive, fixture loading — and therefore the entire voiceprint and
   middlelock suite — breaks with no local change.

**Why this runs before F5, not inside F9** (where the calibration findings
originally filed items 1 and 2): F5 adds a camera stream with its own frame
callback, and would copy today's fake-stream pattern — a fake that never invokes
the callback it is handed. Fixing the pattern once, now, is cheaper than fixing
two copies of it later. This is the feature's stated purpose, not a side effect.

Demo: start a recording, leave it running past 30 seconds, and the app
auto-stops with the audio intact instead of freezing.

## 2. Grilling record — ambiguity scan

**Status: CLEAR** — every category resolved; zero clarification markers remain
(2026-07-26).

| Category                           | Verdict | Resolved by |
| ---------------------------------- | ------- | ----------- |
| Functional scope & behavior        | Clear   | Three items, listed in §1 and bounded in §3. The callback raises `sd.CallbackStop` and does no teardown; the existing `pump()` cap check performs it (§4). |
| Domain & data model                | Clear   | No change — no new state, no format change, no vault or crypto surface touched. |
| Interaction & UX flow              | Clear   | No intended UX change. The 30 s auto-stop already notifies the UI via `app.py`'s `onCaptureEnded`; that path is preserved. The visible difference is that the app stops freezing. |
| Non-functional (perf, security)    | Clear   | Offline-only unaffected; no crypto surface. Callback tests add negligible runtime. Pump-teardown latency stays ≤ 50 ms (`app.py:358`). |
| Integration & dependencies         | Clear   | One dependency, `soundfile`, declared as a MAIN dep — TECH-PICK run and human-approved 2026-07-26 (`memory/decisions.md`). `torchaudio` was evaluated and ruled out on evidence (§4). |
| Edge cases & failure modes         | Clear   | Cap reached with no pump running; `stop()` on an already-stopped stream; a take shorter than the cap; mic-error path unchanged (§4). |
| Completion signals                 | Clear   | §5 pinned: callback-path tests + a declared-dependency assertion + a source assertion that the defect is gone, plus the required human-attested 31-second live check. |
| Terminology (matches `CONTEXT.md`) | Clear   | No new terms. Booth is the only glossary term used, unchanged. |

**Mode 3 "if every gate passed but it were still wrong" (RESOLVED 2026-07-26):**
the fake-stream tests prove the *logic* of the fix, but a fake that never
deadlocks proves nothing about whether raising `sd.CallbackStop` from a Python
callback actually unwinds and stops the stream cleanly across sounddevice's CFFI
boundary on this machine. The bug being fixed is **defined** by only appearing
live. The human chose a **required, human-attested 31-second live check** (§5) —
a required check, not accepted risk. This follows the F1–F4 precedent, where
every feature made its live Booth check required.

## 3. Non-goals

- **No new capture behavior.** The 30-second soft cap, the level frames, the
  mic-error path, `toggle()`, and the returned PCM buffer all keep today's
  semantics. This feature changes *how* the cap is honored, not *what* it does.
- **No UI change.** `src/voicelock/ui/index.html` is not touched. `app.py`'s
  pump loop and `onCaptureEnded` notification stay as they are.
- **No crypto, vault, voiceprint, or middlelock change.** F4's measured
  constants (`CORRECTION_RADIUS = 110`, `ACCEPT_CUTOFF = 0.45`) must remain
  valid, which is precisely why the approved `soundfile` option is the one that
  changes **no** decode code.
- **Calibration finding 3 is explicitly OUT.** `voiceprint.py`'s `_resample()`,
  its two call sites, the `data.ndim > 1` branch, and the `sample_rate`
  parameters on `embed`/`compare` are dead surface and a live hit on the earned
  guardrail — but declaring `soundfile` is a `pyproject.toml` edit, so this
  feature is never "in there". Touching `voiceprint.py` would put F3/F4's
  measured cutoffs at risk for no gain. It stays filed in
  `.out-of-scope/2026-07-26-calibration-findings.md` for F9.
- **Calibration finding 4 is out** (a documentation caveat beside
  `ACCEPT_CUTOFF`) — same reason: it edits `voiceprint.py`. Filed for F9.
- **No camera, face, or F5 work of any kind.** This feature exists so F5 starts
  from a sound pattern; it does not start F5.
- **No broader test refactor.** The pump-driven tests stay. `pump()` is a real
  production path — `app.py:341-358` polls it every 50 ms — so it keeps its
  coverage. This feature *adds* the missing callback coverage; it does not
  replace one path's tests with the other's.
- Out-of-scope discoveries during build (Mode 3 default): record in
  `.out-of-scope/`, never build.

## 4. Constraints

- Honor `constitution/project.md` + conventions: Python 3.11 + uv (no bare pip);
  engine in `src/voicelock/`, tests in `tests/`; **offline-only — no network at
  runtime**; snake_case; `tests/test_<module>.py`.
- Honor the earned guardrail in `project.md` (2026-07-26): no helper, method, or
  branch that no caller and no test exercises. All three of F4's REJECTs were
  that defect — and this feature's whole subject is untested code, so the bar
  applies with force.

**The callback fix (RESOLVED 2026-07-26):** `_on_audio` must not perform stream
teardown. On reaching `max_seconds` it raises **`sd.CallbackStop`** — the
supported in-callback stop, present in the installed sounddevice 0.5.5
(`sounddevice.py:2289`) — and does nothing else. PortAudio then stops the stream
itself, without the callback waiting on its own return. Engine state converges
through the path that already exists: `pump()`'s cap check
(`capture.py:107-108`) calls `stop()`, which closes the stream and sets `IDLE`,
and `app.py`'s 50 ms pump loop then fires `onCaptureEnded` exactly as it does
today. **No new state, no new flag** — the smallest change that solves it.
The stale comment on `capture.py:117` is corrected to describe what the code
actually does.

Edge cases this must hold under:
- **Cap reached with no pump running.** PortAudio stops delivering, the buffer
  is intact, and the next `stop()` returns it. `CaptureEngine`'s docstring
  already offers pump-or-callback as alternatives; the app always pumps.
- **`stop()` on an already-stopped stream.** `_close_stream` already wraps both
  `stream.stop()` and `stream.close()` in try/except — that stays.
- **A take shorter than the cap** and **the mic-error path** are untouched.

**The test fix (RESOLVED 2026-07-26):** `FakeStream` gains the ability to
deliver frames **through the callback it was handed**, shaped as PortAudio
delivers them (2-D `(frames, channels)`), and it stops delivering once the
callback raises `CallbackStop`. It must also make a re-entrant teardown —
`stop()` or `close()` called from inside the callback — raise immediately.
That last part is not gold-plating: without it, the regression test for this
exact defect would express itself as a **suite that hangs forever** rather than
a test that fails, which is unusable inside a Gate that runs on a runtime
budget. This is the pattern F5's fake camera stream is expected to copy.

**The dependency (RESOLVED 2026-07-26, human-approved TECH-PICK):**
`uv add soundfile` — declared as a **main** dependency in `pyproject.toml`, with
**no code change**. Liveness quoted: 0.14.0 published
`2026-06-06T08:58:47.869Z` (`uv.lock` registry metadata), ~7 weeks old;
adoption evidenced by its being a SpeechBrain requirement; docs current.
**`torchaudio` was evaluated and ruled OUT on evidence** — the calibration note
suggested it as the zero-cost answer, but `torchaudio.load` on the installed
2.11.0 raises `ImportError: TorchCodec is required for load_with_torchcodec`,
so it would add torchcodec, a genuinely new dependency.
(`torchaudio.functional.resample` is unaffected and stays.) Rejected
alternatives and the accepted limit — that this declares a main dependency no
runtime code path currently uses — are recorded in `memory/decisions.md`.
`uv.lock` is regenerated by `uv add`; no other manifest edit.

- Gate standing commands (unchanged): `uv run ruff check .` → exit 0;
  `uv run pytest` → exit 0.
- **No dependency beyond `soundfile`** — anything else needs a fresh TECH-PICK
  and human sign-off.

## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Harness rules find this
section by its NAME ("Verification"). Two parts, both required.

Runtime budget: `uv run pytest` loads torch + the vendored ECAPA model and pays
Argon2id twice per middlelock unlock — F4's final Gate measured **83 passed in
48.15 s**. Whole-suite budget: within the 10-minute default.

Standing (project regression net, from `project.md`), pinned:
- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed — the whole existing
  suite, including all F1–F4 tests, still green)

Feature-specific (proves THIS feature works), pinned:

- `uv run pytest tests/test_capture.py -q` → exit 0; final summary reports 0
  failed. Must cover, using only injectable fakes (no real mic):
  (1) **the callback path carries audio** — frames delivered through the real
  `_on_audio` callback (not `pump`) accumulate into `pcm_buffer()` and emit
  level frames, proving `_on_audio` is exercised at all;
  (2) **no self-teardown** — driving the capture past `max_seconds` through the
  callback does **not** call `stream.stop()` or `stream.close()` from inside the
  callback; the fake raises if it happens, so this defect fails **fast** instead
  of hanging the suite;
  (3) **the supported stop is used** — `sd.CallbackStop` propagates out of
  `_on_audio` at the cap, the fake stops delivering frames, and the engine
  converges to `IDLE` with the captured buffer intact once `pump()`/`stop()`
  runs;
  (4) **the pump path is unregressed** — the existing pump-driven tests
  (start/stop, level frames, mic error, 30 s cap, toggle) still pass, since
  `app.py` polls `pump()` every 50 ms in production.

- `uv run python -c "import inspect; from voicelock.capture import CaptureEngine as C; s = inspect.getsource(C._on_audio); assert '_close_stream' not in s, 'callback still tears down the stream'; assert 'CallbackStop' in s, 'callback does not use the supported stop'"`
  → exit 0. Pins the defect itself: the callback no longer performs teardown and
  does use sounddevice's supported in-callback stop.

- `uv run python -c "import tomllib, pathlib; deps = tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['dependencies']; assert any(d.replace(' ', '').lower().startswith('soundfile') for d in deps), 'soundfile is not a declared dependency'"`
  → exit 0. Pins the manifest gap as closed.

- `uv run python -c "import pathlib; t = pathlib.Path('tests/test_capture.py').read_text(encoding='utf-8'); assert 'callback' in t, 'the capture tests still never mention the callback'"`
  → exit 0. The calibration run's own detection signal, kept as a regression
  tripwire — the finding was literally "the word `callback` does not appear in
  the file".

Proof surface: the highest real surface this feature touches is the live
pywebview Booth driving a real PortAudio stream. The automated tests prove the
fix's logic against injectable fakes; they do **not** prove that
`sd.CallbackStop` unwinds cleanly through sounddevice's CFFI boundary on real
hardware — that gap is covered by the required manual line below (a required
check, not accepted risk).

- **Manual (required for F4.5 done, human-attested):** run `uv run voicelock` →
  press Record → let it run **past 30 seconds without pressing Stop**. The
  recording auto-stops on its own, the window **stays responsive** (buttons
  still react — no freeze), and pressing Play plays back the captured audio.
  Observable: the app survives the exact path that deadlocks at HEAD today.

Out-of-scope discoveries during build (Mode 3 default): record in
`.out-of-scope/`, never build.

---

*Spec-anchored: amendments follow the F2/F3/F4 path — update this file, re-scan
changed sections, human re-checks box 2, re-plan.*

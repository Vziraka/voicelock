# Research — offline STT for F8 challenge-phrase matching

Date: 2026-07-28. Question: which offline, local, Python-installable
speech-to-text option best verifies that a spoken challenge phrase (a few
words, drawn from a small known pool) matches what the user actually said,
in VoiceLock's offline-only desktop app (Python 3.11, already vendors
SpeechBrain ECAPA-TDNN via torch, and MediaPipe + OpenCV SFace)?

Playbook: `formats/source-playbooks/library-evaluation.md` (registry →
repo → docs → community, in that order; last release/commit within ~12
months or FAIL; fit beats fame).

## Candidates checked

### 1. Vosk (`vosk`, alphacep/vosk-api) — Kaldi-based offline ASR

- **PyPI**: latest wheel `0.3.45`, uploaded **2023-06-21T09:19:22Z**
  (PyPI JSON API, `releases["0.3.45"][0].upload_time_iso_8601`). On the
  ~12-month bar, the **wheel alone is stale** — over 3 years old.
- **Repo**: `github.com/alphacep/vosk-api` — most recent commit
  **2026-07-02** (GitHub commits API, `HEAD` of default branch), 26 days
  before this research date. Most recent GitHub *tag* is `v0.3.50`,
  **2024-04-22** (repo tags page) — the C library gets tagged releases
  roughly yearly, but the underlying repo has ongoing commit activity past
  that tag. **Disclosed nuance**: the PyPI package and the repo tell
  different liveness stories; the repo itself is alive, the published
  Python wheel is not fresh. Per the TECH-PICK guardrail this needs a
  human waive-and-disclose if chosen, not a silent pass.
- **License**: Apache-2.0 (PyPI classifier + repo `LICENSE`).
- **Model**: `vosk-model-small-en-us-0.15`, 40 MB, **Apache 2.0**, listed
  directly on `alphacephei.com/vosk/models` (the asset's own distribution
  page, satisfying `project.md`'s per-asset licence rule). A larger
  128 MB `-lgraph` variant exists, also Apache-2.0, with better dynamic
  vocabulary support — not needed here since the small model already
  supports grammar mode (below).
- **Grammar-constrained recognition — direct fit for this use case.**
  Confirmed from the project's own GitHub issues (primary source, the
  maintainers' own API description): `KaldiRecognizer(model, rate,
  grammar_json)` accepts a JSON array of allowed phrases, e.g.
  `'["turn left", "turn right", "[unk]"]'`, and `rec.SetGrammar(...)`
  updates it at runtime. Recognition is then decoded **only** against
  that phrase set — this is a purpose-built fit for "match against a
  small known pool", cheaper and more reliable than transcribing freely
  and fuzzy-matching text afterward. Small models support this; large
  static models do not (irrelevant here — the small model is the
  candidate).
- **Dependencies**: `cffi`, `requests`, `tqdm`, `srt`, `websockets` (PyPI
  metadata) — no torch, no numpy requirement, no conflict risk with F3/F4's
  pinned torch/numpy versions.
- **Adoption**: 624,279 downloads/month (pypistats.org, queried
  2026-07-28) — real, active use despite the stale wheel date.

### 2. faster-whisper (`faster-whisper`, SYSTRAN) — Whisper via CTranslate2

- **PyPI**: `1.2.1`, uploaded **2025-10-31T11:35:47Z** — inside the
  12-month bar.
- **Repo**: last commit **2025-11-19** (GitHub commits API) — inside the
  bar.
- **License**: MIT (PyPI classifier).
- **Dependencies**: `ctranslate2` (a new native inference runtime, not
  currently in this repo), `huggingface-hub`, `tokenizers`, `onnxruntime`,
  `av`. This pulls in **two** new native/binary packages
  (`ctranslate2` + `onnxruntime`) where Vosk pulls in zero.
- **Fit**: general-purpose transcription — no built-in grammar
  constraint. Matching a known phrase pool means transcribing freely
  (beam search over an open vocabulary) then fuzzy-comparing the text
  output, which is both slower and a strictly harder matching problem
  than Vosk's grammar mode for this exact use case.
- **Adoption**: 8.1M downloads/month (pypistats.org) — larger ecosystem
  than Vosk, reflecting Whisper's general popularity, not a signal about
  fit for constrained-vocabulary matching specifically.

### 3. openai-whisper (`openai-whisper`) — the reference Whisper implementation

- **PyPI**: `20250625`, uploaded **2025-06-26T01:06:13Z** — ~13 months
  before this research date, just past the ~12-month bar (gray zone).
- **Repo**: last commit **2026-04-15** (GitHub commits API) — inside the
  bar, but the commit itself ("pin pre-commit hook revisions") is
  maintenance, not a feature/fix, a weaker liveness signal than a real
  release.
- **License**: MIT.
- **Dependencies**: `torch` (already installed via SpeechBrain — the one
  candidate that adds no new ML runtime), `numba`, `tiktoken`,
  `more-itertools`.
- **Fit**: same general-transcription limitation as faster-whisper — no
  grammar constraint, needs fuzzy text matching after a full decode.
  Model weights (`tiny.en` ~75 MB) download by URL at first use by
  default; would need the same vendor-locally-offline treatment already
  applied to ECAPA and the Face Landmarker bundle.

### 4. PocketSphinx (`pocketsphinx`) — checked and disqualified

- PyPI `5.1.1`; the package's **own description** states active
  development "has largely ceased" and it is "very, very far from the
  state of the art" (maintainer's own words, quoted from the PyPI
  summary). Clear FAIL — excluded without further checking, per the
  library-evaluation playbook's "gray zone = FAIL" rule (this one is not
  even gray).

## Comparison

| Candidate | Live? (quoted evidence) | Fits our stack because | Cost / risk |
|---|---|---|---|
| **Vosk** | Wheel stale (2023-06-21) but repo commit **2026-07-02** (26 days old) — disclosed nuance, not a clean pass | Grammar-constrained decoding matches "small known phrase pool" directly; Apache-2.0 model + wrapper; zero new ML runtime (no torch/CTranslate2 dependency) | New native Kaldi binary (prebuilt wheel, like mediapipe/opencv already are); PyPI wheel itself unmaintained since 2023 even though the C++ core keeps moving |
| faster-whisper | 1.2.1, 2025-10-31 (repo 2025-11-19) — clears bar cleanly | Fast, accurate, modern | Two new native deps (ctranslate2, onnxruntime); no grammar constraint — general transcription + fuzzy text match is a worse fit for a small known pool |
| openai-whisper | 20250625, 2025-06-26 — ~13mo, gray zone on the wheel; repo commit 2026-04-15 is maintenance-only | Reuses the torch runtime already vendored for ECAPA — no new ML backend | No grammar constraint (same limitation as faster-whisper); heavier per-call compute for a task that doesn't need open-vocabulary transcription; wheel liveness is gray |
| PocketSphinx | Maintainers' own words: development "largely ceased" | — | Disqualified — FAIL |

## Answer

For matching a spoken attempt against a **small, known pool of challenge
phrases**, Vosk's grammar-constrained recognition (`SetGrammar`/the
grammar constructor argument, confirmed from the project's own API
surface) is a direct, purpose-built fit that the two Whisper-family
candidates cannot match without an extra fuzzy-matching layer — and it
adds no new ML runtime alongside the already-vendored torch/numpy stack.
Its own PyPI wheel has not been rebuilt since 2023, which is a real,
disclosed liveness gap against the harness's ~12-month bar; the
underlying repo is not abandoned (a commit 26 days before this research).
This is a case for the human to explicitly waive or reject, not a clean
pass — recorded here for that decision, not resolved unilaterally.

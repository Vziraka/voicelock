# Research — F3 voiceprint / speaker-embedding candidates

Date: 2026-07-22
Question: Which offline Python method computes the voiceprint (speaker embedding)
for F3's live match-distance display (and F4's later inner key)?
Playbook: `formats/source-playbooks/library-evaluation.md`
All pages fetched 2026-07-22. Download counts = pypistats "recent" (rolling 30 days).

## Claims

### Resemblyzer (`resemblyzer`)
- Latest **0.1.4**, uploaded **2023-10-12**. Source: https://pypi.org/pypi/resemblyzer/json
- Last commit **2023-10-12** ("Update to 0.1.4"); no newer release. Source: https://api.github.com/repos/resemble-ai/Resemblyzer/commits
- Downloads: **~289,590/month**. Source: https://pypistats.org/api/packages/resemblyzer/recent
- Deps: `torch>=1.0.1`, `librosa>=0.9.1`, `numpy`, `webrtcvad`, `scipy`. Install weight ≈ torch.
- OFFLINE: **bundled weights** — ships `resemblyzer/pretrained.pt` (~16 MB GE2E encoder) inside the package; no runtime download. Source: https://api.github.com/repos/resemble-ai/Resemblyzer/contents/resemblyzer/pretrained.pt
- Purpose-built: 256-dim GE2E d-vector + cosine similarity, exactly the same-vs-different-speaker demo.
- **LIVENESS: FAIL** — last release/commit 2023-10-12 (~2.75 yr, past the ~12-month bar).
- `unconfirmed`: installs/runs cleanly on **Python 3.11 + a modern torch 2.x** (code pinned to `torch>=1.0.1`, 2023-era APIs — not verified; cannot test-install before approval).

### SpeechBrain ECAPA-TDNN (`speechbrain`, `spkrec-ecapa-voxceleb`)
- Latest **1.1.0**, uploaded **2026-03-31**; GitHub release **v1.1.0** 2026-03-30. Source: https://pypi.org/pypi/speechbrain/json , https://api.github.com/repos/speechbrain/speechbrain/releases/latest
- Last commit **2026-06-15**. Source: https://api.github.com/repos/speechbrain/speechbrain/commits
- Downloads: **~1,625,797/month**. Source: https://pypistats.org/api/packages/speechbrain/recent
- Deps: `torch>=2.1.0`, `torchaudio>=2.1.0`, `huggingface_hub`, `soundfile`, … — heaviest install.
- OFFLINE: **runtime/first-use download** — ECAPA weights pulled from HuggingFace on first `from_hparams(...)`. Offline only if weights are pre-downloaded to a local `savedir` + `HF_HUB_OFFLINE=1` (extra packaging work). Source: https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb
- **LIVENESS: PASS** (release 2026-03-30, commits to 2026-06-15).
- `unconfirmed`: 192-dim embedding size (not stated on the fetched model card).

### librosa MFCC + cosine, DIY (`librosa`)
- Latest **0.11.0**, uploaded **2025-03-11**; last commit **2026-07-21** (active yesterday). Source: https://pypi.org/pypi/librosa/json , https://api.github.com/repos/librosa/librosa/commits
- Downloads: **~9,015,009/month** (most-installed of the three). Source: https://pypistats.org/api/packages/librosa/recent
- Deps: numpy, scipy, scikit-learn, numba, soundfile, … — **no torch**; lightest.
- OFFLINE: **fully offline, no model** — pure DSP; `librosa.feature.mfcc` documented. You build the pooled-MFCC vector + cosine yourself.
- **LIVENESS: PASS** on commit activity (2026-07-21); note last *stable release* 0.11.0 is ~16 mo old.

### Rejected without full eval
- **pyannote.audio**: embedding models are **gated** HF downloads (token + terms) at runtime — worst offline fit. OUT.
- **python_speech_features**: no releases since ~2020 — liveness FAIL. OUT.

## Liveness bar
- Resemblyzer: **FAIL** (abandoned 2023) — usable only via a recorded human waiver.
- SpeechBrain: **PASS**.
- librosa: **PASS**.

## Fit notes (vs F3 Outcome + offline constraint)
- Offline-at-runtime is a HARD project constraint. Resemblyzer (bundled) and librosa (no model) satisfy it natively; SpeechBrain needs pre-download + offline-mode packaging or it phones home.
- Demo crispness: a learned speaker encoder (Resemblyzer/ECAPA) separates same-vs-different speaker far more cleanly than pooled MFCCs, which are swayed by *content* (which words) as much as by *speaker*.
- Learning transparency: librosa MFCC is glass-box (you see how the voiceprint is built); the neural encoders are black boxes.

## Delta vs first instinct
First instinct was Resemblyzer (purpose-built, offline-bundled). Research confirmed the offline+crispness fit but flagged two catches memory hid: it is **abandoned** (2023 — needs a waiver) and its **Python 3.11 / modern-torch compatibility is unconfirmed**. librosa emerged as the maintained, torch-free, guaranteed-offline fallback at the cost of weaker separation; SpeechBrain is best-maintained/strongest but fights the offline constraint.

# Research — F1 audio capture / playback candidates

Date: 2026-07-22
Question: Which Python dependency should capture mic audio and play it back for F1?
Playbook: `formats/source-playbooks/library-evaluation.md`

## Claims

- sounddevice latest on PyPI is **0.5.5**, uploaded **2026-01-23**. Source: https://pypi.org/project/sounddevice/ (fetched 2026-07-22).
- sounddevice GitHub release **0.5.5** published **2026-01-23**. Source: https://github.com/spatialaudio/python-sounddevice/releases/tag/0.5.5 (fetched 2026-07-22).
- sounddevice docs: PortAudio bindings; play/record NumPy arrays; Linux/macOS/Windows. Source: https://python-sounddevice.readthedocs.io/ (via PyPI readme, fetched 2026-07-22).
- sounddevice downloads (pypistats): **~22,431,236 last month** / **~1,059,944 last day**. Source: https://pypistats.org/packages/sounddevice (fetched 2026-07-22).
- numpy latest on PyPI is **2.5.1**, uploaded **2026-07-04** (needed for sounddevice array I/O). Source: https://pypi.org/project/numpy/ (fetched 2026-07-22).
- PyAudio latest on PyPI is **0.2.14**, uploaded **2023-11-07**. Source: https://pypi.org/project/PyAudio/ (fetched 2026-07-22).
- PyAudio site notes Windows wheels for newer Pythons (page dated through **2024-11-23**), but that is not a PyPI release within ~12 months. Source: https://people.csail.mit.edu/hubert/pyaudio/ (fetched 2026-07-22); treat site chronology as secondary to PyPI upload date.

## Liveness bar

- sounddevice + numpy: PASS (recent uploads + large download volume).
- PyAudio: **FAIL** on the ~12-month release bar (last PyPI upload 2023-11-07). Gray zone = OUT unless human waives.

## Fit notes

- Conventions: Python owns audio; automated tests inject fake streams (no real mic in Gate).
- sounddevice fits record + playback with injectable streams for tests.
- DIY WASAPI/ctypes is possible but costs F1 demo time and maintenance with no clear gain.

## Delta vs first instinct

First instinct was sounddevice. Research agreed; PyAudio dropped on liveness, not taste.

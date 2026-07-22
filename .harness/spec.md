# Spec: F1 — The recording booth

Feature: Feature 1 from `roadmap.md`

## 0. Approval gate
- [x] Grilling record below is `CLEAR` (a search for the clarification marker —
      the bracketed `NEEDS-CLARIFICATION` token in its colon form — returns
      zero hits in this file)
- [x] Approved by human
- **Mode:** Mode 3

The agent may NOT plan or build until BOTH boxes are checked.
The second box is checked by the HUMAN typing the `x` — the agent never checks
it, no matter what was said in chat.

The Mode line is set by the human; checking box 2 approves the spec AND the
mode together (Mode 2 is the default if the human states no preference).
Mode 4 may only be set if a prior feature in this repo completed cleanly at
Mode 3 or 4. Lowering the mode mid-feature is allowed (edit this line + log it
in `memory/deviations.md`); raising it mid-feature is never allowed — a raise
is a spec amendment needing a fresh box-2 approval.

## 1. Outcome

Ship a local desktop **Booth** window where the user can record from the mic,
see a live visualizer react to speech, and play the captured audio back.
This is the first end-to-end slice of VoiceLock: prove capture + UI bridge +
playback with no auth, vault, or voiceprint yet.
Demo: speak → visualizer moves → captured audio plays back.

## 2. Grilling record — ambiguity scan

**Status: CLEAR**


| Category                                  | Verdict | Resolved by                                  |
| ----------------------------------------- | ------- | -------------------------------------------- |
| Functional scope & behavior               | Clear   | click-toggle · manual Play · mic error · 30s |
| Domain & data model                       | Clear   | roadmap / n-a (no vault yet)                 |
| Interaction & UX flow                     | Clear   | mock chrome · bars · 16k mono                |
| Non-functional (perf, security)           | Clear   | offline-only · learning demo                 |
| Integration & dependencies                | Clear   | pywebview · sounddevice + numpy              |
| Edge cases & failure modes                | Clear   | visible mic error · Record disabled          |
| Completion signals (how we know it works) | Clear   | Verification · Mode 3 blind spot             |
| Terminology (matches `CONTEXT.md`)        | Clear   | Booth · Capture                              |


Answers from grilling are written back into the matching section of THIS file —
never into a side file. Mark anything still open inline where it belongs, using
the marker token: open square bracket, `NEEDS-CLARIFICATION`, a colon, then the
question. The colon form is what the mechanical check greps for — prose that
merely *mentions* the marker (like this paragraph) never uses the colon form,
so any hit is a real unresolved question.

## 3. Non-goals

- No passphrase, enroll, unlock, vault, outer/inner lock, or on-disk sealed profile.
- No voiceprint, match distance, challenge, or liveness.
- No network, cloud, accounts, or packaging/installer polish beyond `uv run voicelock`.
- Not a shippable security product; no FAR/FRR claims.
- No redesign of the mock into a separate minimal booth UI for F1 — use the
mock chrome as-is for looks; only record/visualizer/play are live.
- No real-microphone dependency in automated Gate tests (fake/injected streams only).

## 4. Constraints

- Honor `constitution/project.md` + `constitution/topics/conventions.md`:
Python 3.11 + uv; code in `src/voicelock/`; UI in `src/voicelock/ui/`;
tests in `tests/`; Python owns audio; JS owns rendering only; offline-only.
- Entry point: `uv run voicelock` opens the Booth window.
- UI starting point: ship from `design/voicelock-mock.html` as the Booth chrome
(layout, branding, sidebar, enroll/demo panels as visual context). F1 only
wires **live** behavior for record → visualizer → playback (+ mic error).
Other mock controls stay visible but inert until later features; polish /
redesign is deferred to the end. Not "full mock wired interactive" in F1.
- Max recording length: **soft cap 30 seconds** — auto-stop at 30s (Booth may
show that the take ended); keeps buffers bounded for the demo.
- Capture format: **16 kHz mono** PCM (speech/identity-friendly default).
- Visualizer: **bars** (mock default) — live levels while recording.
- Desktop UI shell: **pywebview** (human-approved TECH-PICK). Hosts
`src/voicelock/ui/` and bridges Booth JS ↔ Python. Research:
`memory/research/2026-07-22-f1-ui-shell.md`.
- Audio capture/playback: **sounddevice + numpy** (human-approved TECH-PICK).
Python owns mic I/O and playback buffers; tests inject fake streams.
Research: `memory/research/2026-07-22-f1-audio-capture.md`.
- Record interaction: **click-toggle** — click Record to start, click Stop
(or Record again) to finish; then playback is available.
- Playback: **manual Play** — after stop, user hits Play to hear the capture;
no auto-play on stop.
- Mic missing or permission denied: **visible Booth error** — disable Record,
show a short message (e.g. "No microphone available" / permission denied);
window stays open and otherwise usable. No crash, no silent no-op.
- Mode 3 blind spot (accepted as Verification, not waived): automated tests
prove the Python capture path with fake streams; they do not prove the live
pywebview Booth. The manual demo line below covers that surface.
- Out-of-scope discoveries during Mode 3: record in `.out-of-scope/`, never build.
- Gate standing commands (wire in F1): `uv run ruff check .` → exit 0;
`uv run pytest` → exit 0.

## 5. Verification — definition of done (runnable)

The exact commands the Gate runs. Each must exit 0. Two parts, both required.
Harness rules find this section by its NAME ("Verification"), never by number —
keep the word "Verification" in the heading if sections are added or reordered.
(This FULL list gates the feature's LAST task; intermediate tasks gate on their
`plan.md` done-criteria — see the universal [Done] rule.)

Runtime budgets: any command expected to run longer than the 10-minute default
must declare its budget here (e.g. `{command}` → exit 0, budget 25 min). The
verifier waits in the foreground either way; exceeding the budget is a FAIL,
never a kill.

Mode-scaled requirements: at Mode 2+, every command here must be runnable with
pinned expectations — pinned means: the exact command, its exact expected exit
code, and any expected output stated in the line (nothing left to judgment). At Modes 3–4, additionally every task's planned
done-criteria must be runnable (no judgment-worded criteria), and this spec
must state what the agent does with discovered out-of-scope work (default:
record it in `.out-of-scope/`, never build it).

Standing (the project's full regression net, from `project.md`):

- `uv run ruff check .` → exit 0 (stdout/stderr contain no ruff error findings)
- `uv run pytest` → exit 0 (final summary reports 0 failed)

Proof surface: feature-specific commands must prove behavior at the highest
real surface the feature touches — the actual UI, CLI, or API (a script that
drives the real thing counts). If that surface cannot be checked, record the
exact limitation here; never let a proxy check silently stand in for it.
Bug fixes: the feature-specific list includes the reproduction — the same
surface the bug was reported on.

Limitation (automated): the Gate does not drive the real pywebview window or a
real microphone. Python capture/playback/levels are proven with injected fake
streams; the live Booth is proven only by the manual line below.

Feature-specific (proves THIS feature works):

- `uv run pytest tests/test_capture.py tests/test_playback.py -q` → exit 0;
final summary reports 0 failed. These modules must cover, with injected fake
streams (no real mic): (1) click-toggle start/stop yields a non-empty PCM
buffer; (2) level frames are emitted during capture for the visualizer;
(3) playback of the captured buffer completes without error; (4) mic-
unavailable path surfaces an error state suitable for disabling Record
(no crash, no silent success).
- Manual (required for F1 done): run `uv run voicelock`, then Record → speak
until the visualizer moves → Stop → Play; confirm the take is audible.
Observable: Booth window opens; visualizer reacts while recording; Play
reproduces the capture.

---

*Spec-anchored: if requirements change mid-build with human approval, this is
the amendment path — ALL of it, in order: (1) update this file, (2) re-run the
ambiguity scan on the changed sections, (3) the human re-checks box 2 (an
amended spec is a new contract — the old approval does not carry over),
(4) re-plan the affected tasks via the `plan` skill before building against
the change.*
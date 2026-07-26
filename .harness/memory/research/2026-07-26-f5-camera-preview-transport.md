# Research — how a camera feed reaches the pywebview Booth preview

- Date: 2026-07-26
- Question: F5 needs a live webcam image inside the Booth window. Who opens the
  camera — Python or the page's JavaScript — and how do pixels get to the screen?
- Playbook loaded: `formats/source-playbooks/api-how-to.md` (official docs for the
  version we are on → source → changelog → nothing else).
- CUI status: INACTIVE → external sources allowed.
- Supersedes nothing. Companion to `2026-07-26-f5-face-stack.md`, which settled
  *which library*, not *which architecture*.

## The fact that settles it

`src/voicelock/app.py:405` loads the Booth with `url=UI_PATH.as_uri()` — a
**`file://`** URL. On Windows, pywebview renders through WebView2.

Microsoft's WebView2 documentation, section "Loading local content by navigating
to a file URL", states verbatim (page `ms.date` 2025-02-21, `updated_at`
**2026-06-12**, read 2026-07-26):

> Some web APIs are limited to secure HTTPS URLs only and are not available to
> documents loaded by file URLs. This includes APIs such as
> `navigator.mediaDevices.getUserMedia()` to acquire video or sound,
> `navigator.geolocation.getCurrentPosition()` to access the device's location,
> or `Notification.requestPermission()` to request the user's permission to
> display notifications.

The same page's capability matrix marks "DOM APIs requiring secure context" as
❌ for "By navigating to a file URL", and ✔️ only for **virtual host name
mapping** (`SetVirtualHostNameToFolderMapping`) or **`WebResourceRequested`**.

Source: <https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/working-with-local-content>

Corroboration (weaker source, community): pywebview issue #909, "Webcam with
navigator.mediaDevices.getUserMedia" — reports of the camera not being reachable
with the WebView2 renderer.
Source: <https://github.com/r0x0r/pywebview/issues/909>

**Conclusion: JS cannot open the camera in this Booth as it is loaded today.**
Not a permissions prompt to be granted, not a flag to flip from Python — the API
is absent from the document's context. Making it work would mean changing how the
whole Booth is loaded (virtual host mapping), which is a WebView2-native API that
pywebview's Python surface does not expose.

- **`unconfirmed`:** whether any pywebview release exposes virtual host name
  mapping or a `WebResourceRequested`-equivalent hook. Not investigated further —
  even if it exists, it would rewrite F1's window bootstrap for a capability we
  do not need, and it would split camera ownership across the language boundary
  against the project's stated division of labor.

## What that leaves

Python owns the camera (`cv2.VideoCapture`), which is also what
`constitution/project.md` already says — "Python owns audio/DSP/crypto/state; JS
owns rendering only" — and what MediaPipe requires anyway, since MediaPipe's
Python API takes frames it is handed rather than opening a device itself.

The remaining question is only the **transport** from Python to the page:

| Transport | How | Cost / risk |
|---|---|---|
| **Composited JPEG through `evaluate_js`** | Python draws box + landmarks onto the frame with OpenCV, JPEG-encodes, base64s it into an `<img src="data:image/jpeg;base64,…">` | one payload per frame, ~40 KB base64 at 480×360 q60; everything testable in Python; overlay can never drift from its frame; visual style is OpenCV's, not the Booth's CSS |
| **Raw JPEG + landmark coordinates, drawn on a `<canvas>` overlay in JS** | same transport, two fields in one JSON payload | matches the Booth's existing look; more JS; the frame and its coords must be applied together or the dots lag the face |
| **Loopback MJPEG HTTP server** | `<img src="http://127.0.0.1:PORT/stream">`, browser decodes natively | best throughput, but adds a listening socket to an app whose stated rule is "offline-only — no network at runtime"; a loopback listener is not egress, yet it is new surface and a new failure mode |

- **`unconfirmed`:** the achievable frame rate of `evaluate_js` at ~40 KB/frame
  through pywebview's WebView2 bridge on this machine. No documentation states
  it and it was not measured (measuring requires installing the dependency,
  which TECH-PICK forbids before approval). **This is the single biggest
  execution risk in F5** and the reason the spec pins a measurable frame-rate
  floor rather than assuming smoothness.

## Answer to the question that prompted this

Python opens the camera; the page renders what Python sends. That is not a
preference — `getUserMedia` is unavailable in a `file://` document per
Microsoft's own docs, so the JS-owned alternative does not exist without
rebuilding the Booth's bootstrap. The open sub-question, which is a genuine
judgment call rather than a fact, is whether the landmarks are drawn in Python
(one composited image) or in JS (image + coordinates), and what frame rate the
`evaluate_js` bridge can actually sustain.

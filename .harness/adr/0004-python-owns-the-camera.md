# Python owns the camera and pushes composited frames to the page

The Booth is loaded from a `file://` URL (`app.py`, `url=UI_PATH.as_uri()`), and
WebView2 does not grant a secure context to file-URL documents — the browser's
media-capture API is simply absent there, so the obvious design, letting the
page open the webcam itself, does not exist in this app without rebuilding F1's
window bootstrap onto virtual host name mapping. We therefore have Python own
the device: OpenCV reads frames, MediaPipe finds the landmarks, OpenCV draws the
oval and the lip contour, and the finished 172 px square is JPEG-encoded,
base64'd and pushed into an `<img>` via `evaluate_js`.

Compositing in Python rather than shipping raw frames plus coordinates for a JS
canvas is the second half of the decision, and it was chosen for a reason
specific to this repo: the Gate is pytest with **zero** JS tests, so drawing in
Python is the only arrangement whose visible output the Gate can assert on, and
it makes overlay-vs-frame drift structurally impossible instead of merely
unlikely. The cost is that the overlay looks like OpenCV rather than like the
Booth's CSS (F9 polish), and that the `evaluate_js` bridge throughput could not
be measured until it was built — mitigated by keeping the preview at 172 px
(~8 KB/frame) and by pinning an engine-side throughput floor at the 30 fps
target, which measured ~8–10 ms/frame against a 33 ms budget.

The main alternative rejected was a loopback MJPEG HTTP server: better
throughput and native browser decoding, but it adds a listening socket to an app
whose stated rule is "offline-only — no network at runtime", which is new
surface and a new failure mode for a demo that does not need the frame rate.

*Recorded at F5's completion (2026-07-26). Full reasoning and the other rejected
options: `memory/decisions.md` (2026-07-26) and
`memory/research/2026-07-26-f5-camera-preview-transport.md`.*

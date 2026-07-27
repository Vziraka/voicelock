import pathlib

import cv2
import mediapipe as mp

from voicelock.facedetect import load_landmarker

# A single VIDEO-mode landmarker carries tracker state (an ROI prior) across
# calls, so feeding it three unrelated still photos back-to-back drops the
# face on unrelated frames (confirmed empirically: shared-instance run found
# 0 faces on the 2nd/3rd image; a fresh instance per image finds 1 every
# time). These are unrelated photographs, not consecutive video frames, so a
# fresh landmarker per image is the correct match for what is actually being
# tested here.
base = pathlib.Path("tests/fixtures/face")
for name in ("personA_1.jpg", "personA_2.jpg", "personB.jpg"):
    lm = load_landmarker()
    img = cv2.imread(str(base / name))
    assert img is not None, f"{name}: image missing"
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = lm.detect_for_video(frame, 1)
    assert len(result.face_landmarks) == 1, f"{name}: expected 1 face, got {len(result.face_landmarks)}"
    assert len(result.face_landmarks[0]) == 478, f"{name}: expected 478 landmarks"
print("ok")

import cv2
import json
import sys
import subprocess
import os

if len(sys.argv) < 4:
    print("Usage: python auto_crop.py <input.mp4> <faces.json> <output.mp4>")
    sys.exit(1)

input_video = sys.argv[1]
faces_json = sys.argv[2]
output_video = sys.argv[3]

temp_video = "temp_no_audio.mp4"

# =========================
# LOAD FACE DATA
# =========================
with open(faces_json, "r", encoding="utf-8") as f:
    faces = json.load(f)

if not isinstance(faces, list) or len(faces) == 0:
    print("❌ No valid face data parsed")
    sys.exit(1)

# =========================
# VIDEO INPUT
# =========================
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

OUT_W, OUT_H = 1080, 1920

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(temp_video, fourcc, fps, (OUT_W, OUT_H))

# =========================
# SORT FACE BY TIME
# =========================
faces.sort(key=lambda x: x["time"])
face_idx = 0

smooth_x, smooth_y = None, None
SMOOTH = 0.85

frame_idx = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    t = frame_idx / fps

    while face_idx < len(faces) - 1 and faces[face_idx + 1]["time"] <= t:
        face_idx += 1

    face = faces[face_idx]
    cx, cy = int(face["x"]), int(face["y"])

    if smooth_x is None:
        smooth_x, smooth_y = cx, cy
    else:
        smooth_x = int(SMOOTH * smooth_x + (1 - SMOOTH) * cx)
        smooth_y = int(SMOOTH * smooth_y + (1 - SMOOTH) * cy)

    crop_w = int(H * 9 / 16)
    crop_h = H

    x1 = max(0, min(W - crop_w, smooth_x - crop_w // 2))
    y1 = 0

    crop = frame[y1:y1 + crop_h, x1:x1 + crop_w]
    crop = cv2.resize(crop, (OUT_W, OUT_H))

    out.write(crop)
    frame_idx += 1

cap.release()
out.release()

# =========================
# MERGE AUDIO (FFMPEG)
# =========================
print("🔊 Merging audio...")

cmd = [
    "ffmpeg",
    "-y",
    "-i", temp_video,
    "-i", input_video,
    "-c:v", "copy",
    "-c:a", "aac",
    "-map", "0:v:0",
    "-map", "1:a:0?",
    output_video
]

subprocess.run(cmd, check=True)

os.remove(temp_video)

print("✅ DONE WITH AUDIO:", output_video)

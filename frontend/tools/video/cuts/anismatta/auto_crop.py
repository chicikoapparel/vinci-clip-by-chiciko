import cv2
import json
import sys
import subprocess
import math
import os
import numpy as np
from collections import defaultdict

# =========================
# ARGUMENTS
# =========================
if len(sys.argv) < 4:
    print("Usage: python auto_crop.py <input.mp4> <faces.json> <output.mp4>")
    sys.exit(1)

input_video = sys.argv[1]
faces_json = sys.argv[2]
output_video = sys.argv[3]

temp_video = "temp_video_no_audio.mp4"

# =========================
# LOAD FACE DATA
# =========================
with open(faces_json, "r", encoding="utf-8") as f:
    faces = json.load(f)

faces.sort(key=lambda x: x["time"])

# =========================
# VIDEO INPUT
# =========================
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
fps_int = int(round(fps))

W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

OUT_W, OUT_H = 1080, 1920
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(temp_video, fourcc, fps_int, (OUT_W, OUT_H))

# =========================
# CAMERA PARAMS
# =========================
FRAME_TOL = 1.0 / fps

PAN_SMOOTH = 0.94
PAN_DEADZONE = 60
MAX_PAN_STEP = 25

ZOOM_SMOOTH = 0.97
ZOOM_MIN = 1.0
ZOOM_MAX = 1.12

base_crop_w = int(H * 9 / 16)

# =========================
# STATE
# =========================
smooth_cx = W // 2
smooth_cy = H // 2
target_cx = smooth_cx
target_cy = smooth_cy

smooth_zoom = 1.0
target_zoom = 1.0

face_idx = 0
frame_idx = 0

face_presence = defaultdict(int)

print("▶️ Processing video (FULL FRAME • STABLE SPEAKER • SMOOTH ZOOM)...")

# =========================
# MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    t = frame_idx / fps

    faces_now = []
    i = face_idx
    while i < len(faces) and abs(faces[i]["time"] - t) <= FRAME_TOL:
        faces_now.append(faces[i])
        i += 1

    while face_idx < len(faces) - 1 and faces[face_idx]["time"] < t - FRAME_TOL:
        face_idx += 1

    if faces_now:
        for f in faces_now:
            key = f"{int(f['x']/50)}_{int(f['y']/50)}"
            face_presence[key] += 1

        dominant = max(
            faces_now,
            key=lambda f: face_presence[f"{int(f['x']/50)}_{int(f['y']/50)}"]
        )

        cx = dominant["x"] + dominant["w"] // 2
        cy = dominant["y"] + dominant["h"] // 2

        if abs(cx - target_cx) > PAN_DEADZONE:
            target_cx = cx
        if abs(cy - target_cy) > PAN_DEADZONE:
            target_cy = cy

        face_ratio = (dominant["w"] * dominant["h"]) / (base_crop_w * H)
        desired_zoom = 1.0 / math.sqrt(max(face_ratio, 0.08))
        target_zoom = max(ZOOM_MIN, min(ZOOM_MAX, desired_zoom))

    dx = max(-MAX_PAN_STEP, min(MAX_PAN_STEP, target_cx - smooth_cx))
    dy = max(-MAX_PAN_STEP, min(MAX_PAN_STEP, target_cy - smooth_cy))

    smooth_cx += int(dx * (1 - PAN_SMOOTH))
    smooth_cy += int(dy * (1 - PAN_SMOOTH))

    smooth_zoom = ZOOM_SMOOTH * smooth_zoom + (1 - ZOOM_SMOOTH) * target_zoom
    crop_w = int(base_crop_w / smooth_zoom)
    crop_w = max(300, min(W, crop_w))

    x1 = max(0, min(W - crop_w, smooth_cx - crop_w // 2))
    crop = frame[:, x1:x1 + crop_w]

    # =========================
    # RESIZE COVER (FULL FRAME)
    # =========================
    h, w = crop.shape[:2]
    scale = max(OUT_W / w, OUT_H / h)
    resized = cv2.resize(crop, (int(w * scale), int(h * scale)))

    rh, rw = resized.shape[:2]
    x = (rw - OUT_W) // 2
    y = (rh - OUT_H) // 2
    final = resized[y:y + OUT_H, x:x + OUT_W]

    out.write(final)
    frame_idx += 1

cap.release()
out.release()

# =========================
# MERGE AUDIO
# =========================
print("🔊 Merging audio...")

cmd = [
    "ffmpeg", "-y",
    "-i", temp_video,
    "-i", input_video,
    "-map", "0:v:0",
    "-map", "1:a:0?",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-shortest",
    output_video
]

subprocess.run(cmd, check=True)
os.remove(temp_video)

print("✅ DONE — FULL FRAME • NO BLACK BG • STABLE CAMERA")

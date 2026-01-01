import cv2
import json
import sys

if len(sys.argv) < 4:
    print("Usage: python face_track.py <video> <fps_interval> <output.json>")
    sys.exit(1)

video_path = sys.argv[1]
interval = int(sys.argv[2])
output_json = sys.argv[3]

cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30

results = []
frame_idx = 0

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    if frame_idx % interval == 0:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) > 0:
            # ambil wajah terbesar
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            cx = x + w // 2
            results.append({
                "frame": frame_idx,
                "time": frame_idx / fps,
                "centerX": int(cx)
            })

    frame_idx += 1

cap.release()

with open(output_json, "w") as f:
    json.dump(results, f)

print("Face track saved:", output_json)

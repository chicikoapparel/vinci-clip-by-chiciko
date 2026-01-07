import cv2
import sys
import json
import os

if len(sys.argv) < 3:
    print("Usage: python face_detect.py <video_path> <output_json>")
    sys.exit(1)

video_path = sys.argv[1]
output_json = sys.argv[2]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

PROTO = os.path.join(MODEL_DIR, "deploy.prototxt")
MODEL = os.path.join(MODEL_DIR, "res10_300x300_ssd_iter_140000.caffemodel")

if not os.path.exists(PROTO) or not os.path.exists(MODEL):
    print("❌ Face model files not found")
    sys.exit(1)

net = cv2.dnn.readNetFromCaffe(PROTO, MODEL)

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30

frame_idx = 0
results = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(
        frame, 1.0, (300, 300),
        (104.0, 177.0, 123.0)
    )

    net.setInput(blob)
    detections = net.forward()

    t = frame_idx / fps

    for i in range(detections.shape[2]):
        confidence = float(detections[0, 0, i, 2])
        if confidence < 0.6:
            continue

        box = detections[0, 0, i, 3:7] * [w, h, w, h]
        x1, y1, x2, y2 = box.astype(int)

        results.append({
            "time": round(t, 3),
            "x": int((x1 + x2) / 2),
            "y": int((y1 + y2) / 2),
            "w": int(x2 - x1),
            "h": int(y2 - y1),
            "confidence": round(confidence, 3),
            "id": 0  # sementara single face
        })

    frame_idx += 1

cap.release()

# 🔑 TULIS FILE JSON VALID
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"✅ Face data saved to {output_json}")

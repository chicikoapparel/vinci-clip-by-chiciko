# test_track.py
import json
from face_track import FaceTracker
from face_score import score_faces

faces = json.load(open("faces.json"))
tracker = FaceTracker()

current_time = None
bucket = []

for f in faces:
    if current_time is None:
        current_time = f["time"]

    if abs(f["time"] - current_time) < 0.2:
        bucket.append(f)
    else:
        tracked = tracker.update(bucket)
        target = score_faces(tracked)
        print("TARGET:", target)
        bucket = []
        current_time = f["time"]

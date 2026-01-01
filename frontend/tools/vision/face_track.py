import math

class FaceTracker:
    def __init__(self, max_dist=150):
        self.next_id = 1
        self.tracks = {}
        self.max_dist = max_dist

    def _dist(self, a, b):
        return math.hypot(a["x"] - b["x"], a["y"] - b["y"])

    def update(self, detections):
        updated = {}

        for det in detections:
            best_id = None
            best_dist = self.max_dist

            for tid, prev in self.tracks.items():
                d = self._dist(det, prev)
                if d < best_dist:
                    best_dist = d
                    best_id = tid

            if best_id is not None:
                det["id"] = best_id
                det["age"] = self.tracks[best_id].get("age", 0) + 1
                updated[best_id] = det
            else:
                det["id"] = self.next_id
                det["age"] = 1
                updated[self.next_id] = det
                self.next_id += 1

        self.tracks = updated
        return list(updated.values())

from typing import List, Dict
import math


MIN_DURATION = 1.0
MAX_DURATION = 180.0
MIN_SCORE = 4
MAX_CLIPS_PER_10_MIN = 4


def filter_clips(
    segments: List[Dict],
    total_video_duration: float
) -> List[Dict]:
    """
    Filter and limit scored segments into final clip candidates.
    """

    # 1️⃣ FILTER DASAR
    filtered = []
    for seg in segments:
        duration = seg.get("duration", 0)
        score = seg.get("score", 0)

        if (
            duration >= MIN_DURATION
            and duration <= MAX_DURATION
            and score >= MIN_SCORE
        ):
            filtered.append(seg)

    if not filtered:
        return []

    # 2️⃣ SORT BY QUALITY
    filtered.sort(
        key=lambda s: (
            -s["score"],
            abs(40 - s["duration"]),  # ideal around 40s
            s["start"]
        )
    )

    # 3️⃣ LIMIT BY VIDEO LENGTH
    max_allowed = math.ceil(
        (total_video_duration / 600.0) * MAX_CLIPS_PER_10_MIN
    )

    limited = filtered[:max_allowed]

    # 4️⃣ SORT BACK BY TIME (STABLE OUTPUT)
    limited.sort(key=lambda s: s["start"])

    return limited


# ==============================
# DEBUG TEST
# ==============================

if __name__ == "__main__":
    test_segments = [
        {"start": 10, "end": 40, "duration": 30, "score": 6},
        {"start": 50, "end": 90, "duration": 40, "score": 3},
        {"start": 100, "end": 160, "duration": 60, "score": 7},
        {"start": 170, "end": 200, "duration": 30, "score": 5},
    ]

    result = filter_clips(test_segments, total_video_duration=600)

    for r in result:
        print(r)

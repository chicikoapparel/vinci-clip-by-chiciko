from typing import List, Dict


MAX_GAP_SECONDS = 0.7
MAX_SEGMENT_DURATION = 60.0


def merge_segments(segments: List[Dict]) -> List[Dict]:
    """
    Merge transcript segments to avoid jumpy clips.
    Assumes segments are sorted by start time.
    """
    if not segments:
        return []

    merged = []
    current = segments[0].copy()

    for next_seg in segments[1:]:
        gap = next_seg["start"] - current["end"]
        next_duration = next_seg["end"] - current["start"]

        if (
            gap <= MAX_GAP_SECONDS
            and next_duration <= MAX_SEGMENT_DURATION
        ):
            # merge
            current["end"] = next_seg["end"]
            current["text"] = current.get("text", "") + " " + next_seg.get("text", "")
        else:
            merged.append(current)
            current = next_seg.copy()

    merged.append(current)
    return merged


# ==============================
# DEBUG TEST
# ==============================

if __name__ == "__main__":
    test_segments = [
        {"start": 10.0, "end": 14.0, "text": "Masalahnya bukan itu."},
        {"start": 14.2, "end": 18.0, "text": "Yang orang tidak sadar adalah ini."},
        {"start": 30.0, "end": 40.0, "text": "Ini segmen lain."}
    ]

    merged = merge_segments(test_segments)

    for seg in merged:
        print(seg)

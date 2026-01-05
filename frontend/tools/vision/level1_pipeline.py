import json
import sys
from typing import List, Dict

from segment_merge import merge_segments
from keyword_scoring import score_segments
from clip_filter import filter_clips


def load_segments(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def run_pipeline(
    segments_path: str,
    keywords_path: str,
    output_path: str,
    total_video_duration: float
):
    # 1️⃣ LOAD RAW SEGMENTS
    raw_segments = load_segments(segments_path)

    if not raw_segments:
        print("❌ No segments found")
        return

    # 2️⃣ MERGE SEGMENTS (ANTI LOMPAT)
    merged_segments = merge_segments(raw_segments)

    # 3️⃣ KEYWORD SCORING
    scored_segments = score_segments(
        merged_segments,
        keywords_path
    )

    print("MERGED SEGMENTS:", len(merged_segments))

    # 4️⃣ FILTER + LIMIT
    final_candidates = filter_clips(
        scored_segments,
        total_video_duration
    )

    # 5️⃣ SAVE OUTPUT
    save_json(final_candidates, output_path)

    print(f"✅ LEVEL 1 DONE — {len(final_candidates)} clip candidates saved")
    print(f"📄 Output: {output_path}")


# ==============================
# CLI ENTRY
# ==============================

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage:\n"
            "python level1_pipeline.py segments.json keywords.json output.json total_video_duration"
        )
        sys.exit(1)

    segments_path = sys.argv[1]
    keywords_path = sys.argv[2]
    output_path = sys.argv[3]
    total_video_duration = float(sys.argv[4])

    run_pipeline(
        segments_path,
        keywords_path,
        output_path,
        total_video_duration
    )

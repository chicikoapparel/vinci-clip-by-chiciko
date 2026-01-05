import json
import re
from typing import Dict, List


# ==============================
# TEXT NORMALIZATION
# ==============================

def normalize_text(text: str) -> str:
    """
    Normalize transcript text for keyword matching.
    - lowercase
    - remove punctuation
    - normalize whitespace
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)   # remove punctuation
    text = re.sub(r"\s+", " ", text)       # normalize spaces
    return text.strip()


# ==============================
# LOAD KEYWORDS
# ==============================

def load_keywords(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================
# SCORE SINGLE SEGMENT
# ==============================

def score_segment(
    segment: Dict,
    keyword_config: Dict
) -> Dict:
    """
    Score a single transcript segment using keywords.json
    """
    text_raw = segment.get("text", "")
    text = normalize_text(text_raw)

    total_score = 0
    matches: Dict[str, List[str]] = {}

    categories = keyword_config.get("categories", {})

    for category, cfg in categories.items():
        weight = cfg.get("weight", 1)
        keywords = cfg.get("keywords", [])

        for kw in keywords:
            kw_norm = normalize_text(kw)

            if kw_norm in text:
                total_score += weight
                matches.setdefault(category, []).append(kw)

    return {
        "start": segment.get("start"),
        "end": segment.get("end"),
        "duration": round(segment.get("end", 0) - segment.get("start", 0), 2),
        "score": total_score,
        "matches": matches,
        "text": text_raw
    }


# ==============================
# SCORE MULTIPLE SEGMENTS
# ==============================

def score_segments(
    segments: List[Dict],
    keywords_path: str
) -> List[Dict]:
    """
    Score all transcript segments.
    """
    keyword_config = load_keywords(keywords_path)

    results = []
    for seg in segments:
        scored = score_segment(seg, keyword_config)
        results.append(scored)

    return results


# ==============================
# DEBUG RUN (OPTIONAL)
# ==============================

if __name__ == "__main__":
    # Example test
    segments_example = [
        {
            "start": 12.3,
            "end": 38.7,
            "text": "Masalahnya bukan itu. Yang orang tidak sadar adalah makna sebenarnya."
        }
    ]

    scored = score_segments(
        segments_example,
        "keywords.json"
    )

    print(json.dumps(scored, indent=2, ensure_ascii=False))

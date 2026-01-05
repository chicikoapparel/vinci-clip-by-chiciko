import re
import json
import sys

if len(sys.argv) < 2:
    print("❌ Usage: python vtt_to_segments.py subtitle.vtt")
    sys.exit(1)

VTT_FILE = sys.argv[1]
OUTPUT_JSON = "segments.json"

# =========================
# UTIL
# =========================
def ts_to_seconds(ts):
    """
    Convert VTT timestamp HH:MM:SS.mmm → seconds (float)
    """
    h, m, s = ts.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

# =========================
# PARSE VTT
# =========================
segments = []
time_pattern = re.compile(
    r"(?P<start>\d+:\d{2}:\d{2}\.\d+)\s-->\s(?P<end>\d+:\d{2}:\d{2}\.\d+)"
)

current_start = None
current_end = None
current_text = []

with open(VTT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        # skip metadata
        if not line or line.startswith(("WEBVTT", "NOTE", "STYLE")):
            continue

        # timestamp line
        m = time_pattern.match(line)
        if m:
            # save previous block
            if current_start is not None and current_text:
                start = ts_to_seconds(current_start)
                end = ts_to_seconds(current_end)
                segments.append({
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "duration": round(end - start, 2),
                    "text": " ".join(current_text).strip()
                })

            current_start = m.group("start")
            current_end = m.group("end")
            current_text = []
            continue

        # subtitle text
        if current_start:
            # remove html tags
            clean = re.sub(r"<[^>]+>", "", line)
            current_text.append(clean)

# save last block
if current_start and current_text:
    start = ts_to_seconds(current_start)
    end = ts_to_seconds(current_end)
    segments.append({
        "start": round(start, 2),
        "end": round(end, 2),
        "duration": round(end - start, 2),
        "text": " ".join(current_text).strip()
    })

# =========================
# SAVE JSON
# =========================
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(segments, f, ensure_ascii=False, indent=2)

print(f"✅ segments.json dibuat: {len(segments)} segments")

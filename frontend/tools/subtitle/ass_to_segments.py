import re
import json

# =========================
# CONFIG
# =========================
ASS_FILE = "Islam_Agama_Pemersatu.ass"
OUTPUT_JSON = "segments.json"

# =========================
# UTIL
# =========================
def time_to_seconds(t):
    """
    Convert ASS time H:MM:SS.xx to seconds (float)
    """
    h, m, s = t.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

# =========================
# PARSE ASS
# =========================
segments = []

dialogue_pattern = re.compile(
    r"^Dialogue:\s*\d+,"
    r"(?P<start>\d+:\d{2}:\d{2}\.\d+),"
    r"(?P<end>\d+:\d{2}:\d{2}\.\d+),"
    r"[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,"
    r"(?P<text>.*)$"
)

with open(ASS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line.startswith("Dialogue:"):
            continue

        m = dialogue_pattern.match(line)
        if not m:
            continue

        start = time_to_seconds(m.group("start"))
        end = time_to_seconds(m.group("end"))
        duration = round(end - start, 2)

        # Bersihkan tag ASS seperti {\an8}
        text = re.sub(r"\{.*?\}", "", m.group("text")).strip()

        if not text or duration <= 0:
            continue

        segments.append({
            "start": round(start, 2),
            "end": round(end, 2),
            "duration": duration,
            "text": text
        })

# =========================
# SAVE JSON
# =========================
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(segments, f, ensure_ascii=False, indent=2)

print(f"✅ segments.json dibuat ({len(segments)} segments)")

import sys
import os
import json
import re
from faster_whisper import WhisperModel

# =========================
# SUBTITLE PRESETS
# =========================
SUBTITLE_PRESETS = {
    "tiktok": {
        "max_chars": 16,
        "font_size": 100,
        "margin_v": 260,
        "margin_h": 80
    },
    "reels": {
        "max_chars": 18,
        "font_size": 120,
        "margin_v": 260,
        "margin_h": 80
    }
}

# =========================
# COLOR CONFIG (ASS)
# =========================
ACTIVE_COLOR = "&H00FFFF&"
PASSIVE_COLOR = "&H00FFFF&"
OUTLINE_COLOR = "&H000000&"

# =========================
# ARGUMENTS
# =========================
if len(sys.argv) < 3:
    print("Usage: python subtitle.py <input_video> <output_ass> [preset] [--dump-segments]")
    sys.exit(1)

input_video = sys.argv[1]
output_ass = sys.argv[2]
preset_name = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else "tiktok"
dump_segments = "--dump-segments" in sys.argv

preset = SUBTITLE_PRESETS.get(preset_name, SUBTITLE_PRESETS["tiktok"])
MAX_CHARS = preset["max_chars"]
FONT_SIZE = preset["font_size"]
MARGIN_V = preset["margin_v"]
MARGIN_H = preset["margin_h"]

if not os.path.exists(input_video):
    print(f"Input file not found: {input_video}")
    sys.exit(1)

os.makedirs("tmp", exist_ok=True)
segments_output_path = "tmp/segments.json"

# =========================
# HELPERS
# =========================
def ass_time(t: float) -> str:
    t = max(t, 0)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02}:{s:05.2f}"

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).upper()

def split_line(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    mid = len(text) // 2
    left = text[:mid].rsplit(" ", 1)[0]
    right = text[len(left):].strip()
    return left + "\\N" + right

# =========================
# INIT WHISPER (HIGH ACCURACY)
# =========================
print("▶️ Transcribing audio (Whisper HIGH QUALITY)...")
sys.stdout.flush()

model = WhisperModel(
    "large-v3",
    device="cpu",
    compute_type="int8"
)

segments, _ = model.transcribe(
    input_video,
    language="id",
    beam_size=5,
    best_of=5,
    temperature=0.0,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=200),
    word_timestamps=True
)

# =========================
# EXPORT SEGMENTS.JSON (LEVEL 1)
# =========================
if dump_segments:
    simple_segments = []
    for seg in segments:
        if seg.text:
            simple_segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip()
            })

    with open(segments_output_path, "w", encoding="utf-8") as jf:
        json.dump(simple_segments, jf, indent=2, ensure_ascii=False)

    print(f"🧩 segments.json saved → {segments_output_path}")

# =========================
# ASS HEADER
# =========================
ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Poppins-Bold,{FONT_SIZE},{ACTIVE_COLOR},{OUTLINE_COLOR},&H000000&,1,0,0,0,100,100,0,0,1,2,0,2,{MARGIN_H},{MARGIN_H},{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# =========================
# WRITE ASS (PHRASE-BASED)
# =========================
with open(output_ass, "w", encoding="utf-8") as f:
    f.write(ass_header)

    for seg in segments:
        if not seg.words:
            continue

        phrase_words = []
        phrase_start = None

        for w in seg.words:
            if phrase_start is None:
                phrase_start = w.start

            phrase_words.append(w.word)

            joined = normalize(" ".join(phrase_words))

            is_pause = w.end - w.start > 0.6
            is_long = len(joined) >= MAX_CHARS
            is_punct = re.search(r"[.!?]$", w.word)

            if is_pause or is_long or is_punct:
                start = ass_time(phrase_start)
                end = ass_time(w.end)
                text = split_line(joined, MAX_CHARS)
                f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
                phrase_words = []
                phrase_start = None

        if phrase_words:
            start = ass_time(phrase_start)
            end = ass_time(seg.words[-1].end)
            text = split_line(normalize(" ".join(phrase_words)), MAX_CHARS)
            f.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")

print(f"✅ High-quality subtitle generated: {output_ass}")
sys.stdout.flush()

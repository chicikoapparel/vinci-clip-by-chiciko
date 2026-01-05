import sys
import os
from faster_whisper import WhisperModel
import json


# =========================
# SUBTITLE PRESETS
# =========================
SUBTITLE_PRESETS = {
    "tiktok": {
        "words_per_phrase": 2,
        "font_size": 100,
        "margin_v": 260,
        "margin_h": 80
    },
    "reels": {
        "words_per_phrase": 2,
        "font_size": 120,
        "margin_v": 260,
        "margin_h": 80
    }
}

# =========================
# COLOR CONFIG (ASS)
# =========================
ACTIVE_COLOR = "&H00FFFF&"    # Kuning
PASSIVE_COLOR = "&H00FFFF&"   # Kuning
OUTLINE_COLOR = "&H000000&"

# =========================
# ARGUMENTS
# =========================
if len(sys.argv) < 3:
    print("Usage: python subtitle.py <input_video> <output_ass> [preset]")
    sys.exit(1)

input_video = sys.argv[1]
output_ass = sys.argv[2]
preset_name = sys.argv[3] if len(sys.argv) > 3 else "tiktok"

preset = SUBTITLE_PRESETS.get(preset_name, SUBTITLE_PRESETS["tiktok"])

WORDS_PER_PHRASE = preset["words_per_phrase"]
FONT_SIZE = preset["font_size"]
MARGIN_V = preset["margin_v"]
MARGIN_H = preset["margin_h"]

if not os.path.exists(input_video):
    print(f"Input file not found: {input_video}")
    sys.exit(1)

dump_segments = "--dump-segments" in sys.argv
segments_output_path = "tmp/segments.json"

os.makedirs("tmp", exist_ok=True)

# =========================
# HELPERS
# =========================
def normalize(text: str) -> str:
    return text.upper().strip()

def ass_time(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02}:{s:05.2f}"

def safe_word(word: str, max_len=10) -> str:
    if len(word) > max_len:
        mid = len(word) // 2
        return word[:mid] + "\\N" + word[mid:]
    return word

# =========================
# INIT WHISPER (CPU SAFE)
# =========================
print("▶️ Transcribing audio (Whisper CPU)...")
sys.stdout.flush()

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

segments, _ = model.transcribe(
    input_video,
    language="id",
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=300),
    word_timestamps=True
)

# =========================
# EXPORT SEGMENTS.JSON (LEVEL 1)
# =========================
if dump_segments:
    simple_segments = []

    for seg in segments:
        text = seg.text.strip() if seg.text else ""
        if not text:
            continue

        simple_segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": text
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
Style: Passive,Poppins-Bold,{FONT_SIZE},{PASSIVE_COLOR},{OUTLINE_COLOR},&H000000&,1,0,0,0,100,100,0,0,1,2,0,2,{MARGIN_H},{MARGIN_H},{MARGIN_V},1
Style: Active,Poppins-Bold,{FONT_SIZE},{ACTIVE_COLOR},{OUTLINE_COLOR},&H000000&,1,0,0,0,100,100,0,0,1,2,0,2,{MARGIN_H},{MARGIN_H},{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# =========================
# WRITE ASS
# =========================
with open(output_ass, "w", encoding="utf-8") as f:
    f.write(ass_header)

    for seg in segments:
        if not seg.words:
            continue

        buffer = []

        for w in seg.words:
            buffer.append(w)

            if len(buffer) == WORDS_PER_PHRASE:
                start = ass_time(buffer[0].start)
                end = ass_time(buffer[-1].end)

                parts = []
                for i, ww in enumerate(buffer):
                    word = safe_word(normalize(ww.word))
                    if i == len(buffer) - 1:
                        parts.append(f"{{\\rActive}}{word}")
                    else:
                        parts.append(f"{{\\rPassive}}{word}")

                f.write(f"Dialogue: 0,{start},{end},Passive,,0,0,0,,{' '.join(parts)}\n")
                buffer = []

        if buffer:
            start = ass_time(buffer[0].start)
            end = ass_time(buffer[-1].end)

            parts = []
            for i, ww in enumerate(buffer):
                word = safe_word(normalize(ww.word))
                if i == len(buffer) - 1:
                    parts.append(f"{{\\rActive}}{word}")
                else:
                    parts.append(f"{{\\rPassive}}{word}")

            f.write(f"Dialogue: 0,{start},{end},Passive,,0,0,0,,{' '.join(parts)}\n")

print(f"✅ Subtitle ASS generated: {output_ass}")
sys.stdout.flush()

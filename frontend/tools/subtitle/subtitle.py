import sys
import os
from faster_whisper import WhisperModel

# =========================
# SUBTITLE PRESETS
# =========================
SUBTITLE_PRESETS = {
    "tiktok": {
        "words_per_phrase": 2,
        "font_size": 150,
        "margin_v": 260
    },
    "reels": {
        "words_per_phrase": 3,
        "font_size": 150,
        "margin_v": 260
    }
}

# =========================
# COLOR CONFIG (ASS)
# =========================
ACTIVE_COLOR = "&H00FFFF&"    # KUNING
PASSIVE_COLOR = "&HAAAAAA&"   # ABU-ABU
OUTLINE_COLOR = "&H000000&"

# =========================
# ARGUMENT VALIDATION
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

if not os.path.exists(input_video):
    print(f"Input file not found: {input_video}")
    sys.exit(1)

# =========================
# TEXT NORMALIZER
# =========================
def normalize(text: str) -> str:
    return text.upper().strip()

# =========================
# ASS TIME FORMAT
# =========================
def ass_time(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02}:{s:05.2f}"

# =========================
# INIT WHISPER (CPU SAFE)
# =========================
print("WHISPER START")
sys.stdout.flush()

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

# =========================
# TRANSCRIBE
# =========================
segments, _ = model.transcribe(
    input_video,
    language="id",
    vad_filter=True,
    word_timestamps=True
)

# =========================
# ASS HEADER (VALID & SAFE)
# =========================
ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Passive,Poppins-Bold,{FONT_SIZE},{PASSIVE_COLOR},{OUTLINE_COLOR},&H000000&,0,0,0,0,100,100,0,0,1,2,1,2,40,40,{MARGIN_V},1
Style: Active,Poppins-Bold,{FONT_SIZE},{ACTIVE_COLOR},{OUTLINE_COLOR},&H000000&,0,0,0,0,100,100,0,0,1,2,1,2,40,40,{MARGIN_V},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

# =========================
# WRITE ASS (KARAOKE)
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
                    word = normalize(ww.word)
                    if i == len(buffer) - 1:
                        parts.append(f"{{\\rActive}}{word}")
                    else:
                        parts.append(f"{{\\rPassive}}{word}")

                text = " ".join(parts)
                f.write(f"Dialogue: 0,{start},{end},Passive,,0,0,0,,{text}\n")
                buffer = []

        # sisa kata
        if buffer:
            start = ass_time(buffer[0].start)
            end = ass_time(buffer[-1].end)

            parts = []
            for i, ww in enumerate(buffer):
                word = normalize(ww.word)
                if i == len(buffer) - 1:
                    parts.append(f"{{\\rActive}}{word}")
                else:
                    parts.append(f"{{\\rPassive}}{word}")

            text = " ".join(parts)
            f.write(f"Dialogue: 0,{start},{end},Passive,,0,0,0,,{text}\n")

print(f"ASS subtitle generated ({preset_name}): {output_ass}")
sys.stdout.flush()

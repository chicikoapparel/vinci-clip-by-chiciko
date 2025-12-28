import sys
import os
from faster_whisper import WhisperModel

# =========================
# ARGUMENT VALIDATION
# =========================
if len(sys.argv) < 3:
    print("Usage: python subtitle.py <input_video> <output_srt>")
    sys.exit(1)

input_video = sys.argv[1]
output_srt = sys.argv[2]

if not os.path.exists(input_video):
    print(f"Input file not found: {input_video}")
    sys.exit(1)

# =========================
# INIT MODEL (CPU SAFE)
# =========================
# small = balance terbaik akurasi / speed CPU
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"   # penting untuk CPU, jauh lebih ringan
)

# =========================
# TRANSCRIBE
# =========================
segments, info = model.transcribe(
    input_video,
    language="id",
    vad_filter=True      # potong silence → subtitle lebih rapi
)

# =========================
# SRT TIME FORMATTER
# =========================
def to_srt_time(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

# =========================
# WRITE SRT
# =========================
with open(output_srt, "w", encoding="utf-8") as f:
    index = 1
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue

        f.write(f"{index}\n")
        f.write(f"{to_srt_time(seg.start)} --> {to_srt_time(seg.end)}\n")
        f.write(text + "\n\n")
        index += 1

print(f"Subtitle generated: {output_srt}")

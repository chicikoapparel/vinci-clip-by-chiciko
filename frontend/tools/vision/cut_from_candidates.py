import json
import os
import subprocess
from pathlib import Path

# =====================
# CONFIG
# =====================
INPUT_VIDEO = "input.mp4"          # ganti sesuai video kamu
CANDIDATES = "candidates.json"
OUTPUT_DIR = "clips_raw"
FFMPEG = "ffmpeg"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================
# LOAD CANDIDATES
# =====================
with open(CANDIDATES, "r", encoding="utf-8") as f:
    clips = json.load(f)

if not clips:
    raise RuntimeError("❌ candidates.json kosong")

print(f"🎬 Total clips: {len(clips)}")

# =====================
# CUT VIDEO
# =====================
for i, clip in enumerate(clips):
    start = clip["start"]
    end = clip["end"]
    duration = round(end - start, 2)

    out_path = Path(OUTPUT_DIR) / f"clip_{i+1:02d}.mp4"

    cmd = [
        FFMPEG,
        "-y",
        "-ss", str(start),
        "-i", INPUT_VIDEO,
        "-t", str(duration),
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-movflags", "+faststart",
        str(out_path)
    ]

    print(f"✂️  Cutting clip {i+1}: {start:.2f}s → {end:.2f}s ({duration}s)")
    subprocess.run(cmd, check=True)

print("✅ Semua clip berhasil dipotong")

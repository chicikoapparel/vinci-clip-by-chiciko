import json
import subprocess
import os
import sys

if len(sys.argv) < 3:
    print("Usage: python batch_cut.py <input_video> <highlights.json>")
    sys.exit(1)

INPUT_VIDEO = sys.argv[1]
HIGHLIGHTS_FILE = sys.argv[2]

if not os.path.exists(INPUT_VIDEO):
    raise FileNotFoundError(f"Input video not found: {INPUT_VIDEO}")

if not os.path.exists(HIGHLIGHTS_FILE):
    raise FileNotFoundError(f"highlights.json not found: {HIGHLIGHTS_FILE}")

OUTPUT_DIR = "cuts"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# =========================
# LOAD HIGHLIGHTS
# =========================
with open(HIGHLIGHTS_FILE, "r", encoding="utf-8") as f:
    highlights = json.load(f)

if not highlights:
    print("⚠️ highlights.json kosong — tidak ada clip untuk dipotong")
    sys.exit(0)

# =========================
# FFMPEG CUT
# =========================
def cut_clip(idx, start, end):
    output_path = os.path.join(OUTPUT_DIR, f"cut_{idx:02d}.mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", INPUT_VIDEO,
        "-ss", str(start),
        "-to", str(end),
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        output_path
    ]

    print("▶️ Cutting:", output_path)
    subprocess.run(cmd, check=True)

# =========================
# RUN BATCH
# =========================
for i, clip in enumerate(highlights, start=1):
    start = clip.get("start")
    end = clip.get("end")

    if start is None or end is None:
        print(f"❌ Invalid clip data at index {i}")
        continue

    if end <= start:
        print(f"❌ Invalid duration at clip {i}")
        continue

    cut_clip(i, start, end)

print(f"✅ Batch cut selesai: {len(highlights)} clip(s)")
print(f"📂 Output folder: {OUTPUT_DIR}")

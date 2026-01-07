import os
import subprocess
import sys

# =========================
# PATH CONFIG
# =========================
CUTS_DIR = "cuts"
OUTPUT_DIR = "outputs"
TMP_DIR = "tmp"

FACE_DETECT = "../vision/face_detect.py"
AUTO_CROP = "../vision/auto_crop.py"
SUBTITLE = "../subtitle/subtitle.py"

PYTHON = sys.executable  # gunakan python aktif

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

# =========================
# VALIDATION
# =========================
if not os.path.exists(CUTS_DIR):
    raise FileNotFoundError(f"Folder '{CUTS_DIR}' tidak ditemukan")

cut_files = sorted(f for f in os.listdir(CUTS_DIR) if f.endswith(".mp4"))

if not cut_files:
    print("⚠️ Tidak ada file cut_*.mp4")
    sys.exit(0)

# =========================
# PIPELINE PER CLIP
# =========================
for idx, clip_name in enumerate(cut_files, start=1):
    clip_path = os.path.join(CUTS_DIR, clip_name)

    base = os.path.splitext(clip_name)[0]
    faces_json = os.path.join(TMP_DIR, f"{base}_faces.json")
    cropped_video = os.path.join(TMP_DIR, f"{base}_crop.mp4")
    subtitle_ass = os.path.join(TMP_DIR, f"{base}.ass")
    final_output = os.path.join(OUTPUT_DIR, f"{base}_final.mp4")

    print(f"\n🚀 Processing {clip_name}")

    # =========================
    # 1️⃣ FACE DETECT
    # =========================
    print("  🔍 Face detection...")
    subprocess.run(
        [PYTHON, FACE_DETECT, clip_path, faces_json],
        check=True
    )

    # =========================
    # 2️⃣ AUTO CROP (PORTRAIT)
    # =========================
    print("  🎥 Auto crop (9:16)...")
    subprocess.run(
        [PYTHON, AUTO_CROP, clip_path, faces_json, cropped_video],
        check=True
    )

    # =========================
    # 3️⃣ SUBTITLE GENERATION
    # =========================
    print("  📝 Generating subtitle...")
    subprocess.run(
        [PYTHON, SUBTITLE, cropped_video, subtitle_ass, "tiktok"],
        check=True
    )

    # =========================
    # 4️⃣ BURN SUBTITLE
    # =========================
    print("  🔥 Burning subtitle...")
    subtitle_ass_ffmpeg = subtitle_ass.replace("\\", "/")
    burn_cmd = [
    "ffmpeg",
    "-y",
    "-i", cropped_video,
    "-vf", f"ass={subtitle_ass_ffmpeg}",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    final_output
    ]

    subprocess.run(burn_cmd, check=True)

    print(f"  ✅ Done → {final_output}")

print("\n🎉 BATCH PIPELINE SELESAI")
print(f"📂 Final videos → {OUTPUT_DIR}")

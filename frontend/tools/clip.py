import subprocess
import os
import math
import sys

def get_video_duration(video_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

def split_video(video_path, clip_duration, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    total_duration = get_video_duration(video_path)
    total_clips = math.ceil(total_duration / clip_duration)

    for i in range(total_clips):
        start = i * clip_duration
        output_file = os.path.join(output_dir, f"clip_{i+1:03}.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(clip_duration),
            "-c", "copy",
            output_file
        ]

        subprocess.run(cmd)
        print(f"✅ Created {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python split_by_duration.py input.mp4 30 output_folder")
        sys.exit(1)

    video = sys.argv[1]
    duration = int(sys.argv[2])
    output = sys.argv[3]

    split_video(video, duration, output)

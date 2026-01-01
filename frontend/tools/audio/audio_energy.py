import sys
import json
import subprocess
import numpy as np
import os

if len(sys.argv) < 4:
    print("Usage: python audio_energy.py <video> <window_sec> <output.json>")
    sys.exit(1)

video = sys.argv[1]
window = float(sys.argv[2])
output = sys.argv[3]

wav = video + ".wav"

# extract mono audio
subprocess.run([
    "ffmpeg", "-y",
    "-i", video,
    "-ac", "1",
    "-ar", "16000",
    wav
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import soundfile as sf
audio, sr = sf.read(wav)

results = []
samples_per_win = int(window * sr)

for i in range(0, len(audio), samples_per_win):
    chunk = audio[i:i + samples_per_win]
    if len(chunk) == 0:
        continue

    rms = float(np.sqrt(np.mean(chunk ** 2)))
    t = i / sr

    results.append({
        "time": t,
        "energy": rms
    })

os.remove(wav)

with open(output, "w") as f:
    json.dump(results, f)

print("Audio energy saved:", output)

import { execSync } from "child_process";

export function detectHardware() {
  let hasNvidia = false;

  try {
    const out = execSync("nvidia-smi -L", {
      stdio: ["ignore", "pipe", "ignore"],
    }).toString();

    if (out.toLowerCase().includes("nvidia")) {
      hasNvidia = true;
    }
  } catch {
    hasNvidia = false;
  }

  const config = {
    mode: hasNvidia ? "CPU+GPU" : "CPU_ONLY",
    videoCodec: hasNvidia ? "h264_nvenc" : "libx264",
    ffmpegPreset: hasNvidia ? "p4" : "veryfast",
    whisperDevice: hasNvidia ? "cuda" : "cpu",
    whisperCompute: hasNvidia ? "float16" : "int8",
  };

  console.log("🧠 HARDWARE MODE:", config.mode);
  console.log("🎬 VIDEO CODEC:", config.videoCodec);
  console.log("🎙️ WHISPER:", config.whisperDevice);

  return config;
}

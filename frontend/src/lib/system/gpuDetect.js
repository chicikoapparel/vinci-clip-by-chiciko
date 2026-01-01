import { execSync } from "child_process";

let cachedResult = null;

export function detectVideoEncoder() {
  if (cachedResult) return cachedResult;

  try {
    const output = execSync("ffmpeg -hide_banner -encoders", {
      encoding: "utf8",
    });

    if (output.includes("h264_nvenc")) {
      cachedResult = {
        encoder: "h264_nvenc",
        note: "NVIDIA GPU detected",
      };
      return cachedResult;
    }

    if (output.includes("h264_amf")) {
      cachedResult = {
        encoder: "h264_amf",
        note: "AMD GPU detected",
      };
      return cachedResult;
    }

    if (output.includes("h264_qsv")) {
      cachedResult = {
        encoder: "h264_qsv",
        note: "Intel iGPU detected",
      };
      return cachedResult;
    }
  } catch (err) {
    console.warn("GPU detect failed, fallback CPU");
  }

  cachedResult = {
    encoder: "libx264",
    note: "CPU encoding",
  };
  return cachedResult;
}

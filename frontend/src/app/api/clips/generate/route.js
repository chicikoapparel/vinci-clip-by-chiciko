export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import os from "os";
import { EXPORT_PRESETS } from "@/lib/presets/exportPresets";

/* =========================
   AUDIO PAN DETECTOR
   kiri / tengah / kanan
=========================*/
async function detectSpeakerSide(videoPath, start, duration) {
  return new Promise((resolve) => {
    const ffmpeg = spawn("ffmpeg", [
      "-ss", String(start),
      "-t", String(Math.min(duration, 3)), // cukup 2–3 detik
      "-i", videoPath,
      "-filter_complex",
      "astats=metadata=1:reset=1",
      "-f", "null",
      "-"
    ]);

    let left = 0;
    let right = 0;

    ffmpeg.stderr.on("data", (d) => {
      const line = d.toString();
      if (line.includes("Channel 1 RMS level")) {
        left = parseFloat(line.split(":").pop());
      }
      if (line.includes("Channel 2 RMS level")) {
        right = parseFloat(line.split(":").pop());
      }
    });

    ffmpeg.on("close", () => {
      if (!isFinite(left) || !isFinite(right)) {
        resolve("center");
      } else if (left > right * 1.2) {
        resolve("left");
      } else if (right > left * 1.2) {
        resolve("right");
      } else {
        resolve("center");
      }
    });
  });
}

export async function POST(req) {
  try {
    const body = await req.json();
    const { transcriptId, segments, exportPlatform = "tiktok" } = body;

    if (
      !transcriptId ||
      !ObjectId.isValid(transcriptId) ||
      !Array.isArray(segments) ||
      segments.length === 0
    ) {
      return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
    }

    const preset = EXPORT_PRESETS[exportPlatform];
    if (!preset) {
      return NextResponse.json({ error: "Invalid export platform" }, { status: 400 });
    }

    const client = await clientPromise;
    const db = client.db();

    const transcript = await db
      .collection("transcripts")
      .findOne({ _id: new ObjectId(transcriptId) });

    if (!transcript || !fs.existsSync(transcript.filepath)) {
      return NextResponse.json({ error: "Source video not found" }, { status: 404 });
    }

    const inputPath = transcript.filepath;
    const outputDir = path.resolve(process.cwd(), "public", "clips");
    if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

    for (const seg of segments) {
      const startTime = Number(seg.startTime);
      const endTime = Number(seg.endTime);
      if (isNaN(startTime) || isNaN(endTime) || endTime <= startTime) continue;

      const duration = Math.min(endTime - startTime, preset.maxDuration);
      const clipId = new ObjectId();

      const outputPath = path.join(outputDir, `clip-${clipId}.mp4`);
      const videoUrl = `/clips/clip-${clipId}.mp4`;

      /* =========================
         AUDIO SPEAKER SIDE
      ==========================*/
      const side = await detectSpeakerSide(inputPath, startTime, duration);

      const cropWidth = Math.round(preset.height * 9 / 16);
      let cropX;

      if (side === "left") {
        cropX = 0;
      } else if (side === "right") {
        cropX = preset.width - cropWidth;
      } else {
        cropX = Math.floor((preset.width - cropWidth) / 2);
      }

      const videoFilter = `
scale=${preset.width}:${preset.height}:force_original_aspect_ratio=increase,
crop=${cropWidth}:${preset.height}:${cropX}:0
`.replace(/\s+/g, "");

      await new Promise((resolve, reject) => {
        const ffmpeg = spawn("ffmpeg", [
          "-y",
          "-ss", String(startTime),
          "-i", inputPath,
          "-t", String(duration),
          "-vf", videoFilter,
          "-r", String(preset.fps),
          "-c:v", "libx264",
          "-pix_fmt", "yuv420p",
          "-profile:v", "main",
          "-level", "4.1",
          "-b:v", preset.videoBitrate,
          "-c:a", "aac",
          "-b:a", preset.audioBitrate,
          "-movflags", "+faststart",
          outputPath,
        ]);

        ffmpeg.on("close", (code) =>
          code === 0 ? resolve() : reject(new Error("FFmpeg failed"))
        );
      });

      await db.collection("clips").insertOne({
        _id: clipId,
        transcriptId: new ObjectId(transcriptId),
        startTime,
        endTime: startTime + duration,
        exportPlatform,
        presetSnapshot: preset,
        videoUrl,
        status: "ready",
        createdAt: new Date(),
      });
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("GENERATE ERROR:", err);
    return NextResponse.json(
      { error: err.message || "Generate failed" },
      { status: 500 }
    );
  }
}

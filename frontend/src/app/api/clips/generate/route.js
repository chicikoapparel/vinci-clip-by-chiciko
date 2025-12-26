export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import { EXPORT_PRESETS } from "@/lib/presets/exportPresets";

export async function POST(req) {
  try {
    const body = await req.json();
    const { transcriptId, segments, exportPlatform = "tiktok" } = body;

    /* =========================
       VALIDATION
    ==========================*/
    if (
      !transcriptId ||
      !ObjectId.isValid(transcriptId) ||
      !Array.isArray(segments) ||
      segments.length === 0
    ) {
      return NextResponse.json(
        { error: "Invalid payload", received: body },
        { status: 400 }
      );
    }

    const preset = EXPORT_PRESETS[exportPlatform];
    if (!preset) {
      return NextResponse.json(
        { error: "Invalid export platform" },
        { status: 400 }
      );
    }

    /* =========================
       DB
    ==========================*/
    const client = await clientPromise;
    const db = client.db();

    const transcript = await db
      .collection("transcripts")
      .findOne({ _id: new ObjectId(transcriptId) });

    if (!transcript) {
      return NextResponse.json(
        { error: "Transcript not found" },
        { status: 404 }
      );
    }

    const inputPath = transcript.filepath;
    if (!fs.existsSync(inputPath)) {
      return NextResponse.json(
        { error: "Source video not found" },
        { status: 404 }
      );
    }

    /* =========================
       OUTPUT DIR
    ==========================*/
    const outputDir = path.resolve(process.cwd(), "public", "clips");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    /* =========================
       PROCESS SEGMENTS
    ==========================*/
    for (const seg of segments) {
      const startTime = Number(seg.startTime);
      const endTime = Number(seg.endTime);

      if (Number.isNaN(startTime) || Number.isNaN(endTime) || endTime <= startTime) {
        throw new Error(`Invalid segment: ${JSON.stringify(seg)}`);
      }

      const rawDuration = endTime - startTime;
      const duration = Math.min(rawDuration, preset.maxDuration);

      const clipId = new ObjectId();
      const filename = `clip-${clipId.toString()}.mp4`;
      const outputPath = path.join(outputDir, filename);
      const videoUrl = `/clips/${filename}`;

      /* =========================
         🎬 VIDEO FILTER (CENTERED)
         - NO CROP
         - LETTERBOX
      ==========================*/
      const videoFilter = `
scale=${preset.width}:-2:force_original_aspect_ratio=decrease,
pad=${preset.width}:${preset.height}:(ow-iw)/2:(oh-ih)/2:black
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

        ffmpeg.stderr.on("data", (d) =>
          console.log("FFMPEG:", d.toString())
        );

        ffmpeg.on("close", (code) => {
          if (code === 0) resolve();
          else reject(new Error(`FFmpeg exited with ${code}`));
        });
      });

      if (!fs.existsSync(outputPath)) {
        throw new Error("FFmpeg output not created");
      }

      /* =========================
         SAVE CLIP
      ==========================*/
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
      { error: err.message || "Failed generate clip" },
      { status: 500 }
    );
  }
}

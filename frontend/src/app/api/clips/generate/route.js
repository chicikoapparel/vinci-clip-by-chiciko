export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { ObjectId } from "mongodb";
import { spawn } from "child_process";
import path from "path";
import fs from "fs";
import os from "os";
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
       OUTPUT DIR (PUBLIC)
    ==========================*/
    const outputDir = path.resolve(process.cwd(), "public", "clips");
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    /* =========================
       TMP DIR (NO SPACES)
    ==========================*/
    const tmpDir = path.join(os.tmpdir(), "vinci-clips");
    if (!fs.existsSync(tmpDir)) {
      fs.mkdirSync(tmpDir, { recursive: true });
    }

    /* =========================
       PROCESS SEGMENTS (BATCH)
    ==========================*/
    for (const seg of segments) {
      const startTime = Number(seg.startTime);
      const endTime = Number(seg.endTime);

      if (
        Number.isNaN(startTime) ||
        Number.isNaN(endTime) ||
        endTime <= startTime
      ) {
        continue;
      }

      const duration = Math.min(endTime - startTime, preset.maxDuration);

      const clipId = new ObjectId();
      const rawOutput = path.join(outputDir, `clip-${clipId}.mp4`);
      const finalOutput = path.join(outputDir, `clip-${clipId}_sub.mp4`);
      const videoUrl = `/clips/clip-${clipId}_sub.mp4`;

      /* === GENERATE CLIP === */
      await new Promise((resolve, reject) => {
        spawn("ffmpeg", [
          "-y",
          "-ss", String(startTime),
          "-i", inputPath,
          "-t", String(duration),
          "-vf",
          `scale=${preset.width}:-2:force_original_aspect_ratio=decrease,pad=${preset.width}:${preset.height}:(ow-iw)/2:(oh-ih)/2:black`,
          "-r", String(preset.fps),
          "-c:v", "libx264",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac",
          rawOutput,
        ]).on("close", (c) => (c === 0 ? resolve() : reject()));
      });

      if (!fs.existsSync(rawOutput)) continue;

/* === SUBTITLE (ASS KARAOKE – WINDOWS FINAL FIX) === */
const subtitleScript = path.resolve(
  process.cwd(),
  "tools",
  "subtitle",
  "subtitle.py"
);

const assPath = rawOutput.replace(".mp4", ".ass");

// 🔑 PENTING: nama sederhana TANPA PATH
const assTmp = path.join(tmpDir, `sub-${clipId}.ass`);
const tmpOut = path.join(tmpDir, `out-${clipId}.mp4`);

try {
  /* 1️⃣ Generate ASS */
  await new Promise((resolve, reject) => {
    const py = spawn("python", [
      subtitleScript,
      rawOutput,
      assPath,
      exportPlatform,
    ]);

    py.stderr.on("data", (d) =>
      console.error("SUB PY:", d.toString())
    );

    py.on("close", (c) =>
      c === 0 ? resolve() : reject(new Error("Subtitle gen failed"))
    );
  });

  if (!fs.existsSync(assPath)) {
    throw new Error("ASS subtitle not generated");
  }

  /* 2️⃣ COPY ASS → TMP (HILANGKAN PATH WINDOWS) */
  fs.copyFileSync(assPath, assTmp);

  /* 3️⃣ Burn subtitle (PAKAI NAMA FILE SAJA) */
  await new Promise((resolve, reject) => {
    const burn = spawn(
      "ffmpeg",
      [
        "-y",
        "-i", rawOutput,
        "-vf", `ass=${path.basename(assTmp)}`,
        "-c:a", "copy",
        path.basename(tmpOut),
      ],
      { cwd: tmpDir }
    );

    burn.stderr.on("data", (d) =>
      console.log("BURN:", d.toString())
    );

    burn.on("close", (c) =>
      c === 0 ? resolve() : reject(new Error("Burn failed"))
    );
  });

  fs.copyFileSync(tmpOut, finalOutput);
} catch (err) {
  console.error("Subtitle failed, fallback:", err);
  fs.copyFileSync(rawOutput, finalOutput);
}
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
    console.error(err);
    return NextResponse.json(
      { error: err.message || "Generate failed" },
      { status: 500 }
    );
  }
}

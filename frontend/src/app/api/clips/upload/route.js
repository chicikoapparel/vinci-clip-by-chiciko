export const runtime = "nodejs";

import { NextResponse } from "next/server";
import clientPromise from "@/lib/mongodb";
import { spawn } from "child_process";
import fs from "fs";
import path from "path";

/* =========================
   GET VIDEO DURATION
========================= */
async function getVideoDuration(filePath) {
  return new Promise((resolve, reject) => {
    const ffprobe = spawn("ffprobe", [
      "-v",
      "error",
      "-show_entries",
      "format=duration",
      "-of",
      "default=noprint_wrappers=1:nokey=1",
      filePath,
    ]);

    let output = "";

    ffprobe.stdout.on("data", (data) => {
      output += data.toString();
    });

    ffprobe.on("close", () => {
      const duration = Math.floor(Number(output));
      resolve(Number.isNaN(duration) ? 0 : duration);
    });

    ffprobe.on("error", reject);
  });
}

/* =========================
   UPLOAD API
========================= */
export async function POST(req) {
  try {
    const formData = await req.formData();
    const file = formData.get("file");

    if (!file) {
      return NextResponse.json(
        { error: "No file uploaded" },
        { status: 400 }
      );
    }

    const buffer = Buffer.from(await file.arrayBuffer());

    const uploadDir = path.join(process.cwd(), "uploads");
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    const filename = `${Date.now()}-${file.name}`;
    const filePath = path.join(uploadDir, filename);

    fs.writeFileSync(filePath, buffer);

    // 🔥 HITUNG DURASI VIDEO
    const duration = await getVideoDuration(filePath);

    const client = await clientPromise;
    const db = client.db();

    const result = await db.collection("transcripts").insertOne({
      originalFilename: file.name,
      filepath: filePath,
      duration, // ✅ INI YANG KRUSIAL
      status: "uploaded",
      createdAt: new Date(),
    });

    return NextResponse.json({
      success: true,
      transcriptId: result.insertedId,
      duration,
    });
  } catch (err) {
    console.error("UPLOAD ERROR:", err);
    return NextResponse.json(
      { error: "Upload failed" },
      { status: 500 }
    );
  }
}

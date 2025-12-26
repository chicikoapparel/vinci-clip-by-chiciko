export const runtime = "nodejs";

import type { NextApiRequest, NextApiResponse } from "next";
import formidable, { File } from "formidable";
import fs from "fs";
import path from "path";
import clientPromise from "@/lib/mongodb";
import { spawn } from "child_process";

/* =================================================
   HITUNG DURASI VIDEO (FFPROBE)
   ================================================= */
async function getVideoDuration(filePath: string): Promise<number> {
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

    ffprobe.stdout.on("data", (data: Buffer) => {
      output += data.toString();
    });

    ffprobe.on("close", () => {
      const duration = Math.floor(Number(output));
      resolve(Number.isNaN(duration) ? 0 : duration);
    });

    ffprobe.on("error", reject);
  });
}

/* =================================================
   NEXT CONFIG
   ================================================= */
export const config = {
  api: {
    bodyParser: false,
  },
};

/* =================================================
   UPLOAD HANDLER
   ================================================= */
export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  /* 🔕 OFF: bikin folder uploads manual (sudah aman)
  --------------------------------------------------
  const uploadDir = path.join(process.cwd(), "public", "uploads");
  if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
  }
  -------------------------------------------------- */

  const form = formidable({
    multiples: false,
    maxFileSize: 2 * 1024 * 1024 * 1024, // ✅ 2 GB
    keepExtensions: true,
    allowEmptyFiles: false,
  });

  form.parse(req, async (err, fields, files) => {
    try {
      if (err) {
        console.error("FORM PARSE ERROR:", err);
        return res.status(500).json({ error: "Upload failed" });
      }

      const uploaded = files.video;
      if (!uploaded) {
        return res.status(400).json({ error: "No video uploaded" });
      }

      const file: File = Array.isArray(uploaded)
        ? uploaded[0]
        : uploaded;

      if (!fs.existsSync(file.filepath)) {
        return res.status(400).json({ error: "Uploaded file not found" });
      }

      /* =================================================
         🔥 HITUNG DURASI VIDEO (INI KUNCI MASALAHMU)
         ================================================= */
      const duration = await getVideoDuration(file.filepath);

      const client = await clientPromise;
      const db = client.db();

      const result = await db.collection("transcripts").insertOne({
        originalFilename: file.originalFilename,
        filepath: file.filepath, // path permanen
        size: file.size,
        duration,               // ⏱️ FIX UTAMA
        status: "ready",
        createdAt: new Date(),
      });

      return res.status(200).json({
        success: true,
        transcriptId: result.insertedId,
        duration,
      });
    } catch (e) {
      console.error("UPLOAD ERROR:", e);
      return res.status(500).json({ error: "Internal server error" });
    }
  });
}

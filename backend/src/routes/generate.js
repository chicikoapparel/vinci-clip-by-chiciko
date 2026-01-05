// const express = require("express");
// const router = express.Router();
// const path = require("path");
// const fs = require("fs");
// const { spawn } = require("child_process");

// const Transcript = require("../models/Transcript");

// const FFMPEG = "ffmpeg";
// const PYTHON = "python";

// // ⚠️ Python tools tetap di frontend
// const FACE_DETECT = path.join(
//   process.cwd(),
//   "..",
//   "frontend",
//   "tools",
//   "vision",
//   "face_detect.py"
// );

// const AUTO_CROP = path.join(
//   process.cwd(),
//   "..",
//   "frontend",
//   "tools",
//   "vision",
//   "auto_crop.py"
// );

// // ===============================
// // POST /generate
// // ===============================
// router.post("/", async (req, res) => {
//   try {
//     const { transcriptId, segments, mode } = req.body;

//     if (mode !== "ai_framing") {
//       return res.status(400).json({ error: "Invalid mode" });
//     }

//     if (!transcriptId || !Array.isArray(segments) || segments.length === 0) {
//       return res.status(400).json({ error: "Invalid payload" });
//     }

//     const transcript = await Transcript.findById(transcriptId);
//     if (!transcript) {
//       return res.status(404).json({ error: "Transcript not found" });
//     }

//     if (!transcript.videoUrl) {
//       throw new Error("Transcript.videoUrl not found");
//     }

//     // 🎯 VIDEO ASLI (PATH ABSOLUT, BENAR)
//     const inputVideo = path.join(
//       process.cwd(),
//       transcript.videoUrl.replace(/^\/+/, "")
//     );

//     if (!fs.existsSync(inputVideo)) {
//       throw new Error("Input video file not found: " + inputVideo);
//     }

//     // 🛡️ VALIDATE PYTHON TOOLS
//     if (!fs.existsSync(FACE_DETECT)) {
//       throw new Error("face_detect.py not found: " + FACE_DETECT);
//     }
//     if (!fs.existsSync(AUTO_CROP)) {
//       throw new Error("auto_crop.py not found: " + AUTO_CROP);
//     }

//     // 📁 OUTPUT DIR
//     const outputDir = path.join(
//       process.cwd(),
//       "uploads",
//       "clips",
//       transcriptId
//     );
//     fs.mkdirSync(outputDir, { recursive: true });

//     const results = [];

//     // ===============================
//     // PROCESS PER SEGMENT
//     // ===============================
//     for (let i = 0; i < segments.length; i++) {
//       const seg = segments[i];

//       const start =
//         seg.start ??
//         seg.startTime ??
//         seg.from ??
//         null;

//       const end =
//         seg.end ??
//         seg.endTime ??
//         seg.to ??
//         null;

//       if (
//         typeof start !== "number" ||
//         typeof end !== "number" ||
//         end <= start
//       ) {
//         throw new Error(`Invalid segment at index ${i}`);
//       }

//       const workDir = path.join(outputDir, `seg_${i}`);
//       fs.mkdirSync(workDir, { recursive: true });

//       const cutVideo = path.join(workDir, "cut.mp4");
//       const facesJson = path.join(workDir, "faces.json");
//       const finalVideo = path.join(workDir, "final.mp4");

//       // ===============================
//       // 1️⃣ FFMPEG CUT (FAST + SYNC)
//       // ===============================
//       await runProcess(
//         FFMPEG,
//         [
//           "-y",
//           "-ss",
//           String(start),
//           "-i",
//           inputVideo,
//           "-t",
//           String(end - start),
//           "-map",
//           "0:v:0",
//           "-c:v",
//           "libx264",
//           "-preset",
//           "veryfast",
//           "-pix_fmt",
//           "yuv420p",
//           "-map",
//           "0:a?",
//           "-c:a",
//           "copy",
//           cutVideo,
//         ],
//         "FFmpeg cut failed"
//       );

//       // ===============================
//       // 2️⃣ FACE DETECT
//       // ===============================
//       await runProcess(
//         PYTHON,
//         [FACE_DETECT, cutVideo, facesJson],
//         "face_detect.py failed"
//       );

//       if (!fs.existsSync(facesJson)) {
//         throw new Error("faces.json was not generated");
//       }

//       // ===============================
//       // 3️⃣ AUTO CROP AI
//       // ===============================
//       await runProcess(
//         PYTHON,
//         [AUTO_CROP, cutVideo, facesJson, finalVideo],
//         "auto_crop.py failed"
//       );

//       results.push({
//         index: i,
//         start,
//         end,
//         videoUrl: `/uploads/clips/${transcriptId}/seg_${i}/final.mp4`,
//       });
//     }

//     return res.json({ clips: results });
//   } catch (err) {
//     console.error("GENERATE BACKEND ERROR:", err);
//     return res.status(500).json({ error: err.message });
//   }
// });

// // ===============================
// // UTIL: run process (SAFE)
// // ===============================
// function runProcess(cmd, args, errorMessage) {
//   return new Promise((resolve, reject) => {
//     const p = spawn(cmd, args, {
//       stdio: "inherit",
//       cwd: process.cwd(),
//     });

//     p.on("error", reject);
//     p.on("close", (code) =>
//       code === 0
//         ? resolve()
//         : reject(new Error(errorMessage))
//     );
//   });
// }

// module.exports = router;

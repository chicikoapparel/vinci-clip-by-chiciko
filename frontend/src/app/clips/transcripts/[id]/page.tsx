"use client";

import { useEffect, useState } from "react";
import axios from "axios";

type Preset = 15 | 30 | 60 | null;

export default function TranscriptDetailPage() {
  const [data, setData] = useState<any>(null);
  const [clips, setClips] = useState<any[]>([]);
  const [videoDuration, setVideoDuration] = useState<number>(0);

  const [generating, setGenerating] = useState(false);
  const [batchPreset, setBatchPreset] = useState<Preset>(null);

  /* =========================
     LOAD DATA
  ==========================*/
  useEffect(() => {
    const id = window.location.pathname.split("/").pop();
    if (!id) return;

    loadTranscript(id);
    loadClips(id);
  }, []);

  const loadTranscript = async (id: string) => {
    const res = await axios.get(`/api/clips/transcripts/${id}`);
    setData(res.data);

    // ✅ DURASI VIDEO (detik)
    if (typeof res.data.duration === "number") {
      setVideoDuration(res.data.duration);
    }
  };

  const loadClips = async (id: string) => {
    const res = await axios.get(`/api/clips/by-transcript/${id}`);
    setClips(res.data);
  };

  /* =========================
     BATCH GENERATE (FIXED)
  ==========================*/
  const handleGenerate = async () => {
    if (!data?._id) return;

    const transcriptId =
      typeof data._id === "string" ? data._id : data._id?.$oid;

    if (!transcriptId) {
      alert("Invalid transcriptId");
      return;
    }

    if (!batchPreset) {
      alert("Pilih Batch Preset (15s / 30s / 60s)");
      return;
    }

    if (!videoDuration || videoDuration <= 0) {
      alert("Durasi video tidak valid");
      return;
    }

    try {
      setGenerating(true);

      const segments: { startTime: number; endTime: number }[] = [];
      let cursor = 0;

      // ✅ FIX UTAMA: TIDAK ADA CLIP YANG HILANG
      while (cursor < videoDuration) {
        const end = Math.min(cursor + batchPreset, videoDuration);

        segments.push({
          startTime: cursor,
          endTime: end,
        });

        cursor = end;
      }

      console.log("SEGMENTS GENERATED:", segments);

   await axios.post(
  "/api/clips/generate",
  {
    transcriptId,
    exportPlatform: "tiktok",
    segments,
  },
  {
    timeout: 0, // ⏱️ PENTING: tunggu proses lama
  }
);


      await loadClips(transcriptId);
      alert(`Batch generate selesai (${segments.length} clip)`);
    } catch (err) {
      console.error("BATCH GENERATE ERROR:", err);
      alert("Generate clip gagal");
    } finally {
      setGenerating(false);
    }
  };

  if (!data) return <div style={{ padding: 20 }}>Loading…</div>;

  /* =========================
     UI
  ==========================*/
  return (
    <main style={{ padding: 24, maxWidth: 720 }}>
      <h1>{data.originalFilename}</h1>
      <p>Status: {data.status}</p>
      <p>
        Durasi video: {Math.floor(videoDuration / 60)}:
        {(videoDuration % 60).toString().padStart(2, "0")}
      </p>

      <h2 style={{ marginTop: 24 }}>Batch Generate</h2>

      <div style={{ marginTop: 8 }}>
        {[15, 30, 60].map((v) => (
          <button
            key={v}
            onClick={() => setBatchPreset(v as Preset)}
            style={{
              marginRight: 8,
              padding: "6px 10px",
              background: batchPreset === v ? "#1976d2" : "#eee",
              color: batchPreset === v ? "#fff" : "#000",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            {v}s
          </button>
        ))}
      </div>

      <button
        onClick={handleGenerate}
        disabled={generating}
        style={{
          marginTop: 16,
          padding: "8px 14px",
          background: "#1976d2",
          color: "white",
          border: "none",
          borderRadius: 4,
          cursor: "pointer",
        }}
      >
        {generating
          ? "Generating…"
          : batchPreset
          ? `Generate ${batchPreset}s clips`
          : "Pilih preset"}
      </button>

      <h2 style={{ marginTop: 32 }}>Clips ({clips.length})</h2>

      {clips.length === 0 && <p>Belum ada clip</p>}

      {clips.map((clip) => {
        const clipId =
          typeof clip._id === "string" ? clip._id : clip._id?.$oid;

        return (
          <div
            key={clipId}
            style={{
              marginTop: 16,
              padding: 12,
              border: "1px solid #ccc",
            }}
          >
            <p>
              ⏱ {clip.startTime}s – {clip.endTime}s
            </p>

            <video
              src={clip.videoUrl}
              controls
              style={{ width: "100%", maxWidth: 480 }}
            />

            <a
              href={clip.videoUrl}
              download
              style={{
                display: "inline-block",
                marginTop: 6,
                background: "#1976d2",
                color: "white",
                padding: "6px 12px",
                borderRadius: 4,
                textDecoration: "none",
              }}
            >
              Download
            </a>
          </div>
        );
      })}
    </main>
  );
}

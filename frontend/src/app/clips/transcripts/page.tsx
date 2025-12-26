"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import Link from "next/link";

export default function ClipsPage() {
  const [clips, setClips] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClips();
  }, []);

  const fetchClips = async () => {
    try {
      const res = await axios.get("/api/clips/transcripts");
      setClips(res.data);
    } catch (err) {
      console.error("FETCH CLIPS ERROR:", err);
    } finally {
      setLoading(false);
    }
  };

  // ✅ DELETE CLIP (AMAN)
  const handleDeleteClip = async (clip: any) => {
    try {
      const clipId =
        typeof clip._id === "string" ? clip._id : clip._id?.$oid;

      if (!clipId) {
        alert("Invalid clip id");
        return;
      }

      if (!confirm("Hapus clip ini?")) return;

      await axios.delete(`/api/clips/${clipId}`);

      // update UI tanpa reload
      setClips((prev) =>
        prev.filter((c) => {
          const id =
            typeof c._id === "string" ? c._id : c._id?.$oid;
          return id !== clipId;
        })
      );
    } catch (err) {
      console.error("DELETE CLIP ERROR:", err);
      alert("Gagal menghapus clip");
    }
  };

  if (loading) {
    return <div style={{ padding: 20 }}>Loading...</div>;
  }

  return (
    <main style={{ padding: 24 }}>
      <h1>All Clips</h1>

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

            <div style={{ marginTop: 8 }}>
              <button
                onClick={() => handleDeleteClip(clip)}
                style={{
                  background: "#e53935",
                  color: "white",
                  border: "none",
                  padding: "6px 12px",
                  cursor: "pointer",
                }}
              >
                Delete Clip
              </button>
            </div>

            {clip.transcriptId && (
              <p style={{ marginTop: 8 }}>
                <Link
                  href={`/clips/transcripts/${clip.transcriptId}`}
                >
                  Lihat Transcript
                </Link>
              </p>
            )}
          </div>
        );
      })}
    </main>
  );
}

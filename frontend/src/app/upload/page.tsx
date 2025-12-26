"use client";

import React, { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

import {
  UploadCloud,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2,
  Trash2,
} from "lucide-react";

/* ======================
   TYPES
====================== */
interface Transcript {
  _id: string;
  originalFilename: string;
  createdAt: string;
  status?: "uploading" | "completed" | "failed";
  duration?: number; // ⏱️ dari backend
}

/* ======================
   COMPONENT
====================== */
export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState("");

  const [recentTranscripts, setRecentTranscripts] = useState<Transcript[]>([]);
  const [loading, setLoading] = useState(true);

  /* ======================
     LOAD RECENT TRANSCRIPTS
  ====================== */
  useEffect(() => {
    fetchRecent();
  }, []);

  const fetchRecent = async () => {
    try {
      const res = await axios.get("/api/clips/transcripts");
      setRecentTranscripts(res.data || []);
    } catch (err) {
      console.error("FETCH TRANSCRIPTS ERROR:", err);
    } finally {
      setLoading(false);
    }
  };

  /* ======================
     UPLOAD HANDLER
  ====================== */
  const handleUpload = async (file: File) => {
    if (file.size > 2 * 1024 * 1024 * 1024) {
      alert("Ukuran file maksimal 2GB");
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setMessage("Uploading video...");

    const formData = new FormData();
    formData.append("video", file);

    try {
      await axios.post("/api/upload", formData, {
        onUploadProgress: (e) => {
          if (!e.total) return;
          const percent = Math.round((e.loaded * 100) / e.total);
          setUploadProgress(percent);
        },
      });

      setMessage("Upload selesai, memproses video...");
      await fetchRecent();
    } catch (err) {
      console.error("UPLOAD ERROR:", err);
      alert("Upload gagal");
    } finally {
      setUploading(false);
    }
  };

  /* ======================
     FILE INPUT
  ====================== */
  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
  };

  /* ======================
     DELETE TRANSCRIPT
  ====================== */
  const handleDelete = async (id: string) => {
    if (!confirm("Hapus video ini?")) return;
    try {
      await axios.delete(`/api/clips/transcripts/${id}`);
      setRecentTranscripts((prev) => prev.filter((t) => t._id !== id));
    } catch (err) {
      console.error("DELETE ERROR:", err);
      alert("Gagal menghapus video");
    }
  };

  /* ======================
     UI HELPERS
  ====================== */
  const statusBadge = (status?: string) => {
    if (!status || status === "completed") {
      return <Badge>Ready</Badge>;
    }
    if (status === "uploading") {
      return <Badge variant="secondary">Uploading</Badge>;
    }
    if (status === "failed") {
      return <Badge variant="destructive">Failed</Badge>;
    }
    return <Badge variant="secondary">Processing</Badge>;
  };

  const statusIcon = (status?: string) => {
    if (!status || status === "completed") {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    }
    if (status === "failed") {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
  };

  /* ======================
     RENDER
  ====================== */
  return (
    <main className="min-h-screen p-8 bg-background">
      <div className="max-w-5xl mx-auto">

        {/* ===== UPLOAD CARD ===== */}
        <Card className="mb-10">
          <CardHeader>
            <CardTitle>Upload Video</CardTitle>
            <CardDescription>
              Upload video (max 2GB). Durasi akan dihitung otomatis.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div
              className="border-2 border-dashed rounded-lg p-10 text-center cursor-pointer"
              onClick={() => document.getElementById("fileInput")?.click()}
            >
              <UploadCloud className="mx-auto mb-4" />
              <p>Klik untuk upload video</p>
              <input
                id="fileInput"
                type="file"
                accept="video/*"
                className="hidden"
                onChange={onFileChange}
              />
            </div>

            {uploading && (
              <div className="mt-4">
                <Progress value={uploadProgress} />
                <p className="text-sm mt-2">{message}</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* ===== RECENT ===== */}
        <h2 className="text-2xl font-bold mb-4">Recent Videos</h2>

        {loading ? (
          <div className="flex justify-center py-10">
            <Loader2 className="animate-spin" />
          </div>
        ) : recentTranscripts.length === 0 ? (
          <p>Belum ada video</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recentTranscripts.map((t) => (
              <Card key={t._id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-sm truncate">
                      {t.originalFilename}
                    </CardTitle>
                    <Trash2
                      className="h-4 w-4 text-red-500 cursor-pointer"
                      onClick={() => handleDelete(t._id)}
                    />
                  </div>
                </CardHeader>

                <CardContent className="space-y-2">
                  <div className="flex justify-between items-center">
                    {statusBadge(t.status)}
                    {statusIcon(t.status)}
                  </div>

                  {typeof t.duration === "number" && (
                    <div className="flex items-center text-sm text-muted-foreground">
                      <Clock className="h-4 w-4 mr-1" />
                      {Math.floor(t.duration / 60)}:
                      {String(Math.floor(t.duration % 60)).padStart(2, "0")}
                    </div>
                  )}

                  <Button asChild className="w-full">
                    <Link href={`/clips/transcripts/${t._id}`}>
                      View Details
                    </Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

// Jenis platform yang didukung
export type ExportPlatform =
  | "tiktok"
  | "instagram_reels"
  | "youtube_shorts";

// Struktur preset
export interface ExportPreset {
  label: string;
  maxDuration: number; // detik
  width: number;
  height: number;
  fps: number;
  videoBitrate: string;
  audioBitrate: string;
  subtitle: boolean;
}
// PRESET UTAMA (SOURCE OF TRUTH)
export const EXPORT_PRESETS: Record<ExportPlatform, ExportPreset> = {
  tiktok: {
    label: "TikTok",
    maxDuration: 60,
    width: 1080,
    height: 1920,
    fps: 30,
    videoBitrate: "6M",
    audioBitrate: "128k",
    subtitle: true,
  },

  instagram_reels: {
    label: "Instagram Reels",
    maxDuration: 90,
    width: 1080,
    height: 1920,
    fps: 30,
    videoBitrate: "6M",
    audioBitrate: "128k",
    subtitle: true,
  },

  youtube_shorts: {
    label: "YouTube Shorts",
    maxDuration: 60,
    width: 1080,
    height: 1920,
    fps: 60,
    videoBitrate: "8M",
    audioBitrate: "160k",
    subtitle: false,
  },
};

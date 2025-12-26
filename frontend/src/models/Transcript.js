import mongoose from "mongoose";

const TranscriptSchema = new mongoose.Schema(
  {
    originalFilename: String,
    status: {
      type: String,
      enum: ["uploading", "converting", "transcribing", "completed", "failed"],
      default: "uploading",
    },
    duration: Number,
    transcriptText: String,
  },
  { timestamps: true }
);

export default mongoose.models.Transcript ||
  mongoose.model("Transcript", TranscriptSchema);
